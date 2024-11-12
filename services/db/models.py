from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime

from services.db.base import Base


class BaseCommon(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseCommon):
    __tablename__ = "users"

    telegram_id = Column(BigInteger)
