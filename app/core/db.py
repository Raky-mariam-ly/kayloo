import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url,
                             echo=False,
                             pool_size=20,
                             max_overflow=10,
                             pool_pre_ping=True  # Check connection health before use
                             )
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
