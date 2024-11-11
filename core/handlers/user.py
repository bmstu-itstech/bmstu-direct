import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message

from services.db.services.repository import Repo
from config import load_config


logger = logging.getLogger(__name__)
config = load_config()


async def start(message: Message, repo: Repo, state: FSMContext):
    # use repo object to iteract with DB
    await state.finish()
    await message.answer("Привет!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
