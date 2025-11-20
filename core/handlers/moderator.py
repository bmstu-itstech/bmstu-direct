import logging
import re

from aiogram.dispatcher.filters import ForwardedMessageFilter, IsReplyFilter
from aiogram.types import Message, ParseMode, ContentType, InputMediaPhoto, InputMediaDocument, CallbackQuery

from core import domain, texts

from common.repository import dp, bot
from core.filters.role import ModeratorFilter
from services.db.storage import Storage, MessageNotFoundException, TicketNotFoundException
from config import config

from core.domain.status import Status
from core.handlers import keyboards
from core.callbacks import StatusCallback

DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(ModeratorFilter(), ForwardedMessageFilter(is_forwarded=True))
async def handle_ticket_published(message: Message, store: Storage):
    ticket_id = extract_ticket_id(message.text)
    thread_id = message.message_thread_id or message.message_id
    await store.update_ticket(ticket_id, group_message_id=thread_id)


@dp.message_handler(ModeratorFilter(), IsReplyFilter(is_reply=True),
                    content_types=[ContentType.PHOTO,  ContentType.TEXT, ContentType.DOCUMENT])
async def handle_moderator_answer(message: Message, store: Storage, album: list[Message] | None = None):
    thread_id = message.message_thread_id or message.message_id
    try:
        ticket_id = await store.message_ticket_id(thread_id)
    except TicketNotFoundException:
        if message.reply_to_message:
            try:
                replied_message = await store.message_id(message.reply_to_message.message_id)
                ticket_id = replied_message.ticket_id
            except MessageNotFoundException:
                logger.info("Ticket not found for moderator answer and reply mapping failed")
                return
        else:
            logger.info("Ticket not found for moderator answer without reply metadata")
            return
    await send_moderator_answer(message, store, album, ticket_id, message.html_text)


async def send_moderator_answer(message: Message, store: Storage, album: list[Message] | None, ticket_id: int, answer: str):
    ticket = await store.ticket(ticket_id)
    reply_to_id = None
    album_messages: list[Message] | None = None
    try:
        replied_message = await store.message_id(message.reply_to_message.message_id)
        reply_to_id = replied_message.owner_message_id
    except MessageNotFoundException:
        logger.info(f"Message {reply_to_id} to reply not found")

    sent: list[Message]
    # Если документ
    if  message.content_type == ContentType.DOCUMENT:
        # Если одиночный документ
        if message.media_group_id  is None:
            file_id = message.document.file_id
            sent = [await bot.send_document(ticket.owner_chat_id,
                                            document=file_id,
                                            reply_to_message_id=reply_to_id,
                                            parse_mode=ParseMode.HTML,
                                            caption=texts.ticket.moderator_answer(ticket_id, message.html_caption))]
        else:
            album_messages = album or [message]
            media = []
            for idx, obj in enumerate(album_messages):
                media.append(
                    InputMediaDocument(
                        media=obj.document.file_id,
                        caption=texts.ticket.moderator_answer(ticket.id, message.html_caption) if idx == 0 else None,
                        parse_mode=ParseMode.HTML if idx == 0 else None,
                    )
                )
            sent = await bot.send_media_group(chat_id=ticket.owner_chat_id, media=media, reply_to_message_id=reply_to_id)
    # Если фото
    elif message.content_type == ContentType.PHOTO:
        # если одиночное фото
        if message.media_group_id is None:
            file_id = message.photo[-1].file_id
            sent = [await bot.send_photo(ticket.owner_chat_id, photo=file_id,
                                                    reply_to_message_id=reply_to_id,
                                                    parse_mode=ParseMode.HTML,
                                                    caption=texts.ticket.moderator_answer(ticket.id, message.html_caption))]
        else:
            album_messages = album or [message]
            media = [InputMediaPhoto(media=album_messages[0].photo[-1].file_id,
                                                 caption=texts.ticket.moderator_answer(ticket.id, message.html_caption),
                                                 parse_mode=ParseMode.HTML)]
            for obj in album_messages[1:]:
                file_id = obj.photo[-1].file_id
                media.append(InputMediaPhoto(media=file_id))
            sent = await bot.send_media_group(chat_id=ticket.owner_chat_id, media=media, reply_to_message_id=reply_to_id)
    # Если текстовое сообщение
    elif message.content_type == ContentType.TEXT:
        sent = [await bot.send_message(
            ticket.owner_chat_id,
            texts.ticket.moderator_answer(ticket.id, answer),
            reply_to_message_id=reply_to_id,
            parse_mode=ParseMode.HTML,
        )]

    await ticket.change_status(Status.IN_PROGRESS) # Обновление статуса
    ticket = await store.update_ticket(ticket.id, status=ticket.status)
    await update_ticket_message(ticket)

    if message.media_group_id and len(sent) > 1:
        album_messages = album_messages or album or [message]
        for reply_msg, owner_msg in zip(sent, album_messages):
            await store.save_message(
                domain.Message(
                    chat_id=message.chat.id,
                    message_id=owner_msg.message_id,
                    owner_message_id=reply_msg.message_id,
                    reply_to_message_id=reply_msg.reply_to_message.message_id if reply_msg.reply_to_message else reply_to_id,
                    ticket_id=ticket_id,
                )
            )
    else:
        await store.save_message(
            domain.Message(
                chat_id=message.chat.id,
                message_id=message.message_id,
                owner_message_id=sent[0].message_id,
                reply_to_message_id=sent[0].reply_to_message.message_id if sent[0].reply_to_message else reply_to_id,
                ticket_id=ticket_id,
            )
        )


async def update_ticket_message(ticket: domain.TicketRecord):
    await bot.edit_message_text(
        texts.ticket.ticket_meta_message_channel(ticket),
        chat_id=config.channel_chat_id,
        message_id=ticket.channel_meta_message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.keyboard_by_status(ticket.status, ticket.id)
    )


def extract_ticket_id(s: str) -> int:
    match = re.search(r"<code>(\d+)</code>", s)
    if match:
        return int(match.group(1))

    match = re.search(r"\b(\d{3,})\b", s)
    if match:
        return int(match.group(1))

    raise ValueError("Ticket id not found in message")


@dp.callback_query_handler(StatusCallback.filter())
async def status_callback_handler(query: CallbackQuery, callback_data: dict, store: Storage, album: list[Message] | None = None):
        
    ticket = await store.ticket(int(callback_data["ticket_id"]))
    to_status = callback_data['status']

    logger.info(f"Handeled callback status on ticket_id {ticket.id} from {ticket.status} to {to_status} ")

    await ticket.change_status(Status(to_status))

    ticket = await store.update_ticket(ticket.id, status=ticket.status)

    await update_ticket_message(ticket)
