from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from core.text import text

def get_admin_keyboard() -> types.InlineKeyboardMarkup:
    raise NotImplemented

'''
get_first_statement_button - функция для вызова кнопки подачи заявления
'''
def get_first_statement_button() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(text.Btn.make_ticket))
    return keyboard

'''
get_type_of_statement_keyboard - функция для вызова клавиатуры выбора типа заявления
Вопросы - question
Проблема - problem
Предложение - suggestion
'''
def get_type_of_statement_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(text.Btn.question),
                 KeyboardButton(text.Btn.problem),
                 KeyboardButton(text.Btn.suggest),
                 KeyboardButton(text.Btn.back))
    return keyboard

'''
get_category_of_statement_keyboard - Функция для вызова инлайн клавиатуры для выбора категории
обращения, каждая инлайн кнопка со своим запросом
'''
def get_category_of_statement_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(KeyboardButton(text.StandartCats.study),
                 KeyboardButton(text.StandartCats.hostel),
                 KeyboardButton(text.StandartCats.food),
                 KeyboardButton(text.StandartCats.medicine),
                 KeyboardButton(text.StandartCats.army),
                 KeyboardButton(text.StandartCats.entry),
                 KeyboardButton(text.StandartCats.documents),
                 KeyboardButton(text.StandartCats.money),
                 KeyboardButton(text.StandartCats.electives),
                 KeyboardButton(text.StandartCats.other),
                 KeyboardButton(text.Btn.back),
                 )
    return keyboard

def get_anonim_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(text.Btn.yes),
                 KeyboardButton(text.Btn.no),
                 KeyboardButton(text.Btn.back))
    return keyboard

