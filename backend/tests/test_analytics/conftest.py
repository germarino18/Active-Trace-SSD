"""Fixtures for analytics tests."""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


@pytest.fixture
async def auth_admin(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"admin-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Admin",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Admin",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["ADMIN"],
    )


@pytest.fixture(autouse=True)
async def _setup_auth_admin(app, db_session, test_tenant, auth_admin):
    async def _override_user():
        return auth_admin
    app.dependency_overrides[get_current_user] = _override_user
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    app.dependency_overrides.pop(get_current_user, None)
    cleanup_permission_cache()


@pytest_asyncio.fixture
async def test_carrera(db_session: AsyncSession, test_tenant: Tenant) -> Carrera:
    repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "codigo": "ING",
        "nombre": "Ingeniería",
    })


@pytest_asyncio.fixture
async def test_cohorte(db_session: AsyncSession, test_tenant: Tenant, test_carrera: Carrera) -> Cohorte:
    repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "carrera_id": test_carrera.id,
        "nombre": "2025",
        "anio": 2025,
    })


@pytest_asyncio.fixture
async def test_materia(db_session: AsyncSession, test_tenant: Tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "codigo": "MAT101",
        "nombre": "Matemáticas I",
    })


@pytest_asyncio.fixture
async def test_dictado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_materia: Materia,
    test_carrera: Carrera,
    test_cohorte: Cohorte,
) -> Dictado:
    repo = BaseRepository(model=Dictado, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "materia_id": test_materia.id,
        "carrera_id": test_carrera.id,
        "cohorte_id": test_cohorte.id,
        "estado": "Activo",
    })


@pytest_asyncio.fixture
async def test_version_padron(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
    auth_admin: CurrentUser,
) -> VersionPadron:
    repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "dictado_id": test_dictado.id,
        "cargado_por": auth_admin.user_id,
        "activa": True,
    })


@pytest_asyncio.fixture
async def test_entrada_padron(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_version_padron: VersionPadron,
) -> EntradaPadron:
    repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "version_id": test_version_padron.id,
        "nombre": "Juan",
        "apellidos": "Pérez",
        "comision": "A",
    })


@pytest_asyncio.fixture
async def test_entrada_padron_2(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_version_padron: VersionPadron,
) -> EntradaPadron:
    repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "version_id": test_version_padron.id,
        "nombre": "María",
        "apellidos": "García",
        "comision": "A",
    })
