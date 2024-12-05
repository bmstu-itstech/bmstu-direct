from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from core.text.text import Btn

def get_admin_keyboard() -> types.InlineKeyboardMarkup:
    raise NotImplemented

'''
get_first_statement_button - функция для вызова кнопки подачи заявления
'''
def get_first_statement_button() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(Btn.make_ticket))
    return keyboard

'''
get_type_of_statement_keyboard - функция для вызова клавиатуры выбора типа заявления
Вопросы - question
Проблема - problem
Предложение - suggestion
'''
def get_type_of_statement_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(Btn.question),
                 KeyboardButton(Btn.problem),
                 KeyboardButton(Btn.suggestion),
                 KeyboardButton(Btn.back))
    return keyboard

'''
get_category_of_statement_keyboard - Функция для вызова инлайн клавиатуры для выбора категории
обращения, каждая инлайн кнопка со своим запросом
'''
def get_category_of_statement_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(KeyboardButton(Btn.study),
                 KeyboardButton(Btn.hostel),
                 KeyboardButton(Btn.food),
                 KeyboardButton(Btn.medicine),
                 KeyboardButton(Btn.army),
                 KeyboardButton(Btn.entry),
                 KeyboardButton(Btn.documents),
                 KeyboardButton(Btn.money),
                 KeyboardButton(Btn.electives),
                 KeyboardButton(Btn.other),
                 KeyboardButton(Btn.back),
                 )
    return keyboard

def get_anonim_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(Btn.yes),
                 KeyboardButton(Btn.no),
                 KeyboardButton(Btn.back))
    return keyboard

