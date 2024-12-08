import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import domain
from services.db import models

logger = logging.getLogger(__name__)


class TicketNotFoundException(Exception):
    def __init__(self, ticket_id: int):
        super().__init__(f"ticket not found: {ticket_id}")


class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"user not found: {user_id}")


class Storage:

    conn: AsyncSession

    def __init__(self, conn: AsyncSession):
        self.conn = conn

    async def save_ticket(self, ticket: domain.Ticket) -> domain.TicketRecord:
        model = models.Ticket.from_domain(ticket)
        self.conn.add(model)
        await self.conn.commit()
        return model.to_domain()  # Возвращает обновлённую сущность.

    async def ticket(self, ticket_id: int) -> domain.Ticket:
        stmt = select("*").where(models.Ticket.id== ticket_id)
        result = await self.conn.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise TicketNotFoundException(ticket_id)
        return model.to_domain()

    async def user(self, chat_id: int) -> domain.User:
        stmt = select("*").where(models.User.chat_id == chat_id)
        result = await self.conn.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise UserNotFoundException(chat_id)
        return model.to_domain()
