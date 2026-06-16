import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.fecha_academica_repository import FechaAcademicaRepository


@pytest.fixture
def _create_repo(db_session, test_tenant):
    return FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)


@pytest.mark.asyncio
async def test_find_by_dictado_periodo_filters_correctly(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "Parcial", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 4, 15, tzinfo=UTC), "titulo": "Parcial 1",
    })
    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "TP", "numero": 1,
        "periodo": "2026-2", "fecha": datetime(2026, 8, 15, tzinfo=UTC), "titulo": "TP 1",
    })

    result_2026_1 = await repo.find_by_dictado_periodo(seeded_dictado, "2026-1")
    assert len(result_2026_1) == 1
    assert result_2026_1[0].periodo == "2026-1"

    result_2026_2 = await repo.find_by_dictado_periodo(seeded_dictado, "2026-2")
    assert len(result_2026_2) == 1

    result_all = await repo.find_by_dictado_periodo(seeded_dictado)
    assert len(result_all) == 2


@pytest.mark.asyncio
async def test_find_calendar_returns_all_dates(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "Parcial", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 4, 15, tzinfo=UTC), "titulo": "P1",
    })
    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "TP", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 5, 20, tzinfo=UTC), "titulo": "TP1",
    })

    result = await repo.find_calendar(seeded_dictado, "2026-1")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_find_calendar_without_period_returns_all(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "Parcial", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 4, 15, tzinfo=UTC), "titulo": "P1",
    })
    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "TP", "numero": 1,
        "periodo": "2026-2", "fecha": datetime(2026, 8, 20, tzinfo=UTC), "titulo": "TP1",
    })

    result = await repo.find_calendar(seeded_dictado)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_exists_by_dictado_tipo_numero_uniqueness(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)
    assert not await repo.exists_by_dictado_tipo_numero(seeded_dictado, "Parcial", 1)

    await repo.create({
        "dictado_id": seeded_dictado, "tipo": "Parcial", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 4, 15, tzinfo=UTC), "titulo": "P1",
    })
    assert await repo.exists_by_dictado_tipo_numero(seeded_dictado, "Parcial", 1)
    assert not await repo.exists_by_dictado_tipo_numero(seeded_dictado, "Parcial", 2)
    assert not await repo.exists_by_dictado_tipo_numero(seeded_dictado, "TP", 1)


@pytest.mark.asyncio
async def test_tenant_scoping(
    db_session: AsyncSession, test_tenant, another_tenant, seeded_dictado
):
    repo1 = FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo1.create({
        "dictado_id": seeded_dictado, "tipo": "Parcial", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 4, 15, tzinfo=UTC), "titulo": "P1",
    })

    repo2 = FechaAcademicaRepository(session=db_session, tenant_id=another_tenant.id)
    result = await repo2.find_by_dictado_periodo(seeded_dictado, "2026-1")
    assert len(result) == 0


@pytest.mark.asyncio
async def test_soft_delete_hides_records(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = FechaAcademicaRepository(session=db_session, tenant_id=test_tenant.id)
    fecha = await repo.create({
        "dictado_id": seeded_dictado, "tipo": "Parcial", "numero": 1,
        "periodo": "2026-1", "fecha": datetime(2026, 4, 15, tzinfo=UTC), "titulo": "P1",
    })

    await repo.soft_delete(fecha.id)
    result = await repo.find_by_dictado_periodo(seeded_dictado, "2026-1")
    assert len(result) == 0
