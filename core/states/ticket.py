from aiogram.dispatcher.filters.state import State, StatesGroup


class Ticket(StatesGroup):
    tg_user_id = State()
    type = State()
    category = State()
    is_anonim = State()
    name = State()
    group = State()
    text = State()
