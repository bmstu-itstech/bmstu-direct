from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
    start = State() # стартовое состояние
    type = State()  # Вопрос\предложение\проблема
    category = State() # вуц\учеба\общежитие...
    is_anonim = State() # анонимно или нет
    fio = State() # ввод фио
    study_group = State() # ввод учебной группы
    text_statement = State() # ввод текста обращения
    end = State()

class Comments_Moderator(StatesGroup):
    last_moder_mes = State()
    last_user_mes = State()
    question = State()
    problems = State()
    suggestions = State()

