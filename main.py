import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.types import BotCommand, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.orm import sessionmaker

from config import load_config
from core.filters.role import RoleFilter, AdminFilter
from core.handlers.admin import register_admin
from core.handlers.user import register_user, process_choice, process_category, process_anonim, \
    process_choice_type, process_fio, process_study_group, process_text_statement, process_end
from core.middlewares.db import DbMiddleware
from core.middlewares.role import RoleMiddleware
from core.middlewares.user_control import UserControlMiddleware
from core.utils.variables import bot
from services.db.db_pool import create_db_pool


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Открыть меню"),
    ]
    await bot.set_my_commands(commands)


async def main():
    if os.path.isfile('bot.log'):
        os.remove('bot.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        encoding="UTF-8",
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )
    logger.info("Starting bot")
    config = load_config()

    storage = MemoryStorage()
    db_pool: sessionmaker = await create_db_pool(
        user=config.db.user,
        password=config.db.password,
        address=config.db.address,
        name=config.db.name,
        echo=False,
    )

    await set_commands(bot)
    bot_obj = await bot.get_me()
    logger.info(f"Bot username: {bot_obj.username}")
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(DbMiddleware(db_pool))
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admin_ids))
    dp.middleware.setup(UserControlMiddleware())
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    register_admin(dp)
    register_user(dp)

    # process_cancel(dp)
    process_fio(dp)
    process_end(dp)
    process_text_statement(dp)
    process_study_group(dp)
    process_choice(dp) # Вход в первое состояние типа заявление
    process_choice_type(dp) # Обработчик def_choice_type_statement
    process_category(dp) # Обработчик def_choice_is_category
    process_anonim(dp) # Обработчик def_choice_is_anonim



    try:
        await dp.start_polling(allowed_updates=["message", "callback_query", "inline_query"])
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
        executor.start_polling(Dispatcher, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
