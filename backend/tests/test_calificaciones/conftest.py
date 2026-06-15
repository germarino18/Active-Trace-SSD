import os

import pytest


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/activia_trace_test",
    )
