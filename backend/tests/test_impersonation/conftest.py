import uuid
from datetime import UTC, datetime, timedelta

import pytest_asyncio
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth.password_service import PasswordService
from tests.helpers import seed_permissions_for_tenant

_FALLBACK_SECRET = "dev-secret-key-that-is-exactly-32-bytes!"


def make_token(user, actor_id=None, secret: str = _FALLBACK_SECRET) -> str:
    """Generate a test JWT access token matching TokenService fallback.

    If `actor_id` is provided, embeds it as the `actor_id` claim (impersonation session).
    """
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": user.roles,
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }
    if actor_id is not None:
        payload["actor_id"] = str(actor_id)
    return jwt.encode(payload, secret, algorithm="HS256")


async def _grant_impersonacion_usar_to_admin(db_session: AsyncSession, tenant_id):
    """Mirror migration 004's seed (permiso row) and additionally grant it to
    ADMIN via rol_permiso, since migration 004 only seeds the permiso
    catalog row, not a role assignment."""
    await db_session.execute(
        text("""
            INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
            VALUES (gen_random_uuid(), :tenant_id, 'impersonacion:usar', 'impersonacion:usar', NULL, 'impersonacion', now(), now())
            ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
        """),
        {"tenant_id": tenant_id},
    )
    await db_session.execute(
        text("""
            INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at)
            SELECT gen_random_uuid(), :tenant_id, r.id, p.id, false, now(), now()
            FROM rol r, permiso p
            WHERE r.tenant_id = :tenant_id AND r.codigo = 'ADMIN' AND r.deleted_at IS NULL
              AND p.tenant_id = :tenant_id AND p.codigo = 'impersonacion:usar' AND p.deleted_at IS NULL
            ON CONFLICT (tenant_id, rol_id, permiso_id) DO NOTHING
        """),
        {"tenant_id": tenant_id},
    )
    await db_session.flush()


@pytest_asyncio.fixture
async def seeded_tenant(db_session: AsyncSession, test_tenant):
    """Seed default permissions for the test_tenant, plus grant
    impersonacion:usar to ADMIN."""
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    await _grant_impersonacion_usar_to_admin(db_session, test_tenant.id)
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
    """ADMIN role, granted `impersonacion:usar` by the `seeded_tenant` fixture."""
    return await _make_user(db_session, test_tenant.id, "admin@test.edu", ["ADMIN"])


@pytest_asyncio.fixture
async def alumno_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "alumno@test.edu", ["ALUMNO"])


@pytest_asyncio.fixture
async def another_tenant_user(db_session: AsyncSession, another_tenant) -> User:
    return await _make_user(db_session, another_tenant.id, "cross-tenant@test.edu", ["ALUMNO"])
