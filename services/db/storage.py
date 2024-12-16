import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import domain
from services.db import models

logger = logging.getLogger(__name__)


class TicketNotFoundException(Exception):
    def __init__(self, ticket_id: int | domain.MessageID):
        super().__init__(f"ticket not found: {ticket_id}")


class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"user not found: {user_id}")


class MessageNotFound(Exception):
    def __init__(self, _id: domain.MessageID):
        super().__init__(f"message not found: id={_id}")


_message_pairs: dict[domain.MessageID, domain.MessageID] = dict()
_message_tickets: dict[domain.MessageID, int] = dict()


class Storage:
    _db: AsyncSession

    def __init__(self, conn: AsyncSession):
        self._db = conn

    async def save_ticket(self, ticket: domain.Ticket) -> domain.TicketRecord:
        model = models.Ticket.from_domain(ticket)
        self._db.add(model)
        await self._db.commit()
        return model.to_domain()  # Возвращает обновлённую сущность.

    async def ticket(self, ticket_id: int) -> domain.Ticket:
        stmt = select(models.Ticket).where(models.Ticket.id==ticket_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise TicketNotFoundException(ticket_id)
        return model.to_domain()

    async def user(self, chat_id: int) -> domain.User:
        stmt = select(models.User).where(models.User.chat_id == chat_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise UserNotFoundException(chat_id)
        return model.to_domain()

    async def save_message_pair(self, pair: domain.MessagePair) -> None:
        model = models.MessagePair.from_domain(pair)
        self._db.add(model)
        await self._db.commit()

    async def paired_message_id(self, _id: domain.MessageID) -> domain.MessageID:
        """
        Возвращает спаренное сообщение с данным.
        Вызывает исключение MessageNotFound, если спаренного сообщения
        не в БД.
        """
        stmt = \
            select(models.MessagePair).\
            where(  # Поиск по двум _id: source_id и copy_id, то есть в обе стороны.
                models.MessagePair.source_chat_id == _id.chat_id and
                models.MessagePair.source_message_id == _id.message_id
                or
                models.MessagePair.copy_chat_id == _id.chat_id and
                models.MessagePair.copy_message_id == _id.message_id
            )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise MessageNotFound(_id)
        paired = model.to_domain()
        # Возвращаем противоположный ID в паре от переданного.
        return paired.source_id if paired.source_id != _id else paired.copy_id

    async def message_ticket_id(self, _id: domain.MessageID) -> int:
        print(_id)
        stmt = \
            select(models.MessagePair.ticket_id). \
            where(  # Поиск по двум _id: source_id и copy_id, то есть в обе стороны.
                models.MessagePair.source_chat_id == _id.chat_id and
                models.MessagePair.source_message_id == _id.message_id
                or
                models.MessagePair.copy_chat_id == _id.chat_id and
                models.MessagePair.copy_message_id == _id.message_id
            )
        result = await self._db.execute(stmt)
        print(result.scalars().all())
        ticket_id = result.scalar_one_or_none()
        if not ticket_id:
            raise TicketNotFoundException(_id)
        return ticket_id
