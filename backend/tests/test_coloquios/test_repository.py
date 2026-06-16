"""Tests for EvaluacionRepository, ReservaEvaluacionRepository,
ResultadoEvaluacionRepository and AlumnoConvocadoRepository."""

import uuid
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.tenant import Tenant
from app.repositories.alumno_convocado_repository import (
    AlumnoConvocadoRepository,
)
from app.repositories.base import BaseRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.reserva_evaluacion_repository import (
    ReservaEvaluacionRepository,
)
from app.repositories.resultado_evaluacion_repository import (
    ResultadoEvaluacionRepository,
)
from tests.test_coloquios.conftest import _make_dictado


# ── EvaluacionRepository ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_evaluacion_repo_create_and_find(
    db_session: AsyncSession,
    test_tenant: Tenant,
    dictado_valido,
):
    """Test creating and finding an evaluacion by ID."""
    repo = EvaluacionRepository(session=db_session, tenant_id=test_tenant.id)
    ev = await repo.create({
        "dictado_id": dictado_valido.id,
        "tipo": "Coloquio",
        "instancia": "Repo Test",
        "cupo_maximo": 25,
    })
    found = await repo.find_by_id(ev.id)
    assert found is not None
    assert found.id == ev.id
    assert found.instancia == "Repo Test"


@pytest.mark.asyncio
async def test_evaluacion_repo_list_by_tenant(
    db_session: AsyncSession,
    test_tenant: Tenant,
    dictado_valido,
):
    """Test listing evaluaciones with optional filters."""
    repo = EvaluacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "dictado_id": dictado_valido.id,
        "tipo": "Coloquio",
        "instancia": "Coloquio A",
        "cupo_maximo": 20,
    })
    await repo.create({
        "dictado_id": dictado_valido.id,
        "tipo": "Parcial",
        "instancia": "Parcial B",
        "cupo_maximo": 30,
    })

    all_items = await repo.list_by_tenant()
    assert len(all_items) == 2

    filtered = await repo.list_by_tenant(dictado_id=dictado_valido.id)
    assert len(filtered) == 2

    filtered_estado = await repo.list_by_tenant(estado="Activa")
    assert len(filtered_estado) >= 2


@pytest.mark.asyncio
async def test_evaluacion_repo_count_metricas(
    db_session: AsyncSession,
    test_tenant: Tenant,
    dictado_valido,
    alumno_user,
    otro_alumno_user,
):
    """Test metricas counts after creating related data."""
    ev_repo = EvaluacionRepository(session=db_session, tenant_id=test_tenant.id)
    ev = await ev_repo.create({
        "dictado_id": dictado_valido.id,
        "tipo": "Coloquio",
        "instancia": "Metricas Test",
        "cupo_maximo": 10,
    })

    # Convocar alumnos
    ac_repo = AlumnoConvocadoRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    await ac_repo.bulk_import(
        evaluacion_id=ev.id,
        alumno_ids=[alumno_user.id, otro_alumno_user.id],
        tenant_id=test_tenant.id,
    )

    # Create reserva
    res_repo = ReservaEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    await res_repo.create({
        "evaluacion_id": ev.id,
        "alumno_id": alumno_user.id,
        "estado": "Activa",
    })

    metrics = await ev_repo.count_metricas()
    assert metrics["total_alumnos_convocados"] == 2
    assert metrics["instancias_activas"] >= 1
    assert metrics["reservas_activas"] >= 1


# ── ReservaEvaluacionRepository ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reserva_repo_count_activas(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
    otro_alumno_user,
):
    """Test count_activas_by_evaluacion."""
    repo = ReservaEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "estado": "Activa",
    })
    await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": otro_alumno_user.id,
        "estado": "Activa",
    })
    count = await repo.count_activas_by_evaluacion(evaluacion_valida.id)
    assert count == 2


