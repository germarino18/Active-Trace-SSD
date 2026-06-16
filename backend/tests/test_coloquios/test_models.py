"""Tests for Evaluacion, ReservaEvaluacion, ResultadoEvaluacion and AlumnoConvocado models."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alumno_convocado import AlumnoConvocado
from app.models.evaluacion import Evaluacion
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


# ── Evaluacion ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_evaluacion(
    db_session: AsyncSession,
    test_tenant: Tenant,
    dictado_valido,
):
    """Test creating an Evaluacion with required fields."""
    repo = BaseRepository(
        model=Evaluacion, session=db_session, tenant_id=test_tenant.id
    )
    evaluacion = await repo.create({
        "dictado_id": dictado_valido.id,
        "tipo": "Coloquio",
        "instancia": "Coloquio Final Diciembre",
        "dias_disponibles": 15,
        "cupo_maximo": 25,
        "estado": "Activa",
    })
    assert evaluacion.id is not None
    assert evaluacion.tenant_id == test_tenant.id
    assert evaluacion.tipo == "Coloquio"
    assert evaluacion.instancia == "Coloquio Final Diciembre"
    assert evaluacion.cupo_maximo == 25
    assert evaluacion.estado == "Activa"


@pytest.mark.asyncio
async def test_evaluacion_default_dias_disponibles(
    db_session: AsyncSession,
    test_tenant: Tenant,
    dictado_valido,
):
    """Verify dias_disponibles defaults to 10."""
    repo = BaseRepository(
        model=Evaluacion, session=db_session, tenant_id=test_tenant.id
    )
    evaluacion = await repo.create({
        "dictado_id": dictado_valido.id,
        "tipo": "TP",
        "instancia": "TP 1",
        "cupo_maximo": 30,
    })
    assert evaluacion.dias_disponibles == 10


@pytest.mark.asyncio
async def test_evaluacion_multi_tenant_isolation(
    db_session: AsyncSession,
    test_tenant: Tenant,
    another_tenant: Tenant,
    dictado_valido,
):
    """Verify evaluaciones from different tenants are isolated."""
    # Create second tenant's dictado
    from tests.test_coloquios.conftest import _make_dictado

    otro_dictado = await _make_dictado(db_session, another_tenant.id, "COL-T2")

    repo1 = BaseRepository(
        model=Evaluacion, session=db_session, tenant_id=test_tenant.id
    )
    repo2 = BaseRepository(
        model=Evaluacion, session=db_session, tenant_id=another_tenant.id
    )

    await repo1.create({
        "dictado_id": dictado_valido.id,
        "tipo": "Coloquio",
        "instancia": "T1 Coloquio",
        "cupo_maximo": 30,
    })
    await repo2.create({
        "dictado_id": otro_dictado.id,
        "tipo": "Parcial",
        "instancia": "T2 Parcial",
        "cupo_maximo": 20,
    })

    t1_items = await repo1.find_all()
    t2_items = await repo2.find_all()

    assert len(t1_items) == 1
    assert len(t2_items) == 1
    assert t1_items[0].instancia == "T1 Coloquio"
    assert t2_items[0].instancia == "T2 Parcial"


# ── ReservaEvaluacion ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_reserva(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test creating a ReservaEvaluacion."""
    repo = BaseRepository(
        model=ReservaEvaluacion, session=db_session, tenant_id=test_tenant.id
    )
    reserva = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "estado": "Activa",
    })
    assert reserva.id is not None
    assert reserva.tenant_id == test_tenant.id
    assert reserva.estado == "Activa"
    assert reserva.fecha_hora is not None


@pytest.mark.asyncio
async def test_reserva_default_estado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Verify estado defaults to Activa."""
    repo = BaseRepository(
        model=ReservaEvaluacion, session=db_session, tenant_id=test_tenant.id
    )
    reserva = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
    })
    assert reserva.estado == "Activa"


# ── ResultadoEvaluacion ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_resultado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test creating a ResultadoEvaluacion."""
    repo = BaseRepository(
        model=ResultadoEvaluacion, session=db_session, tenant_id=test_tenant.id
    )
    resultado = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "nota_final": "Aprobado (8)",
    })
    assert resultado.id is not None
    assert resultado.tenant_id == test_tenant.id
    assert resultado.nota_final == "Aprobado (8)"


# ── AlumnoConvocado ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_alumno_convocado(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test creating an AlumnoConvocado entry."""
    repo = BaseRepository(
        model=AlumnoConvocado, session=db_session, tenant_id=test_tenant.id
    )
    ac = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
    })
    assert ac.id is not None
    assert ac.tenant_id == test_tenant.id


@pytest.mark.asyncio
async def test_alumno_convocado_unique_constraint(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Verifies unique constraint on (evaluacion_id, alumno_id)."""
    repo = BaseRepository(
        model=AlumnoConvocado, session=db_session, tenant_id=test_tenant.id
    )
    await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
    })
    with pytest.raises(Exception):  # IntegrityError from the DB
        await repo.create({
            "evaluacion_id": evaluacion_valida.id,
            "alumno_id": alumno_user.id,
        })
