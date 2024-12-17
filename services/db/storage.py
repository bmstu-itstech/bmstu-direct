import logging

from sqlalchemy import select, update
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


class MessageNotFound(Exception):
    def __init__(self, _id: int):
        super().__init__(f"message not found: id={_id}")


# _message_pairs: dict[domain.MessageID, domain.MessageID] = dict()
# _message_tickets: dict[domain.MessageID, int] = dict()


class Storage:
    _db: AsyncSession

    def __init__(self, conn: AsyncSession):
        self._db = conn

    async def save_ticket(self, ticket: domain.Ticket) -> domain.TicketRecord:
        model = models.Ticket.from_domain(ticket)
        self._db.add(model)
        await self._db.commit()
        return model.to_domain()  # Возвращает обновлённую сущность.

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

    async def ticket(self, ticket_id: int) -> domain.Ticket:
        stmt = select(models.Ticket).filter_by(id=ticket_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise TicketNotFoundException(ticket_id)
        return model.to_domain()

    async def user(self, chat_id: int) -> domain.User:
        stmt = select(models.User).filter_by(chat_id=chat_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise UserNotFoundException(chat_id)
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
            raise MessageNotFound(_id)
        return model.to_domain()

    async def message_where(self, **kwargs) -> domain.Message:
        """
        Возвращает первое сообщение с данными полями.
        Вызывает исключение MessageNotFound, если сообщения не в БД.
        """
        stmt = \
            select(models.GroupMessage).    \
            filter_by(**kwargs)
        result = await self._db.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise MessageNotFound(0)
        return model.to_domain()

    # async def update_message(self, _id: int, **kwargs) -> domain.Message:
    #     stmt = select(models.GroupMessage).filter_by(_id=_id)
    #     result = await self._db.execute(stmt)
    #     model = result.scalar_one_or_none()
    #     if not model:
    #         raise MessageNotFound(_id)
    #     for key, value in kwargs.items():
    #         if not hasattr(models.GroupMessage, key):
    #             raise ValueError(f'Class `models.GroupMessage` doesn\'t have argument {key}')
    #     stmt = \
    #         update(models.GroupMessage).      \
    #         filter_by(_id=_id).    \
    #         values(**kwargs)
    #     await self._db.execute(stmt)
    #     await self._db.commit()
    #     return model.to_domain()

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

    async def chat_ticket_id(self, chat_id: int) -> int:
        stmt = \
            select(models.Ticket.id). \
            filter_by(owner_chat_id=chat_id)
        result = await self._db.execute(stmt)
        ticket_id = result.scalar_one_or_none()
        if not ticket_id:
            raise TicketNotFoundException(chat_id)
        return ticket_id
