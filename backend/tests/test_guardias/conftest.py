"""Shared fixtures for `test_guardias` (C-13).

Mirrors `tests/test_equipos/conftest.py` pattern: real ephemeral test DB,
`test_tenant` from root conftest, `make_token` for router-level tests.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest_asyncio
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth.password_service import PasswordService
from tests.helpers import seed_permissions_for_tenant

_FALLBACK_SECRET = "a" * 32


def make_token(user, secret: str = _FALLBACK_SECRET) -> str:
    """Generate a test JWT access token matching TokenService fallback."""
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": user.roles,
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest_asyncio.fixture
async def seeded_tenant(db_session: AsyncSession, test_tenant):
    """Seed default roles/permissions (incl. encuentros:gestionar)."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    return test_tenant


async def _make_user(db_session, tenant_id, email, roles):
    pw = PasswordService()
    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=pw.hash_password("Password123!"),
        display_name=email,
        roles=roles,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "admin@guardias.test", ["ADMIN"])


@pytest_asyncio.fixture
async def tutor_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "tutor@guardias.test", ["TUTOR"])


@pytest_asyncio.fixture
async def alumno_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "alumno@guardias.test", ["ALUMNO"])
