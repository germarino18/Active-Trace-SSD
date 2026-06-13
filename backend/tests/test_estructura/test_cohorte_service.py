import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.exceptions import ValidationException
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import CarreraCreate, CohorteCreate
from app.services.estructura.carrera_service import CarreraService
from app.services.estructura.cohorte_service import CohorteService


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


def _make_carrera_service(db_session: AsyncSession, tenant_id):
    return CarreraService(
        carrera_repo=CarreraRepository(session=db_session, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db_session, tenant_id=tenant_id),
    )


def _make_cohorte_service(db_session: AsyncSession, tenant_id):
    return CohorteService(
        cohorte_repo=CohorteRepository(session=db_session, tenant_id=tenant_id),
        carrera_repo=CarreraRepository(session=db_session, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db_session, tenant_id=tenant_id),
    )


# ── Alta en carrera activa ───────────────────────────────────────────


async def test_create_cohorte_on_active_carrera_succeeds(db_session: AsyncSession, test_tenant):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    carrera_service = _make_carrera_service(db_session, test_tenant.id)
    cohorte_service = _make_cohorte_service(db_session, test_tenant.id)

    carrera = await carrera_service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )

    cohorte = await cohorte_service.create(
        CohorteCreate(carrera_id=carrera.id, nombre="2024", anio=2024),
        current_user=current_user,
        request=_make_request(),
    )

    assert cohorte.carrera_id == carrera.id
    assert cohorte.tenant_id == test_tenant.id
    assert cohorte.estado == "Activa"


# ── Unicidad ─────────────────────────────────────────────────────────


async def test_create_cohorte_with_duplicate_nombre_in_carrera_rejected(
    db_session: AsyncSession, test_tenant
):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    carrera_service = _make_carrera_service(db_session, test_tenant.id)
    cohorte_service = _make_cohorte_service(db_session, test_tenant.id)

    carrera = await carrera_service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )
    await cohorte_service.create(
        CohorteCreate(carrera_id=carrera.id, nombre="2024", anio=2024),
        current_user=current_user,
        request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await cohorte_service.create(
            CohorteCreate(carrera_id=carrera.id, nombre="2024", anio=2024),
            current_user=current_user,
            request=_make_request(),
        )


# ── D5: cohorte abierta sobre carrera inactiva rechazada ───────────────


async def test_create_open_cohorte_on_inactive_carrera_rejected(
    db_session: AsyncSession, test_tenant
):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    carrera_service = _make_carrera_service(db_session, test_tenant.id)
    cohorte_service = _make_cohorte_service(db_session, test_tenant.id)

    carrera = await carrera_service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )
    from app.schemas.estructura import CarreraUpdate
    await carrera_service.update(
        carrera.id,
        CarreraUpdate(estado="Inactiva"),
        current_user=current_user,
        request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await cohorte_service.create(
            CohorteCreate(carrera_id=carrera.id, nombre="2024", anio=2024, vig_hasta=None),
            current_user=current_user,
            request=_make_request(),
        )


async def test_create_closed_cohorte_on_inactive_carrera_succeeds(
    db_session: AsyncSession, test_tenant
):
    """Edge case: a cohorte with vig_hasta set (closed) is allowed even
    if the carrera is Inactiva — only OPEN cohortes are rejected (D5)."""
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    carrera_service = _make_carrera_service(db_session, test_tenant.id)
    cohorte_service = _make_cohorte_service(db_session, test_tenant.id)

    carrera = await carrera_service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user,
        request=_make_request(),
    )
    from app.schemas.estructura import CarreraUpdate
    await carrera_service.update(
        carrera.id,
        CarreraUpdate(estado="Inactiva"),
        current_user=current_user,
        request=_make_request(),
    )

    from datetime import date
    cohorte = await cohorte_service.create(
        CohorteCreate(
            carrera_id=carrera.id, nombre="2020", anio=2020,
            vig_desde=date(2020, 1, 1), vig_hasta=date(2020, 12, 31),
        ),
        current_user=current_user,
        request=_make_request(),
    )
    assert cohorte.nombre == "2020"
