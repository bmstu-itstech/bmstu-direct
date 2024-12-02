from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from core.text.text import Btn as Text


class Buttons:
    # user_buttons
    back = KeyboardButton(Text.back)
    make_ticket = KeyboardButton(Text.make_ticket)
    help = KeyboardButton(Text.help)
    my_tickets = KeyboardButton(Text.make_ticket)
    yes = KeyboardButton(Text.yes)
    no = KeyboardButton(Text.no)
    question = KeyboardButton(Text.question)
    problem = KeyboardButton(Text.problem)
    suggest = KeyboardButton(Text.suggest)

    # admin_buttons
    edit_types = KeyboardButton(Text.edit_types)
    edit_categories = KeyboardButton(Text.edit_categories)
    block_user = KeyboardButton(Text.block_user)
    unblock_user = KeyboardButton(Text.unblock_user)
    close_ticket = KeyboardButton(Text.close_ticket)
    open_ticket = KeyboardButton(Text.open_ticket)
    make_moderator = KeyboardButton(Text.make_moderator)
    make_admin = KeyboardButton(Text.make_admin)


def main_kb(is_any_opened_tickets: bool = False) -> ReplyKeyboardMarkup:
    base = [
        [Buttons.make_ticket],
        [Buttons.help],
    ]

    if is_any_opened_tickets:
        base.append([Buttons.my_tickets])

    return ReplyKeyboardMarkup(base)


def type_select_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[Buttons.problem],
                  [Buttons.question],
                  [Buttons.suggest],
                  [Buttons.back]], one_time_keyboard=True, resize_keyboard=True)


def categories_select_kb(cats: list[str]) -> ReplyKeyboardMarkup:
    base = []
    for i in range(len(cats)):
        if i % 2:
            base[-1].append(KeyboardButton(cats[i]))
        else:
            base.append([KeyboardButton(cats[i])])

    base.append([Buttons.back])
    return ReplyKeyboardMarkup(base, resize_keyboard=True)


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[Buttons.yes, Buttons.no],
         [Buttons.back]], one_time_keyboard=True)


def back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[Buttons.back]], one_time_keyboard=True)


def admin_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[Buttons.edit_types, Buttons.edit_categories],
         [Buttons.block_user, Buttons.unblock_user],
         [Buttons.make_admin, Buttons.make_admin],
         [Buttons.close_ticket, Buttons.open_ticket]]
    )
