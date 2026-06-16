"""Tests for SlotEncuentroRepository and InstanciaEncuentroRepository."""

import uuid
from datetime import date, time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository
from app.repositories.encuentro_repository import (
    InstanciaEncuentroRepository,
    SlotEncuentroRepository,
)


@pytest.fixture
async def test_dictado(db_session: AsyncSession, test_tenant: Tenant) -> Dictado:
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-REPO", "nombre": "Repo Test"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "REPO", "nombre": "Test Repo"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id,
        "nombre": "2026-R1",
        "anio": 2026,
        "vig_desde": date(2026, 3, 1),
    })
    dictado_repo = BaseRepository(
        model=Dictado, session=db_session, tenant_id=test_tenant.id
    )
    return await dictado_repo.create({
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
    })


@pytest.mark.asyncio
async def test_slot_repo_create_and_find(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Test creating and finding a slot by ID."""
    repo = SlotEncuentroRepository(session=db_session, tenant_id=test_tenant.id)
    slot = await repo.create({
        "dictado_id": test_dictado.id,
        "titulo": "Slot Repo Test",
        "hora": time(18, 0),
        "dia_semana": "Lunes",
        "fecha_inicio": date(2026, 3, 15),
        "cant_semanas": 10,
        "vig_desde": date(2026, 3, 1),
    })
    found = await repo.find_by_id(slot.id)
    assert found is not None
    assert found.id == slot.id
    assert found.titulo == "Slot Repo Test"


@pytest.mark.asyncio
async def test_slot_repo_list_by_dictado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Test listing slots by dictado."""
    repo = SlotEncuentroRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "dictado_id": test_dictado.id,
        "titulo": "Slot 1",
        "hora": time(18, 0),
        "dia_semana": "Lunes",
        "fecha_inicio": date(2026, 3, 15),
        "cant_semanas": 5,
        "vig_desde": date(2026, 3, 1),
    })
    await repo.create({
        "dictado_id": test_dictado.id,
        "titulo": "Slot 2",
        "hora": time(19, 0),
        "dia_semana": "Miércoles",
        "fecha_inicio": date(2026, 3, 17),
        "cant_semanas": 5,
        "vig_desde": date(2026, 3, 1),
    })
    slots = await repo.list_by_dictado(test_dictado.id)
    assert len(slots) == 2


@pytest.mark.asyncio
async def test_instancia_repo_bulk_create(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Test bulk creation of instances."""
    repo = InstanciaEncuentroRepository(session=db_session, tenant_id=test_tenant.id)
    slot_repo = SlotEncuentroRepository(session=db_session, tenant_id=test_tenant.id)
    slot = await slot_repo.create({
        "dictado_id": test_dictado.id,
        "titulo": "Bulk Slot",
        "hora": time(18, 0),
        "dia_semana": "Lunes",
        "fecha_inicio": date(2026, 3, 15),
        "cant_semanas": 3,
        "vig_desde": date(2026, 3, 1),
    })

    instances = await repo.bulk_create([
        {
            "slot_id": slot.id,
            "dictado_id": test_dictado.id,
            "fecha": date(2026, 3, 15),
            "hora": time(18, 0),
            "titulo": "Semana 1",
            "estado": "Programado",
            "tenant_id": test_tenant.id,
        },
        {
            "slot_id": slot.id,
            "dictado_id": test_dictado.id,
            "fecha": date(2026, 3, 22),
            "hora": time(18, 0),
            "titulo": "Semana 2",
            "estado": "Programado",
            "tenant_id": test_tenant.id,
        },
        {
            "slot_id": slot.id,
            "dictado_id": test_dictado.id,
            "fecha": date(2026, 3, 29),
            "hora": time(18, 0),
            "titulo": "Semana 3",
            "estado": "Programado",
            "tenant_id": test_tenant.id,
        },
    ])
    assert len(instances) == 3
    assert instances[0].tenant_id == test_tenant.id


@pytest.mark.asyncio
async def test_instancia_repo_list_by_dictado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Test listing instances by dictado."""
    repo = InstanciaEncuentroRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "dictado_id": test_dictado.id,
        "fecha": date(2026, 3, 15),
        "hora": time(18, 0),
        "titulo": "Instancia 1",
        "estado": "Programado",
    })
    await repo.create({
        "dictado_id": test_dictado.id,
        "fecha": date(2026, 3, 22),
        "hora": time(18, 0),
        "titulo": "Instancia 2",
        "estado": "Realizado",
    })
    items = await repo.list_by_dictado(test_dictado.id)
    assert len(items) == 2
