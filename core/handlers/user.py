import logging

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.util import await_only

from core.states.Ticket_States import Registration, Comments_Moderator
from core.utils.keyboards import *
from core.text import text
from services.db.services.repository import Repo
from config import config


logger = logging.getLogger(__name__)
# config = load_config()

bot = Bot(config.tg_bot.token)
dp = Dispatcher(bot=bot)

questions_chat = config.channel.questions_chat_id # чат для вопросов
problems_chat = config.channel.problems_chat_id # чат для проблем
suggestions_chat = config.channel.suggestions_chat_id # чат для предложений

DATA_TYPE_KEY = 'type'
DATA_CATEGORY_KEY = 'category'
DATA_ANONIM_KEY = 'is_anonim'
DATA_FIO_KEY = 'fio'
DATA_STUDY_GROUP_KEY = 'study_group'
DATA_TEXT_KEY = 'text_statement'

async def start(message: Message, repo: Repo, state: FSMContext):
    # use repo object to iteract with DB
    # await repo.add_user(message.from_user.id)
    await state.finish()
    await message.answer(text.Ticket.hello_message,
                         reply_markup=get_first_statement_button()
                         )

async def choice_start_statement(callback_query: CallbackQuery): # обработчик кнопки Подать заявление
    await Registration.type.set()
    await bot.send_message(text=text.Ticket.ask_type,
                                chat_id=callback_query.from_user.id,
                                reply_markup=get_type_of_statement_keyboard())


"""
Функция для состояние (выбор типа заявления), от этого выбора зависит 
в какой канал будет отправлен тикет к модератору.
"""
async def choice_type_statement(message: Message, state: FSMContext):
    async with state.proxy() as data: # запоминаем тип заявления
        data[DATA_TYPE_KEY] = message.text
    await message.answer(text=text.Ticket.ask_category,
                                        reply_markup=get_category_of_statement_keyboard())
    await Registration.next() # переходим к состоянию category


"""
Функция для состояние (выбора категории), пока что сделана заглушка 
для категорий "Военная кафедра" и "Поступление"
"""
async def choice_is_category(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_CATEGORY_KEY] = message.text

    if message.text == text.StandartCats.army:
        await message.answer(text=text.Ticket.army_links,
                             reply_markup=get_first_statement_button())
        await state.finish()

    elif message.text == text.StandartCats.entry:
        await message.answer(text=text.Ticket.entry_links,
                             reply_markup=get_first_statement_button())
        await state.finish()

    else:
        await message.answer(text=text.Ticket.ask_anonim,
                                        reply_markup=get_anonim_keyboard())
    await Registration.next()


"""
Функция для состояние (выбора анонимно ли подается заявление). В зависимости от этого выбора в дальнейшем будет меняться
маршрут состояний.
"""
async def choice_is_anonim(message: Message, state: FSMContext):
    if message.text == text.Btn.yes:
        async with state.proxy() as data:
            data[DATA_ANONIM_KEY] = "True"

        await message.answer(text=text.Ticket.ask_text, reply_markup=ReplyKeyboardRemove())
        await Registration.text_statement.set()

    elif message.text == text.Btn.no:
        async with state.proxy() as data:
            data[DATA_ANONIM_KEY] = "False"

        await message.answer(text=text.Ticket.ask_name, reply_markup=ReplyKeyboardRemove())
        await Registration.fio.set()

    else:
        await message.answer(text=text.Error.undefined_behaviour, reply_markup=get_anonim_keyboard())


"""
Функция для состояние (ввод Имени\Фио), пока что без валидности (проверки на правильность ввода)
В дальнейшем добавим.
"""
async def input_fio(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_FIO_KEY] = message.text

    await message.answer(text=f'Ваше фио: {message.text}')
    await message.answer(text=text.Ticket.ask_group)
    await Registration.next()


"""
Функция для состояние (ввод учебной группы), пока что без валидности (проверки на правильность ввода)
В дальнейшем добавим.
"""
async def input_study_group(message:  Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_STUDY_GROUP_KEY] = message.text

    await message.answer(text=f'Ваша учебная группа: {message.text}')
    await message.answer(text=text.Ticket.ask_text)
    await Registration.text_statement.set()


