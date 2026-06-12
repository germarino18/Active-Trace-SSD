from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


async def test_find_by_id_respects_tenant_scope(
    db_session: AsyncSession,
):
    parent = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent", "slug": "parent"}
    )

    repo_a = BaseRepository(model=Tenant, session=db_session, tenant_id=parent.id)
    tenant_a = await repo_a.create({"name": "A", "slug": "uni-a"})

    repo_b = BaseRepository(model=Tenant, session=db_session, tenant_id=tenant_a.id)
    tenant_b = await repo_b.create({"name": "B", "slug": "uni-b"})

    found_a = await repo_a.find_by_id(tenant_a.id)
    assert found_a is not None
    assert found_a.id == tenant_a.id

    found_b_from_a = await repo_a.find_by_id(tenant_b.id)
    assert found_b_from_a is None


async def test_find_all_respects_tenant_scope(
    db_session: AsyncSession,
):
    parent_a = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent A", "slug": "parent-a"}
    )
    parent_b = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent B", "slug": "parent-b"}
    )

    repo_a = BaseRepository(model=Tenant, session=db_session, tenant_id=parent_a.id)
    await repo_a.create({"name": "A1", "slug": "a1"})

    repo_b = BaseRepository(model=Tenant, session=db_session, tenant_id=parent_b.id)
    await repo_b.create({"name": "B1", "slug": "b1"})

    results_a = await repo_a.find_all()
    assert len(results_a) == 1
    assert results_a[0].slug == "a1"

    results_b = await repo_b.find_all()
    assert len(results_b) == 1
    assert results_b[0].slug == "b1"


async def test_find_by_respects_tenant_scope(
    db_session: AsyncSession,
):
    parent_a = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent A", "slug": "parent-a"}
    )
    parent_b = await BaseRepository(model=Tenant, session=db_session).create(
        {"name": "Parent B", "slug": "parent-b"}
    )

    repo_a = BaseRepository(model=Tenant, session=db_session, tenant_id=parent_a.id)
    await repo_a.create({"name": "A", "slug": "slug-a"})

    repo_b = BaseRepository(model=Tenant, session=db_session, tenant_id=parent_b.id)
    await repo_b.create({"name": "B", "slug": "slug-b"})

    results_a = await repo_a.find_by(slug="slug-a")
    assert len(results_a) == 1
    assert results_a[0].name == "A"

    results_b = await repo_b.find_by(slug="slug-b")
    assert len(results_b) == 1
    assert results_b[0].name == "B"
