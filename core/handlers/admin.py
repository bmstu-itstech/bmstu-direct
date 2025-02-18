import logging

from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from core import domain, texts

from common.repository import dp
from core.filters.role import AdminFilter
from services.db.storage import Storage, TicketNotFoundException


DATA_SOURCE_ID_KEY = "source_id"

logger = logging.getLogger(__name__)


@dp.message_handler(AdminFilter(), Command("ban"))
async def admin(message: Message, store: Storage):
    ticket_id_from_msg = message.get_args() or ""
    if not ticket_id_from_msg.isdigit():
        return await message.answer("Значение id тикета должно быть числом")
    ticket_id = int(message.text.split()[-1])
    try:
        ticket = await store.ticket(ticket_id)
    except TicketNotFoundException:
        return await message.answer(texts.errors.no_ticket)
    await store.update_user(ticket.owner_chat_id, role=domain.Role.BANNED)
    await message.bot.send_message(
        chat_id=ticket.owner_chat_id,
        text=texts.ticket.banned,
    )
    await message.answer("Пользователь успешно заблокирован")
