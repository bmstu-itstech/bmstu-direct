from aiogram.dispatcher.filters.state import State, StatesGroup


class Answer(StatesGroup):
    """
    Ждем от юзера сообщение устроил ли его ответ модератора
    """
    answer = State()
