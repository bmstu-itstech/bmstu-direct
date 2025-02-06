import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter, ForwardedMessageFilter, IsReplyFilter
from aiogram.types import Message, ParseMode

from core import domain, texts

from common.repository import dp, bot
from core.domain import Status
from services.db.storage import Storage, MessageNotFound
from config import config


DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(IDFilter(chat_id=config.comment_chat_id), ForwardedMessageFilter(is_forwarded=True))
async def handle_ticket_published(message: Message, store: Storage):
    ticket_id = extract_ticket_id(message.text)
    await store.update_ticket(ticket_id, group_message_id=message.message_id)


@dp.message_handler(IDFilter(chat_id=config.comment_chat_id), IsReplyFilter(is_reply=True))
async def handle_moderator_answer(message: Message, store: Storage):
    _id = message.__dict__["_values"]["message_thread_id"]
    ticket_id = await store.message_ticket_id(_id)
    await send_moderator_answer(message, store, ticket_id, message.text)


async def send_moderator_answer(message: Message, store: Storage, ticket_id: int, answer: str):
    ticket = await store.ticket(ticket_id)
    reply_to_id = None
    try:
        replied_message = await store.message_id(message.reply_to_message.message_id)
        reply_to_id = replied_message.owner_message_id
    except MessageNotFound:
        logger.info(f"Message {reply_to_id} to reply not found")

    sent = await bot.send_message(
        ticket.owner_chat_id,
        texts.ticket.moderator_answer(ticket.id, answer),
        reply_to_message_id=reply_to_id,
        parse_mode=ParseMode.HTML,
    )

    if ticket.status != Status.IN_PROGRESS:
        ticket = await store.update_ticket(ticket.id, status=Status.IN_PROGRESS)
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
