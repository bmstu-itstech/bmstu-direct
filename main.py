import os
import asyncio
import logging

from aiogram.utils import executor
from sqlalchemy.orm import sessionmaker

from common.repository import bot, dp, config
from core.middlewares.db import DbMiddleware
from services.db.db_pool import create_db_pool

# NOT REMOVE THIS IMPORT!
from core.handlers import student, moderator


logger = logging.getLogger(__name__)


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

    db_pool: sessionmaker = await create_db_pool(
        user=config.db.user,
        password=config.db.password,
        host=config.db.host,
        # port=config.db.port,
        port=5432,
        name=config.db.name,
        echo=False,
    )

    bot_obj = await bot.get_me()
    logger.info(f"Bot username: {bot_obj.username}")
    dp.middleware.setup(DbMiddleware(db_pool))

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
