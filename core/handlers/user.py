import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from core.models.enums import TicketType
from services.db.services.repository import Repo
from config import load_config
from core.text import text
from core.states.ticket_states import Ticket
from core.utils.variables import bot
from core.utils import funcs, keyboards


logger = logging.getLogger(__name__)
config = load_config()



async def start(msg: Message, repo: Repo, state: FSMContext):
    logger.info('handled start')

    await state.finish()
    is_any_to_edit = await repo.get_opened_tickets_by_user(msg.from_user.id)
    has_opened = True if is_any_to_edit else False
    await msg.answer("Привет!",   reply_markup=keyboards.main_kb(has_opened))


async def create_ticket(msg: Message, state: FSMContext):
    logger.info('handled create')


    await msg.reply(text.Ticket.ask_type,
                    reply_markup=keyboards.type_select_kb())

    await state.set_state(Ticket.group)
    await state.update_data(tg_user_id=msg.from_user.id)
    await state.set_state(Ticket.type)


async def my_tickets(msg: Message, state: FSMContext):
    await state.finish()
    await msg.reply(text.Error.no_func,  reply_markup=keyboards.main_kb())
    raise NotImplemented


async def ticket_type(msg: Message, repo: Repo, state: FSMContext):
    logger.info('handled type')

    if msg.text == text.Btn.problem:
        await state.update_data(type=TicketType.Problem)
    elif msg.text == text.Btn.question:
        await state.update_data(type=TicketType.QUESTION)
    elif msg.text == text.Btn.suggest:
        await state.update_data(type=TicketType.SUGGEST)
    else:
        logger.warning(f'tg_us_id: {msg.from_user.id} undefined behaviour ms: {msg.text}')
        await msg.reply(text.Error.undefined_behaviour,
                         reply_markup=keyboards.type_select_kb())
        return

    await state.set_state(Ticket.category)
    cats = await repo.unique_categories()
    await msg.reply(text.Ticket.ask_category,
                    reply_markup=keyboards.categories_select_kb(cats))


async def ticket_category(msg: Message, repo: Repo, state: FSMContext):
    logger.info('handled cat')
    cats = await repo.unique_categories()
    if msg.text in cats:
        await state.update_data(category=msg.text)
        await msg.reply(text.Ticket.ask_anonim,
                        reply_markup=keyboards.yes_no_keyboard())
        await state.set_state(Ticket.is_anonim)
    else:
        logger.warning(f'tg_us_id: {msg.from_user.id} undefined behaviour ms: {msg.text}')
        await msg.reply(text.Error.undefined_behaviour)


async def ticket_anonim(msg: Message, state: FSMContext):
    logger.info('handled anon')
    if msg.text == text.Btn.yes:
        await state.update_data(is_anonim=True)
        await state.set_state(Ticket.text)
        await msg.reply(text.Ticket.ask_text)
        logger.info(f'tg_us_id: {msg.from_user.id} pinned ticket as anonim')
    elif msg.text == text.Btn.no:
        await state.update_data(is_anonim=False)
        await state.set_state(Ticket.name)
        await msg.reply(text.Ticket.ask_name,
                        reply_markup=keyboards.back_kb())
    else:
        logger.warning(f'tg_us_id: {msg.from_user.id} undefined behaviour ms: {msg.text}')
        await msg.reply(text.Error.undefined_behaviour,
                         reply_markup=keyboards.yes_no_keyboard())


async def ticket_name(msg: Message, state: FSMContext):
    logger.info('handled name')
    if await funcs.validate_name(msg.text):
        await state.update_data(name=msg.text)
        await state.set_state(Ticket.group)
        await msg.reply(text.Ticket.ask_group)
    else:
        logger.warning(f'tg_us_id: {msg.from_user.id} undefined behaviour ms: {msg.text}')
        await msg.reply(text.Ticket.retry_ask_name,
                        reply_markup=keyboards.back_kb())


async def ticket_group(msg: Message, state: FSMContext):
    logger.info('handled group')
    if await funcs.validate_group(msg.text):
        await state.update_data(group=msg.text)
        await state.set_state(Ticket.text)
        await msg.reply(text.Ticket.ask_text)
    else:
        logger.warning(f'tg_us_id: {msg.from_user.id} undefined behaviour ms: {msg.text}')
        await msg.reply(text.Ticket.retry_ask_group,
                        reply_markup=keyboards.back_kb())


async def ticket_text(msg: Message, repo: Repo, state: FSMContext):
    logger.info('handled text')
    await state.update_data(text=msg.text)
    data = await state.get_data()
    await state.finish()
    await send_ticket(repo, data)
    await msg.reply(text.Ticket.successful_sent, reply_markup=keyboards.main_kb())


async def send_ticket(repo: Repo, data: dict):
    chan_id = await funcs.choose_ch_id(data)
    msg = await bot.send_message(chan_id, text.make_ticket_text(data))
    msg_link = await funcs.message_link(chan_id, msg.message_id)
    await funcs.add_ticket(data, msg_link, repo)
    logger.info(f"user {data['tg_user_id']} sent ticket url: {msg_link}")


async def help_handler(msg: Message, state: FSMContext):
    logger.info('handled help')

    await state.finish()
    await msg.reply(text.Ticket.hello_message,
                    reply_markup=keyboards.main_kb())


async def back(msg: Message, state: FSMContext):
    logger.info('handled back')

    await state.finish()
    await msg.reply(text.Ticket.hello_message,
                    reply_markup=keyboards.main_kb())


async def blocked(msg: Message):
    await msg.reply(text.Error.blocked)


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state='*')
    dp.register_message_handler(create_ticket, commands=["create_ticket"])
    dp.register_message_handler(back, Text(text.Btn.back), state='*')
    dp.register_message_handler(back, commands=['back'], state='*')
    dp.register_message_handler(create_ticket, Text(text.Btn.make_ticket))
    dp.register_message_handler(my_tickets,Text(text.Btn.my_tickets))

    dp.register_message_handler(ticket_type, state=Ticket.type)
    dp.register_message_handler(ticket_category, state=Ticket.category)
    dp.register_message_handler(ticket_anonim, state=Ticket.is_anonim)
    dp.register_message_handler(ticket_name, state=Ticket.name)
    dp.register_message_handler(ticket_group, state=Ticket.group)
    dp.register_message_handler(ticket_text, state=Ticket.text)
    dp.register_message_handler(help_handler, commands=["help"])
    dp.register_message_handler(help_handler, Text(text.Btn.help))
