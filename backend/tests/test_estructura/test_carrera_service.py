import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import CarreraCreate, CarreraUpdate
from app.services.estructura.carrera_service import CarreraService


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
    carrera_repo = CarreraRepository(session=db_session, tenant_id=tenant_id)
    audit_repo = AuditLogRepository(session=db_session, tenant_id=tenant_id)
    return CarreraService(carrera_repo=carrera_repo, audit_repo=audit_repo)


async def _current_user(actor: User, tenant_id) -> CurrentUser:
    return CurrentUser(user_id=actor.id, tenant_id=tenant_id, roles=["ADMIN"], actor_id=None)


# ── Alta ─────────────────────────────────────────────────────────────


async def test_create_carrera_persists_activa_and_audits(
    db_session: AsyncSession, test_tenant
):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = await _current_user(actor, test_tenant.id)
    service = _make_service(db_session, test_tenant.id)

    carrera = await service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )

    assert carrera.codigo == "ING-INF"
    assert carrera.estado == "Activa"
    assert carrera.tenant_id == test_tenant.id

    await db_session.commit()
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.tenant_id == test_tenant.id,
            AuditLog.accion == AccionAuditoria.CARRERA_CREAR,
        )
    )
    records = list(result.unique().scalars().all())
    assert len(records) == 1
    assert records[0].actor_id == actor.id


# ── Unicidad ─────────────────────────────────────────────────────────


async def test_create_carrera_with_duplicate_codigo_rejected(
    db_session: AsyncSession, test_tenant
):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = await _current_user(actor, test_tenant.id)
    service = _make_service(db_session, test_tenant.id)

    await service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await service.create(
            CarreraCreate(codigo="ING-INF", nombre="Otra carrera"),
            current_user=current_user,
            request=_make_request(),
        )


async def test_create_carrera_reuses_codigo_after_soft_delete(
    db_session: AsyncSession, test_tenant
):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = await _current_user(actor, test_tenant.id)
    service = _make_service(db_session, test_tenant.id)

    carrera = await service.create(
        CarreraCreate(codigo="ING-SIS", nombre="Ingeniería en Sistemas"),
        current_user=current_user,
        request=_make_request(),
    )
    await service.soft_delete(carrera.id, current_user=current_user, request=_make_request())

    recreated = await service.create(
        CarreraCreate(codigo="ING-SIS", nombre="Ingeniería en Sistemas v2"),
        current_user=current_user,
        request=_make_request(),
    )
    assert recreated.codigo == "ING-SIS"
    assert recreated.id != carrera.id


# ── Cambio de estado ───────────────────────────────────────────────────


async def test_update_carrera_estado_to_inactiva(
    db_session: AsyncSession, test_tenant
):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = await _current_user(actor, test_tenant.id)
    service = _make_service(db_session, test_tenant.id)

    carrera = await service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )

    updated = await service.update(
        carrera.id,
        CarreraUpdate(estado="Inactiva"),
        current_user=current_user,
        request=_make_request(),
    )

    assert updated.estado == "Inactiva"
    assert updated.deleted_at is None
