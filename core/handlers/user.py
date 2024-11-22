import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
# from sqlalchemy.util import await_fallback

from core.models.ticket import TicketType
from services.db.services.repository import Repo
from config import load_config
from core.text import btn
from core import states, text
from core.utils.variables import bot, channel_ids
from core.utils import funcs, keyboards


logger = logging.getLogger(__name__)
config = load_config()



async def start(msg: Message, repo: Repo, state: FSMContext):
    # use repo object to interact with DB


    await state.finish()
    await msg.answer("Привет!", reply_markup= await keyboards.main_kb())

    logger.info((channel_ids.question_channel, channel_ids.question_chat))

    mes = await bot.send_message(chat_id=channel_ids.question_channel, text='qwerty')

    logger.info(mes)
    mes_id = mes.message_id
    mes_link = funcs.message_link(channel_ids.question_channel, mes_id)

    logger.info(mes_id)

    await mes.reply(text=f'asdf {mes_id}')
    await bot.send_message(channel_ids.question_chat, 'a')
    await bot.send_message(channel_ids.question_chat, f'asd {mes_id}',
                           reply_to_message_id=mes_id)


async def create_ticket(msg: Message, state: FSMContext):
    await msg.reply(text.ticket.ask_type,
                    reply_markup=await keyboards.type_select_kb())

    await state.set_state(states.ticket.Ticket.tg_user_id)
    await state.update_data(tg_user_id=msg.from_user.id)
    await state.set_state(states.ticket.Ticket.type)


async def ticket_type(msg: Message,repo: Repo, state: FSMContext):
    if msg.text == text.btn.problem:
        await state.update_data(ticket_type=TicketType.Problem)
    elif msg.text == text.btn.question:
        await state.update_data(ticket_type=TicketType.Question)
    elif msg.text == text.btn.suggest:
        await state.update_data(ticket_type=TicketType.Suggest)
    else:
        await msg.reply(text.errors.undefined_behaviour,
                        reply_markup=await keyboards.type_select_kb())
        return

    await state.set_state(states.ticket.Ticket.category)
    await msg.reply(text.ticket.ask_category,
              reply_markup=await keyboards.categories_select_kb(repo=repo))


async def ticket_category(msg: Message, repo: Repo, state: FSMContext):
    if msg.text in repo.unique_categories():
        await state.update_data(category=msg.text)
        await msg.reply(text.ticket.ask_anonim,
                        reply_markup=await keyboards.yes_no_keyboard())
        await state.set_state(states.ticket.Ticket.is_anonim)
    else:
        await msg.reply(text.errors.undefined_behaviour)


async def ticket_anonim(msg: Message, repo: Repo, state: FSMContext):
    pass


async def ticket_name(msg: Message, repo: Repo, state: FSMContext):
    pass


async def ticket_group(msg: Message, repo: Repo, state: FSMContext):
    pass


async def ticket_text(msg: Message, repo: Repo, state: FSMContext):
    await state.update_data(text=msg.text)
    data = await state.get_data()
    await state.finish()

    # await repo.add_ticket(data["tg_user_id"])


async def help(msg: Message, state: FSMContext):
    await state.finish()
    await msg.reply(text.ticket.hello_message,
                    reply_markup=await keyboards.main_kb())


async def back(msg: Message, state: FSMContext):
    pass


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(create_ticket, Text(equals=btn.open_ticket), commands=['/create_ticket'])
    dp.register_message_handler(ticket_type, state=states.ticket.Ticket.type)
    dp.register_message_handler(ticket_category, state=states.ticket.Ticket.category)
    dp.register_message_handler(ticket_anonim, state=states.ticket.Ticket.is_anonim)
    dp.register_message_handler(ticket_name, state=states.ticket.Ticket.name)
    dp.register_message_handler(ticket_group, state=states.ticket.Ticket.group)
    dp.register_message_handler(ticket_text, state=states.ticket.Ticket.text)
    dp.register_message_handler(help, Text(equals=btn.help), commands=["help"])
    # dp.register_message_handler()

