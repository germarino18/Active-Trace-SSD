import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.exceptions import NotFoundException, ValidationException
from app.schemas.auth import CurrentUser
from app.schemas.fechas_academicas import FechaAcademicaCreate, FechaAcademicaUpdate
from app.services.fechas_academicas_service import FechasAcademicasService


def _make_request() -> Request:
    scope = {
        "type": "http",
        "client": ("203.0.113.5", 12345),
        "headers": [(b"user-agent", b"pytest-agent")],
    }
    return Request(scope)


def _make_current_user(user_id, tenant_id) -> CurrentUser:
    return CurrentUser(user_id=user_id, tenant_id=tenant_id, roles=["ADMIN"])


@pytest.mark.asyncio
async def test_create_fecha_succeeds(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.create_fecha(
        FechaAcademicaCreate(
            dictado_id=seeded_dictado,
            tipo="Parcial",
            numero=1,
            periodo="2026-1",
            fecha=datetime(2026, 4, 15, tzinfo=UTC),
            titulo="Primer Parcial",
        ),
        current_user=current_user,
        request=_make_request(),
    )

    assert result.titulo == "Primer Parcial"
    assert result.tipo == "Parcial"
    assert result.numero == 1
    assert result.periodo == "2026-1"


@pytest.mark.asyncio
async def test_create_fecha_duplicate_rejected(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    data = FechaAcademicaCreate(
        dictado_id=seeded_dictado,
        tipo="TP",
        numero=1,
        periodo="2026-1",
        fecha=datetime(2026, 5, 1, tzinfo=UTC),
        titulo="TP 1",
    )
    await service.create_fecha(data, current_user=current_user, request=_make_request())

    with pytest.raises(ValidationException) as exc:
        await service.create_fecha(data, current_user=current_user, request=_make_request())
    assert "Ya existe" in str(exc.value)


@pytest.mark.asyncio
async def test_update_fecha(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.create_fecha(
        FechaAcademicaCreate(
            dictado_id=seeded_dictado,
            tipo="Parcial", numero=1, periodo="2026-1",
            fecha=datetime(2026, 4, 15, tzinfo=UTC),
            titulo="Original",
        ),
        current_user=current_user, request=_make_request(),
    )

    updated = await service.update_fecha(
        result.id,
        FechaAcademicaUpdate(titulo="Actualizado"),
        current_user=current_user, request=_make_request(),
    )
    assert updated.titulo == "Actualizado"


@pytest.mark.asyncio
async def test_get_fecha(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.create_fecha(
        FechaAcademicaCreate(
            dictado_id=seeded_dictado,
            tipo="Coloquio", numero=1, periodo="2026-1",
            fecha=datetime(2026, 6, 1, tzinfo=UTC),
            titulo="Coloquio Final",
        ),
        current_user=current_user, request=_make_request(),
    )

    found = await service.get_fecha(result.id, current_user=current_user)
    assert found.id == result.id
    assert found.titulo == "Coloquio Final"


@pytest.mark.asyncio
async def test_get_fecha_not_found_raises(
    db_session: AsyncSession, test_tenant, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.get_fecha(uuid.uuid4(), current_user=current_user)


@pytest.mark.asyncio
async def test_list_fechas_returns_filtered(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    await service.create_fecha(
        FechaAcademicaCreate(dictado_id=seeded_dictado, tipo="Parcial", numero=1,
            periodo="2026-1", fecha=datetime(2026, 4, 15, tzinfo=UTC), titulo="P1"),
        current_user=current_user, request=_make_request(),
    )
    await service.create_fecha(
        FechaAcademicaCreate(dictado_id=seeded_dictado, tipo="Parcial", numero=2,
            periodo="2026-1", fecha=datetime(2026, 6, 15, tzinfo=UTC), titulo="P2"),
        current_user=current_user, request=_make_request(),
    )

    fechas = await service.list_fechas(seeded_dictado, "2026-1", 0, 100, current_user=current_user)
    assert len(fechas) == 2


@pytest.mark.asyncio
async def test_generate_lms_fragment_with_dates(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    await service.create_fecha(
        FechaAcademicaCreate(dictado_id=seeded_dictado, tipo="Parcial", numero=1,
            periodo="2026-1", fecha=datetime(2026, 4, 15, tzinfo=UTC), titulo="Primer Parcial"),
        current_user=current_user, request=_make_request(),
    )
    await service.create_fecha(
        FechaAcademicaCreate(dictado_id=seeded_dictado, tipo="TP", numero=1,
            periodo="2026-1", fecha=datetime(2026, 5, 1, tzinfo=UTC), titulo="TP 1"),
        current_user=current_user, request=_make_request(),
    )

    fragment = await service.generate_lms_fragment(
        seeded_dictado, "2026-1", current_user=current_user
    )
    assert "Cronograma de Evaluaciones" in fragment.contenido
    assert "Parcial" in fragment.contenido
    assert "Primer Parcial" in fragment.contenido
    assert "15/04/2026" in fragment.contenido
    assert "TP" in fragment.contenido


@pytest.mark.asyncio
async def test_generate_lms_fragment_no_dates_returns_message(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    fragment = await service.generate_lms_fragment(
        seeded_dictado, "2026-99", current_user=current_user
    )
    assert "No hay fechas académicas" in fragment.contenido


@pytest.mark.asyncio
async def test_delete_fecha_soft_delete(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    service = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.create_fecha(
        FechaAcademicaCreate(dictado_id=seeded_dictado, tipo="Recuperatorio", numero=1,
            periodo="2026-1", fecha=datetime(2026, 7, 1, tzinfo=UTC), titulo="Recu P1"),
        current_user=current_user, request=_make_request(),
    )

    await service.delete_fecha(result.id, current_user=current_user, request=_make_request())

    with pytest.raises(NotFoundException):
        await service.get_fecha(result.id, current_user=current_user)


@pytest.mark.asyncio
async def test_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant, seeded_dictado, admin_user
):
    service1 = FechasAcademicasService.create(db_session, test_tenant.id)
    current_user1 = _make_current_user(admin_user.id, test_tenant.id)

    result = await service1.create_fecha(
        FechaAcademicaCreate(dictado_id=seeded_dictado, tipo="Parcial", numero=1,
            periodo="2026-1", fecha=datetime(2026, 4, 15, tzinfo=UTC), titulo="P1"),
        current_user=current_user1, request=_make_request(),
    )

    service2 = FechasAcademicasService.create(db_session, another_tenant.id)
    current_user2 = _make_current_user(admin_user.id, another_tenant.id)
    with pytest.raises(NotFoundException):
        await service2.get_fecha(result.id, current_user=current_user2)
