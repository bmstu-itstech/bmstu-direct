from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from services.db.base import Base


class BaseCommon(Base):
    __abstract__ = True
    #
    id = Column(Integer, primary_key=True)
    # created_on = Column(DateTime, default=datetime.now)
    # updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    pass

class User(BaseCommon):
    __tablename__ = "users"

    tg_user_id = Column(BigInteger, primary_key=True)
    # tg_user_id: Mapped[int] = mapped_column()
    name = Column(Text)
    group = Column(Text)
    role = Column(Integer)

class Ticket(BaseCommon):
    __tablename__ = 'ticket'

    # id = Column(Integer)
    tg_user_id = Column(BigInteger, primary_key=True)
    tg_link = Column(Text)
    # text = Column(Text)
    # type = Column(Text)
    # category = Column(Text)
    # is_anonim = Column(Boolean)
    # is_closed = Column(Boolean)