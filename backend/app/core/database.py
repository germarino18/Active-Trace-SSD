from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

engine = None
async_session_maker = None


class Base(DeclarativeBase):
    pass


def init_engine(database_url: str, **kwargs):
    global engine, async_session_maker
    engine = create_async_engine(database_url, **kwargs)
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return engine


async def close_engine():
    global engine, async_session_maker
    if engine is not None:
        await engine.dispose()
        engine = None
        async_session_maker = None
