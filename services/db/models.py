from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Text, Enum, Null, Boolean

from core.models.role import UserRole
from core.models.ticket import TicketType
from services.db.base import Base


class BaseCommon(Base):
    __abstract__ = True

    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Users(BaseCommon):
    __tablename__ = "users"

    tg_user_id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=True, default=Null)
    group = Column(Text, nullable=True, default=Null)
    role = Column(Enum(UserRole))


class Tickets(BaseCommon):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, nullable=False)
    tg_user_id = Column(BigInteger, nullable=False)
    tg_link = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    ticket_type = Column(Enum(TicketType))
    is_anonim = Column(Boolean, default=True, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)


class Category(BaseCommon):
    __tablename__ = 'tickets_category'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, nullable=False)
    category = Column(Text, nullable=False)