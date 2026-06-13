import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.dictado import Dictado
from app.models.materia import Materia
from app.repositories.base import BaseRepository


# ── Carrera ────────────────────────────────────────────────────────────


async def test_create_carrera_persists_with_tenant_scope(
    db_session: AsyncSession, test_tenant
):
    repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    assert carrera.id is not None
    assert carrera.tenant_id == test_tenant.id
    assert carrera.codigo == "ING-INF"
    assert carrera.estado == "Activa"
    assert carrera.deleted_at is None


async def test_carrera_codigo_unique_per_tenant_excludes_soft_deleted(
    db_session: AsyncSession, test_tenant
):
    repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await repo.create({"codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"})
    await repo.soft_delete(carrera.id)

    # Reusing the codigo after soft delete must succeed (D4).
    recreated = await repo.create({"codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas v2"})
    assert recreated.id != carrera.id
    assert recreated.codigo == "ING-SIS"


# ── Materia ────────────────────────────────────────────────────────────


async def test_create_materia_persists_with_tenant_scope(
    db_session: AsyncSession, test_tenant
):
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    materia = await repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})

    assert materia.id is not None
    assert materia.tenant_id == test_tenant.id
    assert materia.estado == "Activa"
    assert materia.deleted_at is None


# ── Cohorte ────────────────────────────────────────────────────────────


async def test_create_cohorte_persists_with_carrera_fk_and_tenant_scope(
    db_session: AsyncSession, test_tenant
):
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    cohorte = await cohorte_repo.create(
        {"carrera_id": carrera.id, "nombre": "2024", "anio": 2024}
    )

    assert cohorte.id is not None
    assert cohorte.tenant_id == test_tenant.id
    assert cohorte.carrera_id == carrera.id
    assert cohorte.estado == "Activa"
    assert cohorte.vig_desde is None
    assert cohorte.vig_hasta is None


# ── Dictado ────────────────────────────────────────────────────────────


async def test_create_dictado_persists_with_full_terna_and_tenant_scope(
    db_session: AsyncSession, test_tenant
):
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    materia = await materia_repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})

    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    cohorte = await cohorte_repo.create(
        {"carrera_id": carrera.id, "nombre": "2024", "anio": 2024}
    )

    dictado_repo = BaseRepository(model=Dictado, session=db_session, tenant_id=test_tenant.id)
    dictado = await dictado_repo.create(
        {
            "materia_id": materia.id,
            "carrera_id": carrera.id,
            "cohorte_id": cohorte.id,
        }
    )

    assert dictado.id is not None
    assert dictado.tenant_id == test_tenant.id
    assert dictado.materia_id == materia.id
    assert dictado.carrera_id == carrera.id
    assert dictado.cohorte_id == cohorte.id
    assert dictado.estado == "Activo"
