import logging
from typing import Sequence

from sqlalchemy import select, delete, and_, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from services.db.models import User

logger = logging.getLogger(__name__)


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn: AsyncSession = conn

    async def add_user(
            self,
            telegram_id: int,
    ):
        user = User(
            telegram_id=telegram_id,
        )

        self.conn.add(user)
        await self.conn.commit()

        logger.info(f"add new user with {telegram_id=}")

        return user

    async def get_users(self) -> Sequence[User]:
        res = await self.conn.execute(
            select(User)
        )

        return res.scalars().all()
