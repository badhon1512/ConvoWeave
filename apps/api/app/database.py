from collections.abc import AsyncIterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings


@lru_cache
def _session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[AsyncSession]:
    factory = _session_factory(settings.database_url)
    async with factory() as session:
        yield session

