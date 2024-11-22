from aiogram import Bot

from config import load_config

config = load_config()

bot = Bot(token=config.tg_bot.token)
channel_ids = config.tg_bot