import logging

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.states.Ticket_States import registration
from core.utils.keyboards import *
from services.db.services.repository import Repo
from config import load_config


logger = logging.getLogger(__name__)
config = load_config()

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
    await message.answer("Привет!\n"
                         "Для подачи заявления нажми кнопку ниже",
                         reply_markup=get_first_statement_button()
                         )

async def choice_start_statement(callback_query: CallbackQuery): # обработчик кнопки Подать заявление
    await registration.type.set()
    await bot.send_message(text='Далее выберите тип заявления',
                                chat_id=callback_query.from_user.id,
                                reply_markup=get_type_of_statement_keyboard())


"""
Функция для состояние (выбор типа заявления), от этого выбора зависит 
в какой канал будет отправлен тикет к модератору.
"""
async def choice_type_statement(message: Message, state: FSMContext):
    async with state.proxy() as data: # запоминаем тип заявления
        data[DATA_TYPE_KEY] = message.text
    await message.answer(text=f'Вы выбрали тип заявления: {message.text}')
    await message.answer(text='Далее выберите категорию заявления: ',
                                        reply_markup=get_category_of_statement_keyboard())
    await registration.next() # переходим к состоянию category


"""
Функция для состояние (выбора категории), пока что сделана заглушка 
для категорий "Военная кафедра" и "Поступление"
"""
async def choice_is_category(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_CATEGORY_KEY] = message.text

    await message.answer(text= f'Вы выбрали категорию {message.text}')
    if message.text == btn.army:
        await message.answer(text='https://aiogram-birdi7.readthedocs.io/en/latest/examples/media_group.html\n'
                                                 'Вот ссылка на сайт вуц\n'
                                                 'Для подачи нового заявления нажмите кнопку "Начать заново"',
                             reply_markup=get_first_statement_button())
        await state.finish()
    elif message.text == btn.entry:
        await message.answer(text='https://bmstu.ru/\n'
                                                 'Вот ссылка на сайт приемной комиссии\n'
                                                 'Для подачи нового заявления нажмите кнопку "Начать заново"',
                             reply_markup=get_first_statement_button())
        await state.finish()
    else:
        await message.answer(text='Выберите как вы хотите задать вопрос(анонимно или нет)',
                                        reply_markup=get_anonim_keyboard())
    await registration.next()

"""
Функция для состояние (выбора анонимно ли подается заявление). В зависимости от этого выбора в дальнейшем будет меняться
маршрут состояний.
"""
async def choice_is_anonim(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_ANONIM_KEY] = message.text

    await message.answer(text= f'Вы выбрали {message.text}')
    if message.text == btn.yes:
        await registration.text_statement.set()
        await message.answer(text='Введите текст обращения: ', reply_markup=ReplyKeyboardRemove())
        await registration.text_statement.set()
    else:
        await registration.fio.set()
        await message.answer(text='Введите ваше Фио: ', reply_markup=ReplyKeyboardRemove())
        await registration.fio.set()

"""
Функция для состояние (ввод Имени\Фио), пока что без валидности (проверки на правильность ввода)
В дальнейшем добавим.
"""
async def input_fio(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_FIO_KEY] = message.text

    await message.answer(text=f'Ваше фио: {message.text}')
    await message.answer(text='Введите учебную группу')
    await registration.next()

"""
Функция для состояние (ввод учебной группы), пока что без валидности (проверки на правильность ввода)
В дальнейшем добавим.
"""
async def input_study_group(message:  Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATA_STUDY_GROUP_KEY] = message.text

    await message.answer(text=f'Ваша учебная группа: {message.text}')
    await message.answer(text='Введите текст обращения')
    await registration.text_statement.set()

"""
функция для последнего (на данный момент) состояния пользователя, ожидание ввода текста заявления.
В дальнейшем будет добавлено состояние, ожидание ответа от модератора.
"""
async def input_text(message: Message, state: FSMContext, repo: Repo):
    async with state.proxy() as data:
        data[DATA_TEXT_KEY] = message.text

    await message.answer(text=f'Вы ввели {message.text}')
    user_data = await state.get_data()
    all_data = '\n'.join([f"{key}: {value}" for key, value in user_data.items()])
    # Пока тестовый вывод данные поданного заявления пользователю в чат
    await message.answer(text= f'Ваши данные из фсм:\n'
                                              f'{all_data}')
    await message.answer(text='Для создания нового заявление, нажмите кнопку "Начать заново"',
                         reply_markup=get_first_statement_button())


    if data[DATA_ANONIM_KEY] == btn.yes:
        await repo.update_user(tg_id=message.from_user.id, name='0', group='0')
        await repo.add_ticket(tg_user_id=message.from_user.id, tg_link='0',
                              text=data['text_statement'], type=data['type'], category=data['category'],
                              is_anonim=data['is_anonim'], is_closed='False')
    elif data[DATA_ANONIM_KEY] == btn.no:
        await repo.update_user(tg_id=message.from_user.id, name=data['fio'], group=data['study_group'])
        await repo.add_ticket(tg_user_id=message.from_user.id, tg_link='0',
                              text=data['text_statement'], type=data['type'], category=data['category'],
                              is_anonim=data['is_anonim'], is_closed='False')


    if data[DATA_TYPE_KEY] == btn.question:
        await bot.send_message(chat_id=questions_chat, text= f'Новое заявление!\n'
                                                        f'Его данные из фсм:\n'
                                                        f'{all_data}' )
    elif data[DATA_TYPE_KEY] == btn.problem:
        await bot.send_message(chat_id=problems_chat, text= f'Новое заявление!\n'
                                                        f'Его данные из фсм:\n'
                                                        f'{all_data}'  )
    elif data[DATA_TYPE_KEY] == btn.suggestion:
        await bot.send_message(chat_id=suggestions_chat, text= f'Новое заявление!\n'
                                                        f'Его данные из фсм:\n'
                                                        f'{all_data}'  )

    await state.finish()



def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(start, Text(equals='Назад'), state='*')
    dp.register_message_handler(choice_start_statement, Text(equals='Подать заявление'))
    dp.register_message_handler(choice_type_statement,  state=registration.type)
    dp.register_message_handler(choice_is_category, state=registration.category)
    dp.register_message_handler(choice_is_anonim, state=registration.is_anonim)
    dp.register_message_handler(input_fio, state=registration.fio)
    dp.register_message_handler(input_study_group, state=registration.study_group)
    dp.register_message_handler(input_text, state=registration.text_statement)

