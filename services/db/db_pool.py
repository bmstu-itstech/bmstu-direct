import logging

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from services.db.models import Base, BaseModel

logger = logging.getLogger(__name__)


async def create_db_pool(user, password, host, port, name, echo):
    engine = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}",
        echo=echo,
        future=True,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    return async_sessionmaker
