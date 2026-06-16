"""Shared fixtures for `test_coloquios` (C-14).

Mirrors `tests/test_encuentros/conftest.py` pattern: real ephemeral test DB,
`test_tenant` from root conftest, `make_token` for router-level tests.
Plus helpers for creating dictado + evaluacion rows needed by all tests.
"""

import uuid
from datetime import UTC, datetime, timedelta, date

import pytest_asyncio
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
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
    """Seed default roles/permissions (incl. coloquios:*)."""
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

    # Create matching Usuario row so that user.id == usuario.id.
    # The evaluation tables FK to usuario.id, but the service code
    # uses current_user.user_id (which is user.id). Making them
    # equal avoids the mismatch.
    usuario = Usuario(
        id=user.id,
        user_id=user.id,
        tenant_id=tenant_id,
        nombre=email.split("@")[0],
        apellidos="Test",
        estado="Activo",
        facturador=False,
    )
    db_session.add(usuario)
    await db_session.flush()

    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "admin@coloquios.test", ["ADMIN"])


@pytest_asyncio.fixture
async def coordinador_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(
        db_session, test_tenant.id, "coordinador@coloquios.test", ["COORDINADOR"]
    )


@pytest_asyncio.fixture
async def profesor_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(
        db_session, test_tenant.id, "profesor@coloquios.test", ["PROFESOR"]
    )


@pytest_asyncio.fixture
async def alumno_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(db_session, test_tenant.id, "alumno@coloquios.test", ["ALUMNO"])


@pytest_asyncio.fixture
async def otro_alumno_user(db_session: AsyncSession, test_tenant) -> User:
    return await _make_user(
        db_session, test_tenant.id, "alumno2@coloquios.test", ["ALUMNO"]
    )


async def _make_usuario_perfil(
    db_session: AsyncSession, tenant_id, user_id, nombre="Perfil", apellidos="Test"
) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await repo.create({"user_id": user_id, "nombre": nombre, "apellidos": apellidos})


async def _make_dictado(
    db_session: AsyncSession, tenant_id, codigo_suffix="COL"
) -> Dictado:
    """Helper: create materia + carrera + cohorte + dictado in one call."""
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session,
        tenant_id=tenant_id,
    )
    materia = await materias_repo.create(
        {"codigo": f"MAT-{codigo_suffix}", "nombre": f"Materia {codigo_suffix}"}
    )
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session,
        tenant_id=tenant_id,
    )
    carrera = await carreras_repo.create(
        {"codigo": f"CAR-{codigo_suffix}", "nombre": f"Carrera {codigo_suffix}"}
    )
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session,
        tenant_id=tenant_id,
    )
    cohorte = await cohortes_repo.create(
        {
            "carrera_id": carrera.id,
            "nombre": f"2026-{codigo_suffix}",
            "anio": 2026,
            "vig_desde": date(2026, 3, 1),
        }
    )
    dictado_repo = BaseRepository(
        model=Dictado, session=db_session, tenant_id=tenant_id
    )
    return await dictado_repo.create(
        {
            "materia_id": materia.id,
            "carrera_id": carrera.id,
            "cohorte_id": cohorte.id,
        }
    )


@pytest_asyncio.fixture
async def dictado_valido(
    db_session: AsyncSession, test_tenant
) -> Dictado:
    """A dictado belonging to `test_tenant`."""
    return await _make_dictado(db_session, test_tenant.id, "COL-T1")


@pytest_asyncio.fixture
async def evaluacion_valida(
    db_session: AsyncSession, test_tenant, dictado_valido
):
    """A minimal Evaluacion row for reuse across tests."""
    from app.models.evaluacion import Evaluacion

    repo = BaseRepository(
        model=Evaluacion, session=db_session, tenant_id=test_tenant.id
    )
    return await repo.create(
        {
            "dictado_id": dictado_valido.id,
            "tipo": "Coloquio",
            "instancia": "Coloquio Final",
            "dias_disponibles": 10,
            "cupo_maximo": 30,
            "estado": "Activa",
        }
    )