"""
функция для последнего (на данный момент) состояния пользователя, ожидание ввода текста заявления.
В дальнейшем будет добавлено состояние, ожидание ответа от модератора.
"""
async def input_text(message: Message, state: FSMContext, repo: Repo):
    async with state.proxy() as data:
        data[DATA_TEXT_KEY] = message.text

    await message.answer(text=f'Вы ввели {message.text}')
    user_data = await state.get_data()
    # all_data = '\n'.join([f"{key}: {value}" for key, value in user_data.items()])
    # # Пока тестовый вывод данные поданного заявления пользователю в чат
    # await message.answer(text= f'Ваши данные из фсм:\n'
    #                                           f'{all_data}')
    await message.answer(text=text.Ticket.successful_sent,
                         reply_markup=get_first_statement_button())

    ticket_id = None
    if data[DATA_ANONIM_KEY] == True:
        await repo.update_user(tg_id=message.from_user.id, name='0', group='0')
        ticket = await repo.add_ticket(tg_user_id=message.from_user.id, tg_link='0',
                              text=data['text_statement'], type=data['type'], category=data['category'],
                              is_anonim=data['is_anonim'], is_closed='False')
        ticket_id = ticket[1]
    elif data[DATA_ANONIM_KEY] == False:
        await repo.update_user(tg_id=message.from_user.id, name=data['fio'], group=data['study_group'])
        ticket = await repo.add_ticket(tg_user_id=message.from_user.id, tg_link='0',
                              text=data['text_statement'], type=data['type'], category=data['category'],
                              is_anonim=data['is_anonim'], is_closed='False')
        ticket_id = ticket[1]


    if data[DATA_TYPE_KEY] == Btn.question:
        await bot.send_message(chat_id=questions_chat, text= f'Новое заявление!\n'
                                                            f'Его данные из фсм:\n'
                                                            f'{all_data}\n\n' 
                                                            f'ID: {ticket_id}')
    elif data[DATA_TYPE_KEY] == Btn.problem:
        await bot.send_message(chat_id=problems_chat, text= f'Новое заявление!\n'
                                                            f'Его данные из фсм:\n'
                                                            f'{all_data}\n\n'
                                                             f'ID: {ticket_id}')
    elif data[DATA_TYPE_KEY] == Btn.suggestion:
        await bot.send_message(chat_id=suggestions_chat, text= f'Новое заявление!\n'
                                                               f'Его данные из фсм:\n'
                                                               f'{all_data}\n\n'
                                                                 f'ID: {ticket_id}')
    await message.answer(text=f'Вы зарегистрировали новое заявление\n'
                              f'Ожидайте ответ от модератора')
    await state.finish()


last_mes = None
reply_last_mes = None


async def forward_comment_question(message: types.Message, repo: Repo, state: FSMContext):
    logging.info('ЗАЯВЛЕНИЕ БЕЗ ФСМ ВОШЛО В ВПОРОСЫ')

    if message.reply_to_message:  # Если сообщение — ответ на другое сообщение
        post_message = message.reply_to_message
        logging.info('СЛОВИЛ ОТВЕТ')

    if message.from_user.is_bot:
        logging.info(f"Ignored message from bot: {message.from_user.username}")
        return  # Игнорируем сообщение, если оно от бота

    if message.forward_from or message.forward_from_chat:
        logging.info("Message was forwarded automatically.")
        return
    else:
        logging.info("message was from moderator or user.")

    try:
        ticket_id = int(message.reply_to_message.text.split()[-1])
        user_id = await repo.get_user_id_from_ticket_id(ticket_id=ticket_id)
        await bot.send_message(chat_id=user_id, text=f'Вам пришел ответ от модератора на ваше заявление #{ticket_id}:\n'
                                                     f' {message.text}')

        global last_mes
        last_mes = message.message_id

        logging.info(f'message sent from moderator, lst_mes id == {last_mes}')

    except Exception as e:
        logging.error('error sending message(not reply or nothing else)')

    await Comments_Moderator.question.set()


async def forward_comment_problems(message: types.Message, repo: Repo, state: FSMContext):
    logging.info('ЗАЯВЛЕНИЕ БЕЗ ФСМ ВОШЛО В ПРОБЛЕМЫ')

    if message.reply_to_message:  # Если сообщение — ответ на другое сообщение
        post_message = message.reply_to_message
        logging.info('СЛОВИЛ ОТВЕТ')

    if message.from_user.is_bot:
        logging.info(f"Ignored message from bot: {message.from_user.username}")
        return  # Игнорируем сообщение, если оно от бота

    if message.forward_from or message.forward_from_chat:
        logging.info("Message was forwarded automatically.")
        return
    else:
        logging.info("message was from moderator or user.")

    await Comments_Moderator.problems.set()
    try:
        ticket_id = int(message.reply_to_message.text.split()[-1])
        user_id = await repo.get_user_id_from_ticket_id(ticket_id=ticket_id)
        await bot.send_message(chat_id=user_id, text=f'Вам пришел ответ от модератора на ваше заявление #{ticket_id}:\n'
                                                     f' {message.text}')

        global last_mes
        last_mes = message.message_id

        logging.info(f'message sent from moderator, lst_mes id == {last_mes}')

    except Exception as e:
        logging.error('error sending message(not reply or nothing else)')


