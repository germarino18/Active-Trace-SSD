import uuid
from datetime import UTC, datetime, timedelta

import pytest_asyncio
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository
from app.services.auth.password_service import PasswordService
from tests.helpers import seed_permissions_for_tenant

_FALLBACK_SECRET = "a" * 32


def make_token(user, secret: str = _FALLBACK_SECRET) -> str:
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
    return await _make_user(db_session, test_tenant.id, "admin@fechas.test", ["ADMIN"])


@pytest_asyncio.fixture
async def alumno_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "alumno@fechas.test", ["ALUMNO"])


@pytest_asyncio.fixture
async def another_tenant_admin(db_session: AsyncSession, another_tenant) -> User:
    await seed_permissions_for_tenant(db_session, another_tenant.id)
    return await _make_user(db_session, another_tenant.id, "admin@other.test", ["ADMIN"])


@pytest_asyncio.fixture
async def seeded_dictado(db_session: AsyncSession, test_tenant) -> uuid.UUID:
    """Create a minimal dictado for testing with all required entities."""
    tenant_id = test_tenant.id
    carrera_repo = CarreraRepository(session=db_session, tenant_id=tenant_id)
    materia_repo = MateriaRepository(session=db_session, tenant_id=tenant_id)
    cohorte_repo = CohorteRepository(session=db_session, tenant_id=tenant_id)
    dictado_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)

    carrera = await carrera_repo.create({
        "codigo": f"CAR-{uuid.uuid4().hex[:6]}",
        "nombre": "Test Carrera",
        "estado": "Activa",
    })
    materia = await materia_repo.create({
        "codigo": f"MAT-{uuid.uuid4().hex[:6]}",
        "nombre": "Test Materia",
        "estado": "Activa",
    })
    cohorte = await cohorte_repo.create({
        "carrera_id": carrera.id,
        "nombre": "2024",
        "anio": 2024,
    })
    dictado = await dictado_repo.create({
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "estado": "Activo",
    })
    return dictado.id
