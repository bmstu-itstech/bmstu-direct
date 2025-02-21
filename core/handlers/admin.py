import logging

from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from core import domain, texts

from common.repository import dp
from core.filters.role import AdminFilter
from services.db.storage import Storage, TicketNotFoundException


DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(AdminFilter(), Command("ban"), state="*")
async def ban(message: Message, store: Storage):
    ticket_id_from_msg = message.get_args() or ""
    if not ticket_id_from_msg.isdigit():
        return await message.answer("Значение id тикета должно быть числом")
    ticket_id = int(ticket_id_from_msg)
    try:
        ticket = await store.ticket(ticket_id)
    except TicketNotFoundException:
        return await message.answer(texts.errors.no_ticket)
    await store.save_banned_user(domain.BannedUser(chat_id=ticket.owner_chat_id))
    await message.bot.send_message(
        chat_id=ticket.owner_chat_id,
        text=texts.ticket.banned,
    )
    await message.answer("Пользователь успешно заблокирован")
