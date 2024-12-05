from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from services.db.services.repository import Repo


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def pre_process(self, obj, data, *args):
        db: AsyncSession = self.pool()
        data["db"] = db
        data["repo"] = Repo(db)
