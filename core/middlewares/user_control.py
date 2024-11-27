# import datetime
#
# from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from config import load_config
from services.db.services.repository import Repo, logger

config = load_config()


class UserControlMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        if obj is not None and not obj.from_user.is_bot:
            this_user = obj.from_user.id
            repo: Repo = data["repo"]
            usr = await repo.get_user(this_user)
            if usr is None:
                tg_user_id: int = this_user
                await repo.add_user(tg_user_id=tg_user_id)
            logger.info('user already exist')
            return
        else:
            return

    async def post_process(self, obj, data, *args):
        del data["repo"]
        db = data.get("db")
        if db:
            await db.close()