from aiogram.dispatcher.filters.state import State, StatesGroup


class Ticket(StatesGroup):
    tg_user_id = State()
    type = State()
    category = State()
    is_anonim = State()
    name = State()
    group = State()
    text = State()


class Answer(StatesGroup):
    """
    Ждем от юзера сообщение устроил ли его ответ модератора
    """
    answer = State()
