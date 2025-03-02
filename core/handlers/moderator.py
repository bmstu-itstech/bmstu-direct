import logging

from aiogram.dispatcher.filters import ForwardedMessageFilter, IsReplyFilter
from aiogram.types import Message, ParseMode, ContentType, InputMediaPhoto

from core import domain, texts

from common.repository import dp, bot
from core.filters.role import ModeratorFilter
from services.db.storage import Storage, MessageNotFoundException
from config import config


DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(ModeratorFilter(), ForwardedMessageFilter(is_forwarded=True))
async def handle_ticket_published(message: Message, store: Storage):
    ticket_id = extract_ticket_id(message.text)
    await store.update_ticket(ticket_id, group_message_id=message.message_id)


@dp.message_handler(ModeratorFilter(), IsReplyFilter(is_reply=True),
                    content_types=[ContentType.PHOTO,  ContentType.TEXT])
async def handle_moderator_answer(message: Message, store: Storage, album: list[Message] | None = None):
    _id = message.__dict__["_values"]["message_thread_id"]
    ticket_id = await store.message_ticket_id(_id)
    await send_moderator_answer(album, message, store, ticket_id, message.text)


async def send_moderator_answer(album, message: Message, store: Storage, ticket_id: int, answer: str):
    ticket = await store.ticket(ticket_id)
    reply_to_id = None
    try:
        replied_message = await store.message_id(message.reply_to_message.message_id)
        reply_to_id = replied_message.owner_message_id
    except MessageNotFoundException:
        logger.info(f"Message {reply_to_id} to reply not found")

    if message.content_type == ContentType.PHOTO and message.media_group_id is None:  # если одиночное фото
        file_id = message.photo[-1].file_id
        file_caption = message.caption
        sent = await bot.send_photo(ticket.owner_chat_id, photo=file_id, reply_to_message_id=reply_to_id,
                                                parse_mode=ParseMode.HTML, caption=file_caption)
    if message.content_type  == ContentType.PHOTO and message.media_group_id: # если медиа групп
        if album:
            media = []
            for obj in album:
                if obj.photo:
                    file_id = obj.photo[-1].file_id
                    if obj == album[0]:
                        media.append(InputMediaPhoto(media=file_id, caption=message.caption))
                    else:
                        media.append(InputMediaPhoto(media=file_id))
            sent = await bot.send_media_group(chat_id=ticket.owner_chat_id, media=media)
    if message.content_type == ContentType.TEXT: # если текстовое сообщение
        sent = await bot.send_message(
            ticket.owner_chat_id,
            texts.ticket.moderator_answer(ticket.id, answer),
            reply_to_message_id=reply_to_id,
            parse_mode=ParseMode.HTML,
        )

    if ticket.status != domain.Status.IN_PROGRESS:
        ticket = await store.update_ticket(ticket.id, status=domain.Status.IN_PROGRESS)
        await update_ticket(ticket)

    await store.save_message(
        domain.Message(
            chat_id=message.chat.id,
            message_id=message.message_id,
            owner_message_id=sent.message_id,
            reply_to_message_id=sent.reply_to_message.message_id if sent.reply_to_message else None,
            ticket_id=ticket_id,
        )
    )


async def update_ticket(ticket: domain.TicketRecord):
    await bot.edit_message_text(
        texts.ticket.ticket_channel(ticket),
        chat_id=config.channel_chat_id,
        message_id=ticket.channel_message_id,
        parse_mode=ParseMode.HTML,
    )


def extract_ticket_id(s: str) -> int:
    i = s.find(" ")
    j = s.find("\n", i)
    if j < 0:
        j = len(s)
    return int(s[i+1:j])
