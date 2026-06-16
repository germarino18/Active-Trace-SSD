"""Tests for GuardiaRepository."""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.guardia import Guardia
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository
from app.repositories.guardia_repository import GuardiaRepository


@pytest.fixture
async def test_dictado(db_session: AsyncSession, test_tenant: Tenant) -> Dictado:
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session, tenant_id=test_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-GR", "nombre": "Guardia Repo"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session, tenant_id=test_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "GR", "nombre": "Test GR"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session, tenant_id=test_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id, "nombre": "2026-GR1", "anio": 2026,
        "vig_desde": date(2026, 3, 1),
    })
    dictado_repo = BaseRepository(
        model=Dictado, session=db_session, tenant_id=test_tenant.id
    )
    return await dictado_repo.create({
        "materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id,
    })


@pytest.fixture
async def test_asignacion(
    db_session: AsyncSession, test_tenant: Tenant, test_dictado: Dictado
):
    from app.models.user import User
    from app.models.usuario import Usuario
    from app.models.asignacion import Asignacion

    user_repo = BaseRepository(
        model=User, session=db_session, tenant_id=test_tenant.id
    )
    user = await user_repo.create({
        "email": "tutor-gr@test.com",
        "password_hash": "dummy",
        "display_name": "Tutor GR",
    })
    usuario_repo = BaseRepository(
        model=Usuario, session=db_session, tenant_id=test_tenant.id
    )
    usuario = await usuario_repo.create({
        "user_id": user.id, "nombre": "Tutor", "apellidos": "GR",
    })
    asig_repo = BaseRepository(
        model=Asignacion, session=db_session, tenant_id=test_tenant.id
    )
    return await asig_repo.create({
        "usuario_id": usuario.id, "rol": "TUTOR",
        "dictado_id": test_dictado.id, "desde": date(2026, 3, 1),
    })


@pytest.mark.asyncio
async def test_guardia_repo_create_and_find(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
    test_asignacion,
):
    """Test creating and finding a guardia."""
    repo = GuardiaRepository(session=db_session, tenant_id=test_tenant.id)
    guardia = await repo.create({
        "asignacion_id": test_asignacion.id,
        "dictado_id": test_dictado.id,
        "dia": "Lunes",
        "horario": "09:00–09:45",
    })
    found = await repo.find_by_id(guardia.id)
    assert found is not None
    assert found.id == guardia.id
    assert found.dia == "Lunes"


@pytest.mark.asyncio
async def test_guardia_repo_list_by_tenant(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
    test_asignacion,
):
    """Test listing guardias with filters."""
    repo = GuardiaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "asignacion_id": test_asignacion.id,
        "dictado_id": test_dictado.id,
        "dia": "Lunes",
        "horario": "09:00–09:45",
    })
    await repo.create({
        "asignacion_id": test_asignacion.id,
        "dictado_id": test_dictado.id,
        "dia": "Miércoles",
        "horario": "14:00–14:45",
    })

    all_items = await repo.list_by_tenant()
    assert len(all_items) == 2

    filtered = await repo.list_by_tenant(dia="Lunes")
    assert len(filtered) == 1
    assert filtered[0].dia == "Lunes"

    filtered2 = await repo.list_by_tenant(dictado_id=test_dictado.id)
    assert len(filtered2) == 2


@pytest.mark.asyncio
async def test_guardia_repo_list_by_asignacion(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
    test_asignacion,
):
    """Test listing guardias by asignacion."""
    repo = GuardiaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "asignacion_id": test_asignacion.id,
        "dictado_id": test_dictado.id,
        "dia": "Lunes",
        "horario": "09:00–09:45",
    })

    items = await repo.list_by_asignacion(test_asignacion.id)
    assert len(items) == 1
