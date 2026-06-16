"""Override DB‑bound fixtures so pure‑function tests can run without PostgreSQL."""

import pytest


@pytest.fixture(scope="session")
def test_db_url() -> str | None:
    return None


@pytest.fixture(scope="session")
async def db_engine():
    return None


@pytest.fixture(scope="session")
async def db_session_factory():
    return None


@pytest.fixture
async def db_session():
    return None


@pytest.fixture
async def client():
    from unittest.mock import AsyncMock
    return AsyncMock()
