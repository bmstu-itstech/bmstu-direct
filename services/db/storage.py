import logging

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core import domain
from services.db import models

logger = logging.getLogger(__name__)


class ModelNotFoundException(Exception):
    def __init__(self, model: type, model_id: int):
        super().__init__(f"{model.__name__} not found: id={model_id}")


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
            raise ModelNotFoundException(models.Ticket, ticket_id)
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

    async def save_user(self, user: domain.User) -> domain.User:
        model = models.User.from_domain(user)
        self._db.add(model)
        await self._db.commit()
        return model.to_domain()

    async def user(self, chat_id: int) -> domain.User:
        stmt = select(models.User).filter_by(chat_id=chat_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ModelNotFoundException(models.User, chat_id)
        return model.to_domain()

    async def users_where(self, **kwargs) -> list[domain.User]:
        stmt = select(models.User).filter_by(**kwargs)
        result = await self._db.execute(stmt)
        db_models = result.scalars().all()
        return [model.to_domain() for model in db_models]

    async def update_user(self, chat_id: int, **kwargs) -> domain.User:
        stmt = select(models.User).filter_by(chat_id=chat_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ModelNotFoundException(models.User, chat_id)
        for key, value in kwargs.items():
            if not hasattr(models.User, key):
                raise ValueError(f'Class `models.User` doesn\'t have argument {key}')
        stmt = \
            update(models.User).      \
            filter_by(chat_id=chat_id).    \
            values(**kwargs)
        await self._db.execute(stmt)
        await self._db.commit()
        return model.to_domain()

    async def ticket(self, ticket_id: int) -> domain.TicketRecord:
        stmt = select(models.Ticket).filter_by(id=ticket_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ModelNotFoundException(models.Ticket, ticket_id)
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
            raise ModelNotFoundException(models.GroupMessage, _id)
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
            raise ModelNotFoundException(models.GroupMessage, 0)
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
            raise ModelNotFoundException(models.Ticket, _id)
        return ticket_id

    async def chat_ticket_ids(self, chat_id: int) -> list[int]:
        stmt = \
            select(models.Ticket.id). \
            filter_by(owner_chat_id=chat_id)
        result = await self._db.execute(stmt)
        ticket_ids = list(result.scalars().all())
        if not ticket_ids:
            raise ModelNotFoundException(models.Ticket, chat_id)
        return ticket_ids
