import datetime

from aiogram.dispatcher.handler import CancelHandler
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
        # todo: add user if it does not exist in DB

    async def post_process(self, obj, data, *args):
        del data["repo"]
        db = data.get("db")
        if db:
            await db.close()
