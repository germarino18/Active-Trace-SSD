import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.exceptions import ValidationException
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.materia_repository import MateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import MateriaCreate
from app.services.estructura.materia_service import MateriaService


def _make_request() -> Request:
    scope = {
        "type": "http",
        "client": ("203.0.113.5", 12345),
        "headers": [(b"user-agent", b"pytest-agent")],
    }
    return Request(scope)


async def _make_actor(db_session: AsyncSession, tenant_id) -> User:
    user = User(
        tenant_id=tenant_id,
        email=f"admin-{uuid.uuid4().hex[:8]}@test.edu",
        password_hash="hash",
        display_name="Admin Actor",
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


def _make_service(db_session: AsyncSession, tenant_id):
    materia_repo = MateriaRepository(session=db_session, tenant_id=tenant_id)
    audit_repo = AuditLogRepository(session=db_session, tenant_id=tenant_id)
    return MateriaService(materia_repo=materia_repo, audit_repo=audit_repo)


async def test_create_materia_persists_activa(db_session: AsyncSession, test_tenant):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    service = _make_service(db_session, test_tenant.id)

    materia = await service.create(
        MateriaCreate(codigo="MAT-101", nombre="Análisis Matemático I"),
        current_user=current_user,
        request=_make_request(),
    )

    assert materia.codigo == "MAT-101"
    assert materia.estado == "Activa"


async def test_create_materia_with_duplicate_codigo_rejected(db_session: AsyncSession, test_tenant):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    service = _make_service(db_session, test_tenant.id)

    await service.create(
        MateriaCreate(codigo="MAT-101", nombre="Análisis Matemático I"),
        current_user=current_user,
        request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await service.create(
            MateriaCreate(codigo="MAT-101", nombre="Otra materia"),
            current_user=current_user,
            request=_make_request(),
        )
