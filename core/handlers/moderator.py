import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter, ForwardedMessageFilter, IsReplyFilter
from aiogram.types import Message

from core import domain

from common.repository import dp, bot
from core.domain import MessageID
from services.db.storage import Storage
from config import config


DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(IDFilter(chat_id=config.comment_chat_id), ForwardedMessageFilter(is_forwarded=True))
async def handle_ticket_published(message: Message, state: FSMContext, repos: Storage):
    ticket_id = extract_ticket_id(message.text)
    ticket = await repos.ticket(ticket_id)
    await repos.save_message_pair(domain.MessagePair(
        # Сообщение заявителя.
        source_id=domain.MessageID(
            chat_id=ticket.owner_chat_id,
            message_id=ticket.source_message_id,
        ),
        # Дублирование в чат к каналу.
        copy_id=domain.MessageID(
            chat_id=message.chat.id,
            message_id=message.message_id,
        ),
        ticket_id=ticket_id,
    ))


@dp.message_handler(IDFilter(chat_id=config.comment_chat_id), IsReplyFilter(is_reply=True))
async def handle_moderator_answer(message: Message, state: FSMContext, repos: Storage):
    _id = domain.MessageID(
        chat_id=message.chat.id,
        message_id=message.reply_to_message.message_id,
    )
    ticket_id = await repos.message_ticket_id(_id)
    async with state.proxy() as data:
        data[DATA_SOURCE_ID_KEY] = _id
    await send_moderator_answer(message, state, repos, ticket_id, message.text)


async def send_moderator_answer(message: Message, state: FSMContext, repos: Storage, ticket_id: int, answer: str):
    ticket = await repos.ticket(ticket_id)
    sent = await bot.send_message(ticket.owner_chat_id,
        f"Ответ: {answer}"
    )
    async with state.proxy() as data:
        source_id = data[DATA_SOURCE_ID_KEY]
    copy_id = MessageID(
        chat_id=sent.chat.id,
        message_id=sent.message_id,
    )
    await repos.save_message_pair(domain.MessagePair(
        source_id=source_id,
        copy_id=copy_id,
        ticket_id=ticket_id,
    ))


@dp.message_handler(IsReplyFilter(is_reply=True), state="*")
async def handle_student_answer(message: Message, state: FSMContext, repos: Storage):
    _id = domain.MessageID(
        chat_id=message.chat.id,
        message_id=message.reply_to_message.message_id,
    )
    ticket_id = await repos.message_ticket_id(_id)
    async with state.proxy() as data:
        data[DATA_SOURCE_ID_KEY] = _id
    await send_student_answer(message, state, repos, ticket_id, message.text)


async def send_student_answer(message: Message, state: FSMContext, repos: Storage, ticket_id: int, answer: str):
    async with state.proxy() as data:
        _id = data[DATA_SOURCE_ID_KEY]
    paired_id = await repos.paired_message_id(_id)
    sent = await bot.send_message(
        config.comment_chat_id,
        answer,
        reply_to_message_id=paired_id.message_id,
    )
    await repos.save_message_pair(domain.MessagePair(
        source_id=MessageID(
            chat_id=message.chat.id,
            message_id=message.message_id,
        ),
        copy_id=MessageID(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
        ),
        ticket_id=ticket_id,
    ))


def extract_ticket_id(s: str) -> int:
    i = s.find("#")
    j = s.find("\n", i)
    if j < 0:
        j = len(s)
    return int(s[i+1:j])
