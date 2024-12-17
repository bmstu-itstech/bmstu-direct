from aiogram.dispatcher.filters.state import State, StatesGroup


class CommentsModerator(StatesGroup):
    last_moder_mes = State()
    last_user_mes = State()
    question = State()
    problems = State()
    suggestions = State()
