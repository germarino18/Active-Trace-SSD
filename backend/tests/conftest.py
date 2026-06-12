from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from app.core.config import Settings
from app.core.database import Base, init_engine
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/activia_trace",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="a" * 64,
        OTEL_ENABLED=False,
    )


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/activia_trace_test"


@pytest_asyncio.fixture(scope="session")
async def db_engine(test_db_url: str):
    engine = create_async_engine(test_db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    session = AsyncSession(db_engine, expire_on_commit=False)
    yield session
    await session.rollback()
    await session.close()


@pytest_asyncio.fixture(scope="session")
async def app(settings: Settings, test_db_url: str):
    from app.main import create_app
    application = create_app(settings)
    init_engine(test_db_url)
    yield application
    from app.core.database import close_engine
    await close_engine()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    repo = BaseRepository(model=Tenant, session=db_session)
    return await repo.create(
        {
            "name": "Test University",
            "slug": f"test-university-{uuid4().hex[:8]}",
        }
    )


@pytest_asyncio.fixture
async def another_tenant(db_session: AsyncSession) -> Tenant:
    repo = BaseRepository(model=Tenant, session=db_session)
    return await repo.create(
        {
            "name": "Another University",
            "slug": f"another-university-{uuid4().hex[:8]}",
        }
    )
