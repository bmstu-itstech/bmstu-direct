import logging

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, InputFile
import asyncio
from io import StringIO, BytesIO
import csv


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


@dp.message_handler(AdminFilter(), Command("export"), state="*")
async def export(message: Message, store: Storage):
    logger.info(f"!!  EXPORT ENTRY")
    data_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    chat_id = message.chat.id
    await store.export_all(data_queue, stop_event)
    await send_csv(chat_id, message, data_queue, stop_event)


async def send_csv(chat_id: int, message: Message, data_queue: asyncio.Queue, stop_event: asyncio.Event):
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer,  dialect = "excel")

    try:
        csv_buffer.write('\ufeff')
        while not stop_event.is_set() or not data_queue.empty():
            try:
                row = await asyncio.wait_for(data_queue.get(), timeout=0.1)
                csv_writer.writerow(row)
                data_queue.task_done()
            except asyncio.TimeoutError:
                pass

        csv_buffer.seek(0)
        file = InputFile(csv_buffer, filename="Tickets.csv")
        await message.bot.send_document(chat_id, document=file)
    finally:
        csv_buffer.close()