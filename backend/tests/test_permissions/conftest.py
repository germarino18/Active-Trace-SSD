import uuid
from datetime import UTC, datetime, timedelta

import pytest_asyncio
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth.password_service import PasswordService
from tests.helpers import seed_permissions_for_tenant


@pytest_asyncio.fixture
async def seeded_tenant(db_session: AsyncSession, test_tenant):
    """Seed default permissions for the test_tenant."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    return test_tenant


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession, test_tenant) -> User:
    """Create an admin test user with ADMIN role."""
    pw = PasswordService()
    user = User(
        tenant_id=test_tenant.id,
        email="admin@test.edu",
        password_hash=pw.hash_password("Admin123!"),
        display_name="Admin User",
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def profesor_user(db_session: AsyncSession, test_tenant) -> User:
    """Create a profesor test user with PROFESOR role."""
    pw = PasswordService()
    user = User(
        tenant_id=test_tenant.id,
        email="profesor@test.edu",
        password_hash=pw.hash_password("Prof123!"),
        display_name="Profesor User",
        roles=["PROFESOR"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def alumno_user(db_session: AsyncSession, test_tenant) -> User:
    """Create an alumno test user with ALUMNO role."""
    pw = PasswordService()
    user = User(
        tenant_id=test_tenant.id,
        email="alumno@test.edu",
        password_hash=pw.hash_password("Alumno123!"),
        display_name="Alumno User",
        roles=["ALUMNO"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


# This must match the test settings fixture's SECRET_KEY (tests/conftest.py)
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
