import os
import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.utils import executor
from sqlalchemy.orm import sessionmaker

from common.repository import bot, dp, config
from core.filters.role import AdminFilter, RoleFilter, ModeratorFilter
from core.middlewares.db import DbMiddleware
from core.middlewares.user_control import UserControlMiddleware
from core.middlewares.album import AlbumMiddleware
from services.db.db_pool import create_db_pool

# NOT REMOVE THIS IMPORT!
from core.handlers import admin, moderator, student


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Подать обращение"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        encoding="UTF-8",
        handlers=[
            logging.FileHandler(os.path.join(config.logs_dir, "bot.log")),
            logging.StreamHandler()
        ]
    )
    logger.info("Starting bot")

    db_pool: sessionmaker = await create_db_pool(
        user=config.db.user,
        password=config.db.password,
        host=config.db.host,
        port=5432,
        name=config.db.name,
        echo=False,
    )

    await set_commands(bot)
    bot_obj = await bot.get_me()
    logger.info(f"Bot username: {bot_obj.username}")
    dp.middleware.setup(DbMiddleware(db_pool))
    dp.middleware.setup(UserControlMiddleware())
    dp.middleware.setup(AlbumMiddleware(wait_time_seconds=1))
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(ModeratorFilter)

    try:
        await dp.start_polling(allowed_updates=["message", "callback_query", "inline_query"])
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
        executor.start_polling(dp, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
