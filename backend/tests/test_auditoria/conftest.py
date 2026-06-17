"""Fixtures for auditoria tests."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.audit_log import AuditLog
from app.models.asignacion import Asignacion
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
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


@pytest.fixture
async def auth_user_no_perm(db_session, test_tenant) -> CurrentUser:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"alumno-{uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Alumno",
        "is_active": True,
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Alumno",
        "apellidos": "Test",
    })
    return CurrentUser(
        user_id=user.id,
        tenant_id=test_tenant.id,
        roles=["ALUMNO"],
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
async def test_materia(db_session: AsyncSession, test_tenant: Tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "codigo": "MAT101",
        "nombre": "Matemáticas I",
    })


@pytest_asyncio.fixture
async def audit_log_entry(
    db_session: AsyncSession,
    test_tenant: Tenant,
    auth_admin: CurrentUser,
    test_materia: Materia,
) -> AuditLog:
    repo = BaseRepository(model=AuditLog, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "actor_id": auth_admin.user_id,
        "materia_id": test_materia.id,
        "accion": "CALIFICACIONES_IMPORTAR",
        "detalle": {"file": "notas.xlsx", "rows": 25},
        "filas_afectadas": 25,
        "ip": "127.0.0.1",
        "user_agent": "pytest",
    })


@pytest_asyncio.fixture
async def comunicacion_entry(
    db_session: AsyncSession,
    test_tenant: Tenant,
    auth_admin: CurrentUser,
    test_materia: Materia,
) -> Comunicacion:
    from app.models.comunicacion import ComunicacionEstado
    repo = BaseRepository(model=Comunicacion, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "enviado_por": auth_admin.user_id,
        "materia_id": test_materia.id,
        "asunto": "Recordatorio",
        "cuerpo": "Estimado alumno...",
        "destinatario": "alumno@test.com",
        "destinatario_hash": "abc123",
        "estado": ComunicacionEstado.ENVIADO.value,
        "lote_id": uuid4(),
    })


@pytest_asyncio.fixture
async def asignacion_coordinador(
    db_session: AsyncSession,
    test_tenant: Tenant,
    auth_admin: CurrentUser,
    test_materia: Materia,
) -> Asignacion:
    from datetime import date
    # Create Usuario for auth_admin first (seed_asignaciones helper)
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuarios = await usuario_repo.find_by(user_id=auth_admin.user_id)
    usuario = usuarios[0] if usuarios else await usuario_repo.create({
        "user_id": auth_admin.user_id,
        "nombre": "Admin",
        "apellidos": "Test",
    })
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "usuario_id": usuario.id,
        "rol": "COORDINADOR",
        "materia_id": test_materia.id,
        "desde": date(2026, 1, 1),
        "hasta": None,
    })
