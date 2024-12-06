import enum
import logging
from tokenize import group
from typing import Sequence

from sqlalchemy import select, delete, and_, update, or_, Enum, Boolean, BOOLEAN
from sqlalchemy.ext.asyncio import AsyncSession

from services.db.models import User, Ticket

logger = logging.getLogger(__name__)




class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn: AsyncSession = conn

    async def add_user(
            self,
            tg_id: int, # user table
            name: str,  # user table
            group: str,
    ):
        user = User(
            tg_id=tg_id,
            name=name,
            group=group
        )

        self.conn.add(user)
        await self.conn.commit()

        logger.info(f"add new user with {tg_id=}")

        return user




    async def add_ticket(
            self,
            # ticket_id: int, # id ticket
            tg_user_id: int, #id from user
            tg_link: str,
            text: str,
            type: str,
            category: str,
            is_anonim: str,
            is_closed: str
    ):

        ticket = Ticket(
            tg_user_id=tg_user_id,
            tg_link=tg_link,
            text=text,
            type=type,
            category=category,
            is_anonim=is_anonim,
            is_closed=is_closed

        )
        self.conn.add(ticket)
        await self.conn.commit()


        logger.info(f'add new ticket with id: {ticket.ticket_id}')


        return ticket, ticket.ticket_id


    async def get_user_id_from_ticket_id(self, ticket_id: int):
        stmt = select(Ticket.tg_user_id).filter(Ticket.ticket_id == ticket_id)
        result = await self.conn.execute(stmt)

        id = result.scalar_one_or_none()
        if id:
            return int(id)
        else:
            logger.info(f'Пользователь с тикет айди = {ticket_id} не найден')
            return None

    # async def get_user_by_ticket_id(self, ticket_id: int) -> int:
    #     res = await self.conn.execute(select(User.tg_id).filter(ticket_id == Ticket.ticket_id))
    #
    #     user = res.scalar_one_or_none()
    #     return user


    async def get_users(self) -> Sequence[User]:
        res = await self.conn.execute(
            select(User)
        )

        return res.scalars().all()

    async def get_user_by_telegram_id(self, user_id: int):
        stmt = select(User).filter(User.tg_id == user_id)
        result = await self.conn.execute(stmt)

        user = result.scalar_one_or_none()
        if user:
            return user
        else:
            # logger.info(f"Пользователь с id {user_id} не найден.")
            return None


    async def update_user(
            self,
            tg_id: int,
            name: str,  # user table
            group: str,
    ):
        user = User(
            name=name,
            group=group
        )

        stmt = select(User).filter(User.tg_id == tg_id)
        result = await self.conn.execute(stmt)
        client = result.scalar_one_or_none()

        if user:
            client.name = name
            client.group = group
            await self.conn.commit()
            logger.info(f'add new information in user with id {tg_id=}')
        else:
            logger.info(f'for add new information, user with id {tg_id=} not found')

