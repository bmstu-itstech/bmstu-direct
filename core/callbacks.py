
from aiogram.utils.callback_data import CallbackData


StatusCallback = CallbackData("my_action", "status", "ticket_id")


def make_status_cb(pack_status: str, pack_ticket_id: int):
    return StatusCallback.new(status=pack_status, ticket_id=pack_ticket_id)
