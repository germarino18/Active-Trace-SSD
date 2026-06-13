import os
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from app.core.config import Settings
from app.core.database import Base, init_engine
from app.core.dependencies import get_db
from app.core.tenancy import TenantContext
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository

_TEST_SECRET_KEY = "a" * 32
_TEST_ENCRYPTION_KEY = "a" * 64


@pytest.fixture(scope="session", autouse=True)
def _test_security_env():
    """Make ad-hoc `TokenService()` / `get_encryption_key()` calls in tests
    agree with `app.state.settings` (used by the request-side dependencies).

    `TokenService()` falls back to `Settings()`, which reads `SECRET_KEY`
    from `.env`/os.environ (pydantic-settings env vars win over `.env`).
    `get_encryption_key()` reads `ENCRYPTION_KEY` directly from
    `os.environ`. Pinning both here keeps every code path -- app and
    test-constructed services alike -- using the same keys.
    """
    old_secret = os.environ.get("SECRET_KEY")
    old_encryption = os.environ.get("ENCRYPTION_KEY")
    os.environ["SECRET_KEY"] = _TEST_SECRET_KEY
    os.environ["ENCRYPTION_KEY"] = _TEST_ENCRYPTION_KEY
    yield
    if old_secret is None:
        os.environ.pop("SECRET_KEY", None)
    else:
        os.environ["SECRET_KEY"] = old_secret
    if old_encryption is None:
        os.environ.pop("ENCRYPTION_KEY", None)
    else:
        os.environ["ENCRYPTION_KEY"] = old_encryption


@pytest.fixture(scope="session")
def settings(_test_security_env) -> Settings:
    return Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/activia_trace",
        SECRET_KEY=_TEST_SECRET_KEY,
        ENCRYPTION_KEY=_TEST_ENCRYPTION_KEY,
        OTEL_ENABLED=False,
    )


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/activia_trace_test"


@pytest_asyncio.fixture(scope="session")
async def db_engine(test_db_url: str):
    engine = create_async_engine(test_db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Install the append-only trigger on audit_log (D2 / migration 004).
        # `create_all` builds the table from the ORM model but does not run
        # migration DDL, so the DB-level guard is installed here for tests.
        await conn.execute(
            text(
                """
                CREATE OR REPLACE FUNCTION audit_log_block_update_delete()
                RETURNS TRIGGER AS $$
                BEGIN
                    RAISE EXCEPTION 'audit_log is append-only: % is not permitted', TG_OP;
                END;
                $$ LANGUAGE plpgsql;
                """
            )
        )
        await conn.execute(
            text("DROP TRIGGER IF EXISTS trg_audit_log_block_update_delete ON audit_log")
        )
        await conn.execute(
            text(
                """
                CREATE TRIGGER trg_audit_log_block_update_delete
                BEFORE UPDATE OR DELETE ON audit_log
                FOR EACH ROW EXECUTE FUNCTION audit_log_block_update_delete();
                """
            )
        )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Per-test session bound to an external transaction with savepoints.

    Any `commit()` (issued by the test or by the app via the request
    session, see `client` fixture) operates on a SAVEPOINT nested inside
    the outer transaction. The outer transaction is rolled back at
    teardown, so nothing persists between tests regardless of who commits.
    """
    connection = await db_engine.connect()
    trans = await connection.begin()
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest_asyncio.fixture(autouse=True)
async def _reset_tenant_context():
    """Ensure TenantContext does not leak between tests."""
    TenantContext.reset()
    yield
    TenantContext.reset()


@pytest_asyncio.fixture(scope="session")
async def app(settings: Settings, test_db_url: str):
    from app.main import create_app
    application = create_app(settings)
    init_engine(test_db_url)
    yield application
    from app.core.database import close_engine
    await close_engine()


@pytest_asyncio.fixture
async def client(app, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client whose requests reuse the test's `db_session`.

    This makes data seeded by the test (even unflushed/uncommitted within
    the outer transaction) visible to the request, and vice versa, closing
    the isolation gap between the test's session and the app's per-request
    session.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)


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
