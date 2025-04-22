import logging

from aiogram.dispatcher.filters import ForwardedMessageFilter, IsReplyFilter
from aiogram.types import Message, ParseMode, ContentType, InputMediaPhoto, InputMediaDocument, CallbackQuery

from core import domain, texts

from common.repository import dp, bot
from core.filters.role import ModeratorFilter
from services.db.storage import Storage, MessageNotFoundException
from config import config

from core.domain.status import Status
from core.handlers import keyboards
from core.callbacks import StatusCallback

DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(ModeratorFilter(), ForwardedMessageFilter(is_forwarded=True))
async def handle_ticket_published(message: Message, store: Storage):
    ticket_id = extract_ticket_id(message.text)
    if ticket_id:
        await store.update_ticket(ticket_id, group_message_id=message.message_id)


@dp.message_handler(ModeratorFilter(), IsReplyFilter(is_reply=True),
                    content_types=[ContentType.PHOTO,  ContentType.TEXT, ContentType.DOCUMENT])
async def handle_moderator_answer(message: Message, store: Storage, album: list[Message] | None = None):
    _id = message.__dict__["_values"]["message_thread_id"]
    ticket_id = await store.message_ticket_id(_id)
    await send_moderator_answer(message, store, album, ticket_id, message.text)


async def send_moderator_answer(message: Message, store: Storage, album: list[Message] | None, ticket_id: int, answer: str):
    ticket = await store.ticket(ticket_id)
    reply_to_id = None
    try:
        replied_message = await store.message_id(message.reply_to_message.message_id)
        reply_to_id = replied_message.owner_message_id
    except MessageNotFoundException:
        logger.info(f"Message {reply_to_id} to reply not found")

    # Если документ
    if  message.content_type == ContentType.DOCUMENT:
        # Если одиночный документ
        if message.media_group_id  is None:
            file_id = message.document.file_id
            sent = [await bot.send_document(ticket.owner_chat_id,
                                            document=file_id,
                                            reply_to_message_id=reply_to_id,
                                            parse_mode=ParseMode.HTML,
                                            caption=texts.ticket.moderator_answer(ticket_id, message.caption))]
        else:
            if album:
                media = [InputMediaDocument(media=album[-1].document.file_id,
                                            # caption=texts.ticket.moderator_answer(ticket.id, message.caption),
                                            parse_mode=ParseMode.HTML)]
                album.reverse()
                for obj in album[1:]:
                    file_id = obj.document.file_id
                    media.append(InputMediaDocument(media=file_id))
                media.reverse()
                sent = await bot.send_media_group(chat_id=ticket.owner_chat_id, media=media, reply_to_message_id=reply_to_id)
    # Если фото
    elif message.content_type == ContentType.PHOTO:
        # если одиночное фото
        if message.media_group_id is None:
            file_id = message.photo[-1].file_id
            sent = [await bot.send_photo(ticket.owner_chat_id, photo=file_id,
                                                    reply_to_message_id=reply_to_id,
                                                    parse_mode=ParseMode.HTML,
                                                    caption=texts.ticket.moderator_answer(ticket.id, message.caption))]
        else:
            if album:
                media = [InputMediaPhoto(media=album[0].photo[-1].file_id,
                                                     caption=texts.ticket.moderator_answer(ticket.id, message.caption),
                                                     parse_mode=ParseMode.HTML)]
                for obj in album[1:]:
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

    await store.save_message(
        domain.Message(
            chat_id=message.chat.id,
            message_id=message.message_id,
            owner_message_id=sent[0].message_id if not message.media_group_id else sent[0].message_id,
            reply_to_message_id=sent[0].reply_to_message.message_id if sent[0].reply_to_message else None,
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
    if s.startswith("Обращение "):
        i = s.find(" ")
        j = s.find("\n", i)
        if j < 0:
            j = len(s)
        return int(s[i+1:j])
    return 0


@dp.callback_query_handler(StatusCallback.filter())
async def status_callback_handler(query: CallbackQuery, callback_data: dict, store: Storage, album: list[Message] | None = None):
        
    ticket = await store.ticket(int(callback_data["ticket_id"]))
    to_status = callback_data['status']

    logger.info(f"Handeled callback status on ticket_id {ticket.id} from {ticket.status} to {to_status} ")

    await ticket.change_status(to_status)

    ticket = await store.update_ticket(ticket.id, status=ticket.status)

    await update_ticket_message(ticket)
