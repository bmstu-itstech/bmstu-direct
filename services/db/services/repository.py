import logging
from typing import Sequence

from sqlalchemy import select, text
# from sqlalchemy import delete, and_, update, or_, ClauseElement
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

from services.db.models import Users, Tickets, Category
from core.models.role import UserRole
from core.models.ticket import TicketType

logger = logging.getLogger(__name__)


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn: AsyncSession = conn

    async def add_user(
            self,
            tg_user_id: int,
            role : UserRole = UserRole.User
    ):
        user = Users(
            telegram_id=tg_user_id,
            role=role
        )

        self.conn.add(user)
        await self.conn.commit()

        logger.info(f"Added new user with {tg_user_id=}")

        return user

    async def get_users(self) -> Sequence[Users]:
        res = await self.conn.execute(
            select(Users).where()
        )

        return res.scalars().all()


    async def get_opened_tickets_by_user(self, user_id: int) -> Sequence[Tickets]:
        res = await self.conn.execute(select(Tickets).filter(user_id == Tickets.tg_user_id))

        tickets = res.scalars().all()
        return tickets


    async def get_num_tickets(self) -> int:
        result = await self.conn.execute(text("SELECT MAX(ticket_id) FROM tickets"))

        n = result.scalars().one_or_none().get(Tickets.ticket_id)

        if result is not None:
            print(f"The highest user_id is: {n}")
        else:
            print("The users table is empty.")

        logger.info(f'len of ticket table == {n + 1}')

        return n


    async def add_ticket(self,
                         tg_user_id: int,
                         tg_link: str,
                         ticket_text: str,
                         ticket_type: TicketType,
                         is_anonim: bool = True):

        ticket_id = await self.get_num_tickets() + 1

        ticket = Tickets(
            ticket_id=ticket_id,
            tg_user_id=tg_user_id,
            tg_link=tg_link,
            text=ticket_text,
            ticket_type=ticket_type,
            is_anonim=is_anonim
        )

        self.conn.add(ticket)
        await self.conn.commit()

        logger.info(f"Added new ticket with {ticket_id=}")

        return ticket


    async def unique_categories(self) -> tuple:
        res = await self.conn.execute(select(Category.category).distinct())
        cats = res.scalars().all()
        return tuple(cats)
