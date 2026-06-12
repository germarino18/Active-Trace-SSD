import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


@pytest.fixture
async def tenant_a(db_session: AsyncSession) -> Tenant:
    repo = BaseRepository(model=Tenant, session=db_session)
    return await repo.create(
        {
            "name": "Tenant A",
            "slug": "tenant-a",
        }
    )


@pytest.fixture
async def tenant_b(db_session: AsyncSession) -> Tenant:
    repo = BaseRepository(model=Tenant, session=db_session)
    return await repo.create(
        {
            "name": "Tenant B",
            "slug": "tenant-b",
        }
    )


async def test_create_tenant(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    tenant = await repo.create(
        {"name": "New University", "slug": "new-uni"}
    )
    assert tenant.id is not None
    assert tenant.name == "New University"
    assert tenant.slug == "new-uni"
    assert tenant.is_active is True


async def test_find_tenant_by_id(db_session: AsyncSession, tenant_a: Tenant):
    repo = BaseRepository(model=Tenant, session=db_session)
    found = await repo.find_by_id(tenant_a.id)
    assert found is not None
    assert found.id == tenant_a.id
    assert found.name == tenant_a.name


async def test_find_tenant_by_id_not_found(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    found = await repo.find_by_id(uuid.uuid4())
    assert found is None


async def test_update_tenant(db_session: AsyncSession, tenant_a: Tenant):
    repo = BaseRepository(model=Tenant, session=db_session)
    updated = await repo.update(tenant_a.id, {"name": "Updated University"})
    assert updated.name == "Updated University"


async def test_soft_delete_tenant(db_session: AsyncSession, tenant_a: Tenant):
    repo = BaseRepository(model=Tenant, session=db_session)
    deleted = await repo.soft_delete(tenant_a.id)
    assert deleted.deleted_at is not None

    found = await repo.find_by_id(tenant_a.id)
    assert found is None


async def test_find_all_tenants(db_session: AsyncSession):
    repo = BaseRepository(model=Tenant, session=db_session)
    t1 = await repo.create({"name": "U1", "slug": "u1"})
    t2 = await repo.create({"name": "U2", "slug": "u2"})
    all_tenants = await repo.find_all()
    assert len(all_tenants) >= 2
    assert t1.id in [t.id for t in all_tenants]
    assert t2.id in [t.id for t in all_tenants]