@pytest.mark.asyncio
async def test_reserva_repo_cancelar(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test cancelling a reservation."""
    repo = ReservaEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    reserva = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "estado": "Activa",
    })
    cancelled = await repo.cancelar(reserva.id)
    assert cancelled is not None
    assert cancelled.estado == "Cancelada"


@pytest.mark.asyncio
async def test_reserva_repo_cancelar_not_found(
    db_session: AsyncSession,
    test_tenant: Tenant,
):
    """Cancelar on non-existent ID returns None."""
    repo = ReservaEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    result = await repo.cancelar(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_reserva_repo_list_activas(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
    otro_alumno_user,
):
    """Test listing active reservations with filters."""
    repo = ReservaEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    r1 = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "estado": "Activa",
    })
    r2 = await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": otro_alumno_user.id,
        "estado": "Activa",
    })

    items = await repo.list_activas_by_tenant()
    assert len(items) == 2

    items_alumno = await repo.list_activas_by_tenant(
        alumno_id=alumno_user.id
    )
    assert len(items_alumno) == 1
    assert items_alumno[0].id == r1.id


# ── ResultadoEvaluacionRepository ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_resultado_repo_get_by_evaluacion_alumno(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test fetching a result by evaluacion + alumno."""
    repo = ResultadoEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "nota_final": "Aprobado",
    })
    found = await repo.get_by_evaluacion_alumno(
        evaluacion_valida.id, alumno_user.id
    )
    assert found is not None
    assert found.nota_final == "Aprobado"

    missing = await repo.get_by_evaluacion_alumno(
        evaluacion_valida.id, uuid.uuid4()
    )
    assert missing is None


@pytest.mark.asyncio
async def test_resultado_repo_list_by_tenant(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
    otro_alumno_user,
):
    """Test listing resultados with optional filters."""
    repo = ResultadoEvaluacionRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": alumno_user.id,
        "nota_final": "8",
    })
    await repo.create({
        "evaluacion_id": evaluacion_valida.id,
        "alumno_id": otro_alumno_user.id,
        "nota_final": "9",
    })

    items = await repo.list_by_tenant()
    assert len(items) == 2

    items_alumno = await repo.list_by_tenant(alumno_id=alumno_user.id)
    assert len(items_alumno) == 1


# ── AlumnoConvocadoRepository ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ac_repo_bulk_import(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test bulk import of alumnos (idempotent)."""
    repo = AlumnoConvocadoRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    count = await repo.bulk_import(
        evaluacion_id=evaluacion_valida.id,
        alumno_ids=[alumno_user.id],
        tenant_id=test_tenant.id,
    )
    assert count == 1

    # Import same alumno again — idempotent
    count2 = await repo.bulk_import(
        evaluacion_id=evaluacion_valida.id,
        alumno_ids=[alumno_user.id],
        tenant_id=test_tenant.id,
    )
    assert count2 == 0


@pytest.mark.asyncio
async def test_ac_repo_bulk_import_empty(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
):
    """Bulk import with empty list returns 0."""
    repo = AlumnoConvocadoRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    count = await repo.bulk_import(
        evaluacion_id=evaluacion_valida.id,
        alumno_ids=[],
        tenant_id=test_tenant.id,
    )
    assert count == 0


@pytest.mark.asyncio
async def test_ac_repo_exists(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
):
    """Test exists check for convocado."""
    repo = AlumnoConvocadoRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    assert not await repo.exists(evaluacion_valida.id, alumno_user.id)

    await repo.bulk_import(
        evaluacion_id=evaluacion_valida.id,
        alumno_ids=[alumno_user.id],
        tenant_id=test_tenant.id,
    )
    assert await repo.exists(evaluacion_valida.id, alumno_user.id)


@pytest.mark.asyncio
async def test_ac_repo_list_by_evaluacion(
    db_session: AsyncSession,
    test_tenant: Tenant,
    evaluacion_valida,
    alumno_user,
    otro_alumno_user,
):
    """Test listing convocados by evaluacion."""
    repo = AlumnoConvocadoRepository(
        session=db_session, tenant_id=test_tenant.id
    )
    await repo.bulk_import(
        evaluacion_id=evaluacion_valida.id,
        alumno_ids=[alumno_user.id, otro_alumno_user.id],
        tenant_id=test_tenant.id,
    )
    items = await repo.list_by_evaluacion(evaluacion_valida.id)
    assert len(items) == 2
