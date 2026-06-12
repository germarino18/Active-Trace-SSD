from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


async def test_soft_delete_excludes_from_default_query(
    db_session: AsyncSession,
):
    repo = BaseRepository(model=Tenant, session=db_session)
    tenant = await repo.create({"name": "To Delete", "slug": "to-delete"})

    await repo.soft_delete(tenant.id)

    found = await repo.find_by_id(tenant.id)
    assert found is None


async def test_include_deleted_returns_soft_deleted(
    db_session: AsyncSession,
):
    repo = BaseRepository(model=Tenant, session=db_session)
    tenant = await repo.create({"name": "Inc Del", "slug": "inc-del"})

    await repo.soft_delete(tenant.id)

    repo._include_soft_deleted = False
    repo_inc = BaseRepository(model=Tenant, session=db_session)
    repo_inc._include_soft_deleted = True
    # Actually use include_deleted method
    repo3 = BaseRepository(model=Tenant, session=db_session)
    found = await repo3.include_deleted().find_by_id(tenant.id)
    assert found is not None
    assert found.deleted_at is not None


async def test_soft_delete_then_restore(
    db_session: AsyncSession,
):
    repo = BaseRepository(model=Tenant, session=db_session)
    tenant = await repo.create({"name": "Restore Me", "slug": "restore-me"})

    await repo.soft_delete(tenant.id)
    found_deleted = await repo.find_by_id(tenant.id)
    assert found_deleted is None

    tenant_from_db = await repo.include_deleted().find_by_id(tenant.id)
    tenant_from_db.deleted_at = None
    await db_session.flush()

    found_restored = await repo.find_by_id(tenant.id)
    assert found_restored is not None
    assert found_restored.name == "Restore Me"


async def test_hard_delete_removes_permanently(
    db_session: AsyncSession,
):
    repo = BaseRepository(model=Tenant, session=db_session)
    tenant = await repo.create({"name": "Hard Delete", "slug": "hard-del"})

    await repo.hard_delete(tenant.id)

    found = await repo.find_by_id(tenant.id)
    assert found is None
