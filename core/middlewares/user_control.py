# import datetime
#
# from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from config import load_config
from services.db.services.repository import Repo


config = load_config()


class UserControlMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        if obj is not None and not obj.from_user.is_bot:
            this_user = obj.from_user
        else:
            return

        repo: Repo = data["repo"]
        tg_user_id: int = obj.this_user.id
        await repo.add_user(tg_user_id=tg_user_id)

    async def post_process(self, obj, data, *args):
        del data["repo"]
        db = data.get("db")
        if db:
            await db.close()
