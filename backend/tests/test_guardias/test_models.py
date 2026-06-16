"""Tests for Guardia model."""

from datetime import date, datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.guardia import Guardia
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


@pytest.fixture
async def test_dictado(db_session: AsyncSession, test_tenant: Tenant) -> Dictado:
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-GRD", "nombre": "Guardia Test"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "GRD", "nombre": "Test Guardia"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id,
        "nombre": "2026-G1",
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


@pytest.fixture
async def test_asignacion_guardia(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
):
    """Create a test asignacion for guardia tests."""
    from app.models.user import User
    from app.models.usuario import Usuario
    from app.models.asignacion import Asignacion

    user_repo = BaseRepository(
        model=User, session=db_session, tenant_id=test_tenant.id
    )
    user = await user_repo.create({
        "email": "tutor-guardia@test.com",
        "password_hash": "dummy",
        "display_name": "Tutor Guardia",
    })
    usuario_repo = BaseRepository(
        model=Usuario, session=db_session, tenant_id=test_tenant.id
    )
    usuario = await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Tutor",
        "apellidos": "Guardia",
    })
    asig_repo = BaseRepository(
        model=Asignacion, session=db_session, tenant_id=test_tenant.id
    )
    return await asig_repo.create({
        "usuario_id": usuario.id,
        "rol": "TUTOR",
        "dictado_id": test_dictado.id,
        "desde": date(2026, 3, 1),
    })


@pytest.mark.asyncio
async def test_create_guardia(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
    test_asignacion_guardia,
):
    """Test creating a Guardia with required fields."""
    repo = BaseRepository(
        model=Guardia, session=db_session, tenant_id=test_tenant.id
    )
    guardia = await repo.create({
        "asignacion_id": test_asignacion_guardia.id,
        "dictado_id": test_dictado.id,
        "dia": "Martes",
        "horario": "14:00–14:45",
    })
    assert guardia.id is not None
    assert guardia.tenant_id == test_tenant.id
    assert guardia.estado == "Pendiente"
    assert guardia.dia == "Martes"
    assert guardia.horario == "14:00–14:45"
    assert guardia.creada_at is not None


@pytest.mark.asyncio
async def test_guardia_default_estado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_dictado: Dictado,
    test_asignacion_guardia,
):
    """Verify estado defaults to Pendiente."""
    repo = BaseRepository(
        model=Guardia, session=db_session, tenant_id=test_tenant.id
    )
    guardia = await repo.create({
        "asignacion_id": test_asignacion_guardia.id,
        "dictado_id": test_dictado.id,
        "dia": "Miércoles",
        "horario": "15:00–15:45",
    })
    assert guardia.estado == "Pendiente"
