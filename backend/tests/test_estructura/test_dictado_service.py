import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.exceptions import ValidationException
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import (
    CarreraCreate,
    CarreraUpdate,
    CohorteCreate,
    DictadoCreate,
    MateriaCreate,
    MateriaUpdate,
)
from app.services.estructura.carrera_service import CarreraService
from app.services.estructura.cohorte_service import CohorteService
from app.services.estructura.dictado_service import DictadoService
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


class _Fixtures:
    def __init__(self, db_session: AsyncSession, tenant_id):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self.carrera_repo = CarreraRepository(session=db_session, tenant_id=tenant_id)
        self.materia_repo = MateriaRepository(session=db_session, tenant_id=tenant_id)
        self.cohorte_repo = CohorteRepository(session=db_session, tenant_id=tenant_id)
        self.dictado_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
        self.audit_repo = AuditLogRepository(session=db_session, tenant_id=tenant_id)

        self.carrera_service = CarreraService(carrera_repo=self.carrera_repo, audit_repo=self.audit_repo)
        self.materia_service = MateriaService(materia_repo=self.materia_repo, audit_repo=self.audit_repo)
        self.cohorte_service = CohorteService(
            cohorte_repo=self.cohorte_repo, carrera_repo=self.carrera_repo, audit_repo=self.audit_repo
        )
        self.dictado_service = DictadoService(
            dictado_repo=self.dictado_repo,
            materia_repo=self.materia_repo,
            carrera_repo=self.carrera_repo,
            cohorte_repo=self.cohorte_repo,
            audit_repo=self.audit_repo,
        )


async def _setup(db_session: AsyncSession, test_tenant):
    actor = await _make_actor(db_session, test_tenant.id)
    current_user = CurrentUser(user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None)
    f = _Fixtures(db_session, test_tenant.id)

    carrera = await f.carrera_service.create(
        CarreraCreate(codigo="ING-INF", nombre="Ingeniería Informática"),
        current_user=current_user, request=_make_request(),
    )
    materia = await f.materia_service.create(
        MateriaCreate(codigo="MAT-101", nombre="Análisis Matemático I"),
        current_user=current_user, request=_make_request(),
    )
    cohorte = await f.cohorte_service.create(
        CohorteCreate(carrera_id=carrera.id, nombre="2024", anio=2024),
        current_user=current_user, request=_make_request(),
    )
    return f, current_user, carrera, materia, cohorte


# ── Alta consistente ─────────────────────────────────────────────────


async def test_create_dictado_consistent_succeeds(db_session: AsyncSession, test_tenant):
    f, current_user, carrera, materia, cohorte = await _setup(db_session, test_tenant)

    dictado = await f.dictado_service.create(
        DictadoCreate(materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id),
        current_user=current_user,
        request=_make_request(),
    )

    assert dictado.materia_id == materia.id
    assert dictado.carrera_id == carrera.id
    assert dictado.cohorte_id == cohorte.id
    assert dictado.estado == "Activo"


# ── Terna duplicada ──────────────────────────────────────────────────


async def test_create_dictado_with_duplicate_terna_rejected(db_session: AsyncSession, test_tenant):
    f, current_user, carrera, materia, cohorte = await _setup(db_session, test_tenant)

    await f.dictado_service.create(
        DictadoCreate(materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id),
        current_user=current_user,
        request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await f.dictado_service.create(
            DictadoCreate(materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id),
            current_user=current_user,
            request=_make_request(),
        )


# ── D2: inconsistencia carrera-cohorte rechazada ────────────────────────


async def test_create_dictado_with_carrera_cohorte_mismatch_rejected(
    db_session: AsyncSession, test_tenant
):
    f, current_user, carrera, materia, cohorte = await _setup(db_session, test_tenant)

    otra_carrera = await f.carrera_service.create(
        CarreraCreate(codigo="ING-SIS", nombre="Ingeniería en Sistemas"),
        current_user=current_user, request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await f.dictado_service.create(
            # cohorte pertenece a `carrera`, no a `otra_carrera`
            DictadoCreate(materia_id=materia.id, carrera_id=otra_carrera.id, cohorte_id=cohorte.id),
            current_user=current_user,
            request=_make_request(),
        )


# ── D5: dictado sobre entidad inactiva rechazado ────────────────────────


async def test_create_dictado_on_inactive_materia_rejected(db_session: AsyncSession, test_tenant):
    f, current_user, carrera, materia, cohorte = await _setup(db_session, test_tenant)

    await f.materia_service.update(
        materia.id, MateriaUpdate(estado="Inactiva"),
        current_user=current_user, request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await f.dictado_service.create(
            DictadoCreate(materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id),
            current_user=current_user,
            request=_make_request(),
        )


async def test_create_dictado_on_inactive_carrera_rejected(db_session: AsyncSession, test_tenant):
    f, current_user, carrera, materia, cohorte = await _setup(db_session, test_tenant)

    await f.carrera_service.update(
        carrera.id, CarreraUpdate(estado="Inactiva"),
        current_user=current_user, request=_make_request(),
    )

    with pytest.raises(ValidationException):
        await f.dictado_service.create(
            DictadoCreate(materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id),
            current_user=current_user,
            request=_make_request(),
        )
