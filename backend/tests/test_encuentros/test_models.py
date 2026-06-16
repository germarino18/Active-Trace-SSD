"""Tests for SlotEncuentro and InstanciaEncuentro models."""

import uuid
from datetime import date, time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import DiaSemana, SlotEncuentro
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


@pytest.fixture
async def test_dictado(db_session: AsyncSession, test_tenant: Tenant) -> Dictado:
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-ENC", "nombre": "Encuentros Test"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "ENC", "nombre": "Test Encuentros"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id,
        "nombre": "2026-1",
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
async def test_create_slot_encuentro(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Test creating a SlotEncuentro with required fields."""
    repo = BaseRepository(
        model=SlotEncuentro, session=db_session, tenant_id=test_tenant.id
    )
    slot = await repo.create({
        "dictado_id": test_dictado.id,
        "titulo": "Clase 1",
        "hora": time(18, 0),
        "dia_semana": DiaSemana.LUNES.value,
        "fecha_inicio": date(2026, 3, 15),
        "cant_semanas": 14,
        "vig_desde": date(2026, 3, 1),
    })
    assert slot.id is not None
    assert slot.tenant_id == test_tenant.id
    assert slot.titulo == "Clase 1"
    assert slot.dia_semana == "Lunes"
    assert slot.cant_semanas == 14


@pytest.mark.asyncio
async def test_create_instancia_encuentro(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Test creating an InstanciaEncuentro."""
    repo = BaseRepository(
        model=InstanciaEncuentro, session=db_session, tenant_id=test_tenant.id
    )
    instancia = await repo.create({
        "dictado_id": test_dictado.id,
        "fecha": date(2026, 3, 15),
        "hora": time(18, 0),
        "titulo": "Clase 1",
        "estado": "Programado",
    })
    assert instancia.id is not None
    assert instancia.tenant_id == test_tenant.id
    assert instancia.estado == "Programado"
    assert instancia.video_url is None


@pytest.mark.asyncio
async def test_instancia_default_estado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Verify estado defaults to Programado."""
    repo = BaseRepository(
        model=InstanciaEncuentro, session=db_session, tenant_id=test_tenant.id
    )
    instancia = await repo.create({
        "dictado_id": test_dictado.id,
        "fecha": date(2026, 3, 22),
        "hora": time(18, 0),
        "titulo": "Clase 2",
    })
    assert instancia.estado == "Programado"


@pytest.mark.asyncio
async def test_slot_multi_tenant_isolation(
    db_session: AsyncSession,
    test_tenant: Tenant,
    another_tenant: Tenant,
    test_dictado: Dictado,
):
    """Verify slots from different tenants are isolated."""
    # Create a second dictado in another_tenant
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session,
        tenant_id=another_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-OTRO-ENC", "nombre": "Otra Materia"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session,
        tenant_id=another_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "OTRO-ENC", "nombre": "Otra Carrera"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session,
        tenant_id=another_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id,
        "nombre": "2026-2",
        "anio": 2026,
        "vig_desde": date(2026, 7, 1),
    })
    dictado_repo = BaseRepository(
        model=Dictado, session=db_session, tenant_id=another_tenant.id
    )
    otro_dictado = await dictado_repo.create({
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
    })

    repo1 = BaseRepository(
        model=SlotEncuentro, session=db_session, tenant_id=test_tenant.id
    )
    repo2 = BaseRepository(
        model=SlotEncuentro, session=db_session, tenant_id=another_tenant.id
    )

    await repo1.create({
        "dictado_id": test_dictado.id,
        "titulo": "T1 Slot",
        "hora": time(18, 0),
        "dia_semana": "Lunes",
        "fecha_inicio": date(2026, 3, 15),
        "cant_semanas": 1,
        "vig_desde": date(2026, 3, 1),
    })
    await repo2.create({
        "dictado_id": otro_dictado.id,
        "titulo": "T2 Slot",
        "hora": time(18, 0),
        "dia_semana": "Martes",
        "fecha_inicio": date(2026, 7, 5),
        "cant_semanas": 1,
        "vig_desde": date(2026, 7, 1),
    })

    t1_items = await repo1.find_all()
    t2_items = await repo2.find_all()

    assert len(t1_items) == 1
    assert len(t2_items) == 1
    assert t1_items[0].titulo == "T1 Slot"
    assert t2_items[0].titulo == "T2 Slot"
