import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.programa_materia_repository import ProgramaMateriaRepository


@pytest.mark.asyncio
async def test_find_by_dictado_returns_program(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = ProgramaMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    program = await repo.create({
        "dictado_id": seeded_dictado,
        "titulo": "Programa 2024",
        "referencia_archivo": "uploads/programas/test.pdf",
    })

    found = await repo.find_by_dictado(seeded_dictado)
    assert found is not None
    assert found.id == program.id
    assert found.titulo == "Programa 2024"


@pytest.mark.asyncio
async def test_find_by_dictado_returns_none_when_missing(
    db_session: AsyncSession, test_tenant
):
    repo = ProgramaMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_dictado(uuid.uuid4())
    assert found is None


@pytest.mark.asyncio
async def test_exists_by_dictado_checks_uniqueness(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = ProgramaMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    assert not await repo.exists_by_dictado(seeded_dictado)

    await repo.create({
        "dictado_id": seeded_dictado,
        "titulo": "Programa",
        "referencia_archivo": "uploads/test.pdf",
    })
    assert await repo.exists_by_dictado(seeded_dictado)


@pytest.mark.asyncio
async def test_tenant_scoping_isolation(
    db_session: AsyncSession, test_tenant, another_tenant, seeded_dictado
):
    repo1 = ProgramaMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    program = await repo1.create({
        "dictado_id": seeded_dictado,
        "titulo": "Programa Tenant 1",
        "referencia_archivo": "uploads/t1.pdf",
    })

    repo2 = ProgramaMateriaRepository(session=db_session, tenant_id=another_tenant.id)
    found = await repo2.find_by_id(program.id)
    assert found is None


@pytest.mark.asyncio
async def test_soft_delete_hides_record(
    db_session: AsyncSession, test_tenant, seeded_dictado
):
    repo = ProgramaMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    program = await repo.create({
        "dictado_id": seeded_dictado,
        "titulo": "Programa",
        "referencia_archivo": "uploads/test.pdf",
    })

    await repo.soft_delete(program.id)
    found = await repo.find_by_dictado(seeded_dictado)
    assert found is None
