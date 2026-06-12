from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest
from httpx import AsyncClient

from app.repositories.recovery_token_repository import RecoveryTokenRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth.password_recovery_service import PasswordRecoveryService
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService


async def _create_user(db_session, tenant_id, email="recovery@example.com"):
    repo = UserRepository(session=db_session, tenant_id=tenant_id)
    pw_hash = PasswordService.hash_password("OldP@ss1")
    return await repo.create({
        "email": email,
        "password_hash": pw_hash,
        "display_name": "Recovery User",
        "roles": ["ALUMNO"],
        "tenant_id": tenant_id,
    })


async def test_forgot_creates_token_for_existing_email(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    response = await client.post(
        "/api/auth/forgot",
        json={"email": "recovery@example.com"},
    )
    assert response.status_code == 200
    recovery_repo = RecoveryTokenRepository(session=db_session)
    from sqlalchemy import select
    from app.models.recovery_token import RecoveryToken
    query = select(RecoveryToken).where(RecoveryToken.user_id == user.id)
    result = await db_session.execute(query)
    tokens = result.scalars().all()
    assert len(tokens) >= 1
    assert tokens[0].expires_at > datetime.now(UTC)


async def test_forgot_for_nonexistent_email_returns_200(client: AsyncClient):
    response = await client.post(
        "/api/auth/forgot",
        json={"email": "noone@example.com"},
    )
    assert response.status_code == 200


async def test_reset_with_valid_token(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    refresh_repo = RefreshTokenRepository(session=db_session)
    recovery_repo = RecoveryTokenRepository(session=db_session)
    svc = PasswordRecoveryService(
        recovery_token_repo=recovery_repo,
        refresh_token_repo=refresh_repo,
    )
    raw_token = await svc.generate_recovery_token(user)
    response = await client.post(
        "/api/auth/reset",
        json={
            "token": raw_token,
            "new_password": "NewStr0ng!",
            "new_password_confirm": "NewStr0ng!",
        },
    )
    assert response.status_code == 200
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    updated = await repo.find_by_id(user.id)
    assert PasswordService.verify_password("NewStr0ng!", updated.password_hash) is True
    result = await recovery_repo.find_by_hash(sha256(raw_token.encode()).hexdigest())
    assert result.used_at is not None


async def test_reset_with_mismatched_passwords(client: AsyncClient):
    response = await client.post(
        "/api/auth/reset",
        json={
            "token": "sometoken",
            "new_password": "NewStr0ng!",
            "new_password_confirm": "Different!",
        },
    )
    assert response.status_code == 422


async def test_reset_with_short_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/reset",
        json={
            "token": "sometoken",
            "new_password": "abc",
            "new_password_confirm": "abc",
        },
    )
    assert response.status_code == 422


async def test_reset_with_nonexistent_token(client: AsyncClient):
    response = await client.post(
        "/api/auth/reset",
        json={
            "token": "nonexistent-token-value",
            "new_password": "NewStr0ng!",
            "new_password_confirm": "NewStr0ng!",
        },
    )
    assert response.status_code == 401
