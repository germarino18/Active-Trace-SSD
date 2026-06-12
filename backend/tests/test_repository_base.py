import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


async def test_create_record(db_session: AsyncSession):
    parent = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent", "slug": "parent"}
    )
    repo = BaseRepository(model=Tenant, session=db_session, tenant_id=parent.id)
    tenant = await repo.create({"name": "Repo Test", "slug": "repo-test"})
    assert tenant.id is not None
    assert tenant.name == "Repo Test"


async def test_find_by_id_returns_none_for_missing(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    found = await repo.find_by_id(uuid.uuid4())
    assert found is None


async def test_find_all_with_pagination(db_session: AsyncSession):
    parent = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent", "slug": "parent"}
    )
    repo = BaseRepository(model=Tenant, session=db_session, tenant_id=parent.id)
    for i in range(5):
        await repo.create({"name": f"T{i}", "slug": f"t{i}"})

    page1 = await repo.find_all(skip=0, limit=2)
    assert len(page1) == 2

    page2 = await repo.find_all(skip=2, limit=2)
    assert len(page2) == 2

    page3 = await repo.find_all(skip=4, limit=2)
    assert len(page3) == 1


async def test_find_by_filters(db_session: AsyncSession):
    parent = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent", "slug": "parent"}
    )
    repo = BaseRepository(model=Tenant, session=db_session, tenant_id=parent.id)
    await repo.create({"name": "Alpha", "slug": "alpha"})
    await repo.create({"name": "Beta", "slug": "beta"})

    results = await repo.find_by(slug="alpha")
    assert len(results) == 1
    assert results[0].name == "Alpha"

    results = await repo.find_by(name="NonExistent")
    assert len(results) == 0


async def test_update_raises_not_found(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    with pytest.raises(NotFoundException):
        await repo.update(uuid.uuid4(), {"name": "Nope"})


async def test_soft_delete_raises_not_found(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    with pytest.raises(NotFoundException):
        await repo.soft_delete(uuid.uuid4())


async def test_hard_delete_raises_not_found(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    with pytest.raises(NotFoundException):
        await repo.hard_delete(uuid.uuid4())
