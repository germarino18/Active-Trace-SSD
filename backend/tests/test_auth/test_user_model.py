import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.tenancy import TenantContext
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository


async def test_create_user_with_required_fields(db_session, test_tenant):
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    user = await repo.create({
        "email": "user@example.com",
        "password_hash": "$argon2id$hash",
        "display_name": "John Doe",
        "roles": ["ALUMNO"],
        "tenant_id": test_tenant.id,
    })
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.display_name == "John Doe"
    assert user.is_active is True
    assert user.roles == ["ALUMNO"]
    assert user.created_at is not None
    assert user.updated_at is not None


async def test_email_unique_per_tenant(db_session, test_tenant):
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "email": "dup@example.com",
        "password_hash": "$argon2id$hash1",
        "display_name": "User One",
        "tenant_id": test_tenant.id,
    })
    with pytest.raises(IntegrityError):
        await repo.create({
            "email": "dup@example.com",
            "password_hash": "$argon2id$hash2",
            "display_name": "User Two",
            "tenant_id": test_tenant.id,
        })


async def test_same_email_across_tenants(db_session, test_tenant, another_tenant):
    repo1 = UserRepository(session=db_session, tenant_id=test_tenant.id)
    await repo1.create({
        "email": "cross@example.com",
        "password_hash": "$argon2id$hash",
        "display_name": "User A",
        "tenant_id": test_tenant.id,
    })
    repo2 = UserRepository(session=db_session, tenant_id=another_tenant.id)
    user2 = await repo2.create({
        "email": "cross@example.com",
        "password_hash": "$argon2id$hash",
        "display_name": "User B",
        "tenant_id": another_tenant.id,
    })
    assert user2.email == "cross@example.com"
    assert user2.tenant_id == another_tenant.id


async def test_email_uniqueness_allows_reuse_after_soft_delete(db_session, test_tenant):
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    user = await repo.create({
        "email": "old@example.com",
        "password_hash": "$argon2id$hash",
        "display_name": "Old User",
        "tenant_id": test_tenant.id,
    })
    await repo.soft_delete(user.id)
    new_user = await repo.create({
        "email": "old@example.com",
        "password_hash": "$argon2id$hash2",
        "display_name": "New User",
        "tenant_id": test_tenant.id,
    })
    assert new_user.email == "old@example.com"
    assert new_user.id != user.id


async def test_find_by_email(db_session, test_tenant):
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({
        "email": "findme@example.com",
        "password_hash": "$argon2id$hash",
        "display_name": "Find Me",
        "tenant_id": test_tenant.id,
    })
    found = await repo.find_by_email(test_tenant.id, "findme@example.com")
    assert found is not None
    assert found.email == "findme@example.com"


async def test_find_by_email_not_found(db_session, test_tenant):
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_email(test_tenant.id, "nonexistent@example.com")
    assert found is None