async def forward_comment_suggestions(message: types.Message, repo: Repo, state: FSMContext):
    logging.info('ЗАЯВЛЕНИЕ БЕЗ ФСМ ВОШЛО В ПРЕДЛОЖЕНИЯ')

    if message.reply_to_message:  # Если сообщение — ответ на другое сообщение
        post_message = message.reply_to_message
        logging.info('СЛОВИЛ ОТВЕТ')

    if message.from_user.is_bot:
        logging.info(f"Ignored message from bot: {message.from_user.username}")
        return  # Игнорируем сообщение, если оно от бота

    if message.forward_from or message.forward_from_chat:
        logging.info("Message was forwarded automatically.")
        return
    else:
        logging.info("message was from moderator or user.")


    try:
        ticket_id = int(message.reply_to_message.text.split()[-1])
        user_id = await repo.get_user_id_from_ticket_id(ticket_id=ticket_id)
        await bot.send_message(chat_id=user_id, text=f'Вам пришел ответ от модератора на ваше заявление #{ticket_id}:\n'
                                                     f' {message.text}')

        global last_mes
        last_mes = message.message_id

        logging.info(f'message sent from moderator, lst_mes id == {last_mes}')

    except Exception as e:
        logging.error('error sending message(not reply or nothing else)')
    await Comments_Moderator.suggestions.set()


async def comment_from_users_to_moderator_question(message: Message, state: FSMContext):
    logging.info('ЗАЯВЛЕНИЕ ПО ФСМ ВОШЛО В ВОПРОСЫ')

    if message.reply_to_message:
        logging.info('entry comment users')
        reply_message = message.reply_to_message
        reply_text = message.text

        global last_mes
        global reply_last_mes
        await bot.send_message(chat_id=questions_comment, text=f'Пришло дополнение от пользователя:\n'
                                                               f'{reply_text}', reply_to_message_id=last_mes)
        last_mes = message.message_id
        reply_last_mes = reply_message.message_id

    else:
        logging.info('comment from users not reply')

async def comment_from_users_to_moderator_problems(message: Message, state: FSMContext):
    logging.info('ЗАЯВЛЕНИЕ ПО ФСМ ВОШЛО В ПРОБЛЕМЫ')

    if message.reply_to_message:
        logging.info('entry comment users')
        reply_message = message.reply_to_message
        reply_text = message.text

        global last_mes
        global reply_last_mes
        await bot.send_message(chat_id=problems_comment, text=f'Пришло дополнение от пользователя:\n'
                                                               f'{reply_text}', reply_to_message_id=last_mes)
        last_mes = message.message_id
        reply_last_mes = reply_message.message_id

    else:
        logging.info('comment from users not reply')

async def comment_from_users_to_moderator_suggestions(message: Message, state: FSMContext):
    logging.info('ЗАЯВЛЕНИЕ ПО ФСМ ВОШЛО В ПРЕДЛОЖЕНИЯ')
    if message.reply_to_message:
        logging.info('entry comment users')
        reply_message = message.reply_to_message
        reply_text = message.text

        global last_mes
        global reply_last_mes
        await bot.send_message(chat_id=suggestions_comment, text=f'Пришло дополнение от пользователя:\n'
                                                               f'{reply_text}', reply_to_message_id=last_mes)
        last_mes = message.message_id
        reply_last_mes = reply_message.message_id

    else:
        logging.info('comment from users not reply')

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=[text.Commands.start], state="*")
    dp.register_message_handler(start, Text(text.Btn.back), state='*')
    dp.register_message_handler(choice_start_statement, Text(text.Btn.make_ticket), state='*')
    dp.register_message_handler(choice_type_statement,  state=Registration.type)
    dp.register_message_handler(choice_is_category, state=Registration.category)
    dp.register_message_handler(choice_is_anonim, state=Registration.is_anonim)
    dp.register_message_handler(input_fio, state=Registration.fio)
    dp.register_message_handler(input_study_group, state=Registration.study_group)
    dp.register_message_handler(input_text, state=Registration.text_statement)

    dp.register_message_handler(forward_comment_question, chat_id=questions_comment, state='*')
    # dp.register_message_handler(comment_from_users_to_moderator_question, state='*') Без фсм машины, если только категория вопросы работает до глубины 2
    dp.register_message_handler(comment_from_users_to_moderator_question, state = Comments_Moderator.question)

    dp.register_message_handler(forward_comment_problems, chat_id=problems_comment, state='*')
    dp.register_message_handler(comment_from_users_to_moderator_problems, state=Comments_Moderator.problems)

    dp.register_message_handler(forward_comment_suggestions, chat_id = suggestions_comment, state='*')
    dp.register_message_handler(comment_from_users_to_moderator_suggestions, state=Comments_Moderator.suggestions)
