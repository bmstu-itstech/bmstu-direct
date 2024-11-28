import enum
from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Text, Boolean, Enum, Sequence, BOOLEAN
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.sqltypes import NullType

from services.db.base import Base


class BaseCommon(Base):
    __abstract__ = True

    # id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    pass

"""
Енамы пока что нигде не используются, сделано на будущее.
"""
class Enum_types(enum.Enum):
    QUESTIONS = 'questions'
    PROBLEMS = 'problems'
    SUGGESTIONS = 'suggestions'

class Enum_category(enum.Enum):
    STUDY = 'food'
    HOSTEL = 'hostel'
    FOOD = 'food'
    MEDICINE = 'medicine'
    ARMY = 'army'
    ENTRY = 'entry'
    DOCUMENTS = 'documents'
    STIPEND = 'stipend'
    EXTRACURRICULAR_ACTIVITIES = 'extracurricular_activities'
    OTHER = 'other'


class User(BaseCommon):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=True, default=NullType)
    group = Column(Text, nullable=True, default=NullType)
    role = Column(Integer, default=0, nullable=False)

class Ticket(BaseCommon):
    __tablename__ = 'ticket'

    ticket_id = Column(Integer, Sequence('ticket_id', start=1, increment=1), primary_key=True)
    tg_user_id = Column(BigInteger, nullable=False)
    tg_link = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    is_anonim = Column(Text, default=1, nullable=False)
    is_closed = Column(Text, default=0, nullable=False)