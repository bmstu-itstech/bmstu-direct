from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
    create_ticket = State()
    choice_issue = State()
    choice_category = State()
    choice_privacy = State()
    input_full_name = State()
    input_study_group = State()
    input_text = State()
    choice_approve = State()
