from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def get_admin_keyboard() -> types.InlineKeyboardMarkup:
    raise NotImplemented

'''
get_first_statement_button - функция для вызова кнопки подачи заявления
'''
def get_first_statement_button() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(text='Подать заявление'))
    return keyboard

'''
get_type_of_statement_keyboard - функция для вызова клавиатуры выбора типа заявления
Вопросы - question
Проблема - problem
Предложение - suggestion
'''
def get_type_of_statement_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(text='Вопрос'),
                 KeyboardButton(text='Проблема'),
                 KeyboardButton(text='Предложение'),
                 KeyboardButton(text='Назад'))
    return keyboard

'''
get_category_of_statement_keyboard - Функция для вызова инлайн клавиатуры для выбора категории
обращения, каждая инлайн кнопка со своим запросом
'''
def get_category_of_statement_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(text='Учёба'),
                 KeyboardButton(text='Общежитие'),
                 KeyboardButton(text='Питание'),
                 KeyboardButton(text='Медицина'),
                 KeyboardButton(text='Военная кафедра'),
                 KeyboardButton(text='Поступление'),
                 KeyboardButton(text='Документы'),
                 KeyboardButton(text='Стипендия и соц.выплаты'),
                 KeyboardButton(text='Внеучебная деятельность'),
                 KeyboardButton(text='Другое'),
                 KeyboardButton(text='Назад'),
                 )
    return keyboard

def get_anonim_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(text='Да'),
                 KeyboardButton(text='Нет'),
                 KeyboardButton(text='Назад'))
    return keyboard
