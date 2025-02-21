import logging

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core import domain
from services.db import models

logger = logging.getLogger(__name__)


class TicketNotFoundException(Exception):
    def __init__(self, ticket_id: int):
        super().__init__(f"ticket not found: {ticket_id}")


class BannedUserNotFoundException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"banned user not found: {user_id}")


class MessageNotFoundException(Exception):
    def __init__(self, _id: int):
        super().__init__(f"message not found: id={_id}")


class Storage:
    _db: AsyncSession

    def __init__(self, conn: AsyncSession):
        self._db = conn

    async def save_ticket(self, ticket: domain.Ticket) -> domain.TicketRecord:
        model = models.Ticket.from_domain(ticket)
        self._db.add(model)
        await self._db.commit()
        return model.to_domain()

    async def update_ticket(self, ticket_id: int, **kwargs) -> domain.TicketRecord:
        stmt = select(models.Ticket).filter_by(id=ticket_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise TicketNotFoundException(ticket_id)
        for key, value in kwargs.items():
            if not hasattr(models.Ticket, key):
                raise ValueError(f'Class `models.Ticket` doesn\'t have argument {key}')
        stmt = \
            update(models.Ticket).      \
            filter_by(id=ticket_id).    \
            values(**kwargs)
        await self._db.execute(stmt)
        await self._db.commit()
        return model.to_domain()

    async def save_banned_user(self, user: domain.BannedUser) -> domain.BannedUser:
        model = models.BannedUser.from_domain(user)
        self._db.add(model)
        await self._db.commit()
        return model.to_domain()

    async def is_user_banned(self, chat_id: int) -> bool:
        stmt = select(models.BannedUser).filter_by(chat_id=chat_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        return model is not None

    async def ticket(self, ticket_id: int) -> domain.TicketRecord:
        stmt = select(models.Ticket).filter_by(id=ticket_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise TicketNotFoundException(ticket_id)
        return model.to_domain()

    async def save_message(self, message: domain.Message) -> None:
        model = models.GroupMessage.from_domain(message)
        self._db.add(model)
        await self._db.commit()

    async def message_id(self, _id: int) -> domain.Message:
        """
        Возвращает сообщение с данным ID.
        Вызывает исключение MessageNotFound, если сообщения не в БД.
        """
        stmt = \
            select(models.GroupMessage).    \
            filter_by(message_id=_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise MessageNotFoundException(_id)
        return model.to_domain()

    async def message_by_id(self, ticket_ids: list[int], owner_message_id: int) -> domain.Message:
        stmt = \
            select(models.GroupMessage).    \
            where(
                and_(
                    models.GroupMessage.ticket_id.in_(ticket_ids),
                    models.GroupMessage.owner_message_id == owner_message_id,
                )
            )
        result = await self._db.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise MessageNotFoundException(0)
        return model.to_domain()

    async def message_ticket_id(self, _id: int) -> int:
        stmt = \
            select(models.Ticket.id). \
            filter_by(
                group_message_id=_id
            )
        result = await self._db.execute(stmt)
        ticket_id = result.scalar_one_or_none()
        if not ticket_id:
            raise TicketNotFoundException(_id)
        return ticket_id

    async def chat_ticket_ids(self, chat_id: int) -> list[int]:
        stmt = \
            select(models.Ticket.id). \
            filter_by(owner_chat_id=chat_id)
        result = await self._db.execute(stmt)
        ticket_ids = list(result.scalars().all())
        if not ticket_ids:
            raise TicketNotFoundException(chat_id)
        return ticket_ids
