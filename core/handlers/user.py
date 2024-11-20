import logging

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message


from core.states.Example import registration
from core.utils.keyboards import *
from services.db.services.repository import Repo
from config import load_config


logger = logging.getLogger(__name__)
config = load_config()

bot = Bot(config.tg_bot.token)
dp = Dispatcher(bot=bot)
channel_1 = config.channel.chat_id

async def start(message: Message, repo: Repo, state: FSMContext):
    # use repo object to iteract with DB
    await state.finish()
    await message.answer("Привет!\n"
                         "Для подачи заявления нажми кнопку ниже",
                         reply_markup=get_first_statement_button()
                         )

def register_user(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
    # dp.register_message_handler(start, state=registration.end)


'''
async def cancel_button(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer(text='Вы вернулись на начальный этап ')
    return choice_start_statement
def process_cancel(dp: Dispatcher):
    dp.register_message_handler(cancel_button, commands=['cancel'])
    # dp.register_callback_query_handler(choice_start_statement)
'''

async def choice_start_statement(callback_query: CallbackQuery): # обработчик кнопки Подать заявление
    await registration.type.set()
    await bot.send_message(text='Далее выберите тип заявления',
                                chat_id=callback_query.from_user.id,
                                reply_markup=get_type_of_statement_keyboard())


async def choice_type_statement(message: Message, state: FSMContext):
    async with state.proxy() as data: # запоминаем тип заявления
        data['type'] = message.text
    await message.answer(text=f'Вы выбрали тип заявления: {message.text}')
    await message.answer(text='Далее выберите категорию заявления: ',
                                        reply_markup=get_category_of_statement_keyboard())
    await registration.next() # переходим к состоянию category



async def choice_is_category(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text

    await message.answer(text= f'Вы выбрали категорию {message.text}')
    if message.text == 'Военная кафедра':
        await message.answer(text='https://aiogram-birdi7.readthedocs.io/en/latest/examples/media_group.html\n'
                                                 'Вот ссылка на сайт вуц\n'
                                                 'Для подачи нового заявления нажмите кнопку "Начать заново"')
        await state.finish()
    elif message.text == 'Поступление':
        await message.answer(text='https://bmstu.ru/\n'
                                                 'Вот ссылка на сайт приемной комисси\n'
                                                 'Для подачи нового заявления нажмите кнопку "Начать заново"')
        await state.finish()
    else:
        await message.answer(text='Выберите как вы хотите задать вопрос(анонимно или нет)',
                                        reply_markup=get_anonim_keyboard())
    await registration.next()



async def choice_is_anonim(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['is_anonim'] = message.text

    await message.answer(text= f'Вы выбрали {message.text}')
    if message.text == 'Да':
        await registration.text_statement.set()
        await message.answer(text='Введите текст обращения: ')
        await registration.text_statement.set()
    else:
        await registration.fio.set()
        await message.answer(text='Введите ваше Фио: ')
        await registration.fio.set()


async def input_fio(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text

    await message.answer(text=f'Ваше фио: {message.text}')
    await message.answer(text='Введите учебную группу')
    await registration.next()


async def input_study_group(message:  Message, state: FSMContext):
    async with state.proxy() as data:
        data['study_group'] = message.text

    await message.answer(text=f'Ваша учебная группа: {message.text}')
    await message.answer(text='Введите текст обращения')
    await registration.text_statement.set()


async def input_text(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['text_statement'] = message.text

    await message.answer(text=f'Вы ввели {message.text}')
    user_data = await state.get_data()
    all_data = '\n'.join([f"{key}: {value}" for key, value in user_data.items()])
    await message.answer(text= f'Ваши данные из фсм:\n'
                                              f'{all_data}')
    await message.answer(text='Для создания нового заявление, нажмите кнопку "Начать заново"',
                         )
    await bot.send_message(chat_id=channel_1, text= all_data )
    await state.finish()



def process_choice(dp: Dispatcher): # стартовый обработчик
        dp.register_message_handler(choice_start_statement)
def process_choice_type(dp: Dispatcher):
    dp.register_message_handler(choice_type_statement,state=registration.type)
def process_category(dp: Dispatcher):
    dp.register_message_handler(choice_is_category, state=registration.category)
def process_anonim(dp: Dispatcher):
    dp.register_message_handler(choice_is_anonim, state=registration.is_anonim)

def process_fio(dp: Dispatcher):
    dp.register_message_handler(input_fio, state=registration.fio)
def process_study_group(dp: Dispatcher):
    dp.register_message_handler(input_study_group, state=registration.study_group)
def process_text_statement(dp: Dispatcher):
    dp.register_message_handler(input_text, state=registration.text_statement)
def  process_end(dp: Dispatcher):
    dp.register_message_handler(start, Text(equals='Начать заново'), state='*')