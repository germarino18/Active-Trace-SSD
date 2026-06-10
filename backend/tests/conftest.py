from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from app.core.config import Settings
from app.core.database import Base, init_engine


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/activia_trace",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="b" * 32,
        OTEL_ENABLED=False,
    )


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return "postgresql+asyncpg://postgres:postgres@localhost:5433/activia_trace_test"


@pytest_asyncio.fixture(scope="session")
async def db_engine(test_db_url: str):
    engine = create_async_engine(test_db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await db_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture(scope="session")
async def app(settings: Settings):
    from app.main import create_app
    application = create_app(settings)
    init_engine(settings.database_url)
    yield application
    from app.core.database import close_engine
    await close_engine()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
