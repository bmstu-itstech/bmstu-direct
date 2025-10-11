from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from core.domain.status import Status
from core import texts
from core.callbacks import make_status_cb


def create_ticket_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(texts.buttons.create_ticket))
    return keyboard


def choice_issue_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(*[
        KeyboardButton(issue) for issue in texts.buttons.issues
    ], KeyboardButton(texts.buttons.back))
    return keyboard


def choice_category_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
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


def choice_processing_pd_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton(texts.buttons.yes))
    return keyboard


def choice_approve_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        KeyboardButton(texts.buttons.yes),
        KeyboardButton(texts.buttons.no),
    )
    return keyboard


def status_opened_keyboard(ticket_id: int) -> types.InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        InlineKeyboardButton(
            texts.buttons.status_admins,
            callback_data=make_status_cb(Status.ADMINS, ticket_id)
            ),
        InlineKeyboardButton(
            texts.buttons.status_close,
            callback_data=make_status_cb(Status.CLOSED, ticket_id)
            )
    )
    return keyboard


def status_in_progress_keyboard(ticket_id: int) -> types.InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        InlineKeyboardButton(
            texts.buttons.status_admins,
            callback_data=make_status_cb(Status.ADMINS, ticket_id)
            ),
        InlineKeyboardButton(
            texts.buttons.status_close,
            callback_data=make_status_cb(Status.CLOSED, ticket_id)
            )
    )
    return keyboard


def status_admins_keyboard(ticket_id: int) -> types.InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        InlineKeyboardButton(
            texts.buttons.status_open,
            callback_data=make_status_cb(Status.OPENED, ticket_id)
            ),
        InlineKeyboardButton(
            texts.buttons.status_close,
            callback_data=make_status_cb(Status.CLOSED, ticket_id)
            )
    )
    return keyboard


def status_closed_keyboard(ticket_id: int) -> types.InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        InlineKeyboardButton(
            texts.buttons.status_open,
            callback_data=make_status_cb(Status.OPENED, ticket_id)
            )
    )
    return keyboard


def keyboard_by_status(status: Status, ticket_id: int) -> types.InlineKeyboardButton | None:
    keyboard = None
    match status:
        case Status.OPENED:
            keyboard = status_opened_keyboard(ticket_id)
        case Status.CLOSED:
            keyboard = status_closed_keyboard(ticket_id)
        case Status.IN_PROGRESS:
            keyboard = status_in_progress_keyboard(ticket_id)
        case Status.ADMINS:
            keyboard = status_admins_keyboard(ticket_id)

    return keyboard
