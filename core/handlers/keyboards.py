from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from core import texts


def create_ticket_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(texts.buttons.create_ticket))
    return keyboard


def choice_issue_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(*[
        KeyboardButton(issue) for issue in texts.buttons.issues
    ])
    return keyboard


def choice_category_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(*[
        KeyboardButton(category) for category in texts.buttons.categories
    ], KeyboardButton(texts.buttons.back))
    return keyboard


def choice_privacy_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        KeyboardButton(texts.buttons.yes),
        KeyboardButton(texts.buttons.no),
        KeyboardButton(texts.buttons.back),
    )
    return keyboard


def choice_approve_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        KeyboardButton(texts.buttons.yes),
        KeyboardButton(texts.buttons.no),
    )
    return keyboard
