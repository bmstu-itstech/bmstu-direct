import logging
from typing import Sequence

from sqlalchemy import select, text, Null
from sqlalchemy.ext.asyncio import AsyncSession

from core.text import text
from services.db.models import User, Ticket, Category
from core.models.enums import UserRole, TicketType


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
        user = User(
            tg_user_id=tg_user_id,
            role=role
        )

        self.conn.add(user)
        await self.conn.commit()

        logger.info(f"Added new user with {tg_user_id=}")

        return user

    async def get_users(self) -> Sequence[User]:
        res = await self.conn.execute(
            select(User).where()
        )

        return res.scalars().all()


    async def get_user(self, user_id: int) -> Sequence[User]:
        res = await self.conn.execute(select(User).filter(user_id == User.tg_user_id))

        return res.scalars().one_or_none()



    async def update_user(self, user_id: int, name: str, group: str):
        user = User(
            name=name,
            group=group
        )

        stmt = select(User).filter(user_id == User.tg_user_id)
        result = await self.conn.execute(stmt)
        person = result.scalar_one_or_none()

        if user:
            person.name = name
            person.group = group
            await self.conn.commit()
            logger.info(f'add new information in user with id {user_id=}')


    async def get_opened_tickets_by_user(self, user_id: int) -> Sequence[Ticket]:
        res = await self.conn.execute(select(Ticket).filter(user_id == Ticket.tg_user_id))

        tickets = res.scalars().all()
        return tickets


    async def get_num_categories(self) -> int:
        result = await self.conn.execute(text("SELECT MAX(id) FROM categories"))

        n = result.scalars().one_or_none().get(Category.id)

        return n if result is not None else 0


    async def add_ticket(self,
                         tg_user_id: int,
                         tg_link: str,
                         ticket_text: str,
                         ticket_type: TicketType,
                         ticket_category: str,
                         is_anonim: bool = True,
                         name: str = Null,
                         group: str = Null):

        ticket_id = await self.get_num_tickets() + 1

        ticket_row = Ticket(
            ticket_id=ticket_id,
            tg_user_id=tg_user_id,
            tg_link=tg_link,
            text=ticket_text,
            ticket_type=ticket_type,
            is_anonim=is_anonim,
            if_closed=False,
            name=name,
            group=group
        )

        cat_id = await self.get_num_categories() + 1

        category_row = Category(
            id=cat_id,
            ticket_id=ticket_id,
            category=ticket_category
        )

        self.conn.add(ticket_row)
        self.conn.add(category_row)
        await self.conn.commit()

        logger.info(f"Added new ticket with {ticket_id=} and its category")

        return ticket_row, category_row


    async def get_num_tickets(self) -> int:
        result = await self.conn.execute(text("SELECT MAX(ticket_id) FROM tickets"))

        n = result.scalars().one_or_none().get(Ticket.ticket_id)

        if result is not None:
            print(f"The highest user_id is: {n}")
        else:
            print("The users table is empty.")

        logger.info(f'len of ticket table == {n + 1}')

        return n


    async def unique_categories(self):
        res = await self.conn.execute(select(Category.category).distinct())
        categories = res.scalars().all()
        logger.info(categories)
        if not categories:
            logger.info('no cats')
            zero_ticket = Ticket(
                ticket_id=-1,
                tg_user_id=-1,
                tg_link='',
                text='',
                ticket_type=TicketType.Problem,
                is_anonim=True,
                is_closed=True
            )
            self.conn.add(zero_ticket)
            await self.conn.commit()

            for i in range(len(text.cats)):
                cat_row = Category(
                    id=i,
                    ticket_id=-1,
                    category=text.cats[i]
                )
                logger.info(text.cats[i])
                self.conn.add(cat_row)
                await self.conn.commit()

            logger.info('added cats')
            return await self.unique_categories()

        logger.info(categories)
        return list(categories)
