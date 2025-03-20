
from aiogram.utils.callback_data import CallbackData


Status_callback = CallbackData("my_action", "status",  "ticket_id")


def make_status_cb(pack_status: str, pack_ticket_id: int):
    return Status_callback.new(status=pack_status, ticket_id=pack_ticket_id)
