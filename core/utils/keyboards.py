from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.db.services.repository import Repo
from core.text import btn as text


class Buttons:
    # user_buttons
    back = KeyboardButton(text.back)
    make_ticket = KeyboardButton(text.make_ticket)
    help = KeyboardButton(text.help)
    my_tickets = KeyboardButton(text.make_ticket)
    yes = KeyboardButton(text.yes)
    no = KeyboardButton(text.no)
    question = KeyboardButton(text.question)
    problem = KeyboardButton(text.problem)
    suggest = KeyboardButton(text.suggest)

    # admin_buttons
    edit_types = KeyboardButton(text.edit_types)
    edit_categories = KeyboardButton(text.edit_categories)
    block_user = KeyboardButton(text.block_user)
    unblock_user = KeyboardButton(text.unblock_user)
    close_ticket = KeyboardButton(text.close_ticket)
    open_ticket = KeyboardButton(text.open_ticket)
    make_moderator = KeyboardButton(text.make_moderator)
    make_admin = KeyboardButton(text.make_admin)


async def main_kb(is_any_opened_tickets: bool = False):
    base = [
        [Buttons.make_ticket],
        [Buttons.help],
    ]

    if is_any_opened_tickets:
        base.append([Buttons.my_tickets])

    return ReplyKeyboardMarkup(base)


async def type_select_kb():
    return ReplyKeyboardMarkup(
        [[Buttons.problem],
                  [Buttons.question],
                  [Buttons.suggest]], one_time_keyboard=True)


async def categories_select_kb(repo: Repo) -> ReplyKeyboardMarkup:
    cats = await repo.unique_categories()
    base = []
    for i in range(len(cats)):
        if i % 2:
            base[-1].append(KeyboardButton(cats[i]))
        else:
            base.append([KeyboardButton(cats[i])])
        return ReplyKeyboardMarkup(base)


async def yes_no_keyboard():
    return ReplyKeyboardMarkup(
        [[Buttons.yes, Buttons.no],
         [Buttons.back]], one_time_keyboard=True)


async def back_kb():
    return ReplyKeyboardMarkup([[Buttons.back]], one_time_keyboard=True)


async def admin_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[Buttons.edit_types, Buttons.edit_categories],
         [Buttons.block_user, Buttons.unblock_user],
         [Buttons.make_admin, Buttons.make_admin],
         [Buttons.close_ticket, Buttons.open_ticket]]
    )
