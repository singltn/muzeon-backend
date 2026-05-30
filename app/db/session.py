from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO_DEBUG_LOG,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise

async def close_db() -> None:
    await engine.dispose()