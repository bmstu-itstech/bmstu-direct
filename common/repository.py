from pybars import Compiler
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import config


bot = Bot(token=config.telegram_bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
compiler = Compiler()
