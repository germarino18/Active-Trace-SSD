"""Shared fixtures for `test_equipos` (C-08).

Mirrors `tests/test_usuarios/conftest.py` (C-07): real ephemeral test DB
(no DB mocks, regla dura #4), `test_tenant`/`another_tenant` from the root
conftest, `make_token` for router-level tests in group 4/5.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest_asyncio
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
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
    """Seed default roles/permissions (incl. equipos:asignar -> ADMIN)."""
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
    return await _make_user(db_session, test_tenant.id, "admin@equipos.test", ["ADMIN"])


@pytest_asyncio.fixture
async def alumno_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "alumno@equipos.test", ["ALUMNO"])


@pytest_asyncio.fixture
async def another_tenant_admin(db_session: AsyncSession, another_tenant) -> User:
    await seed_permissions_for_tenant(db_session, another_tenant.id)
    return await _make_user(db_session, another_tenant.id, "admin@othertenant-equipos.test", ["ADMIN"])


@pytest_asyncio.fixture
async def plain_user(db_session: AsyncSession, test_tenant) -> User:
    """A second auth identity with no `usuario` profile yet."""
    return await _make_user(db_session, test_tenant.id, "perfilable@equipos.test", [])


async def make_usuario_perfil(
    db_session: AsyncSession, tenant_id, user_id, nombre="Perfil", apellidos="Test"
) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await repo.create({"user_id": user_id, "nombre": nombre, "apellidos": apellidos})
