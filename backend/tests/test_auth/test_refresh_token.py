import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService


async def _create_user(db_session, tenant_id):
    repo = UserRepository(session=db_session, tenant_id=tenant_id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    return await repo.create({
        "email": "refresh@example.com",
        "password_hash": pw_hash,
        "display_name": "Refresh User",
        "roles": ["ALUMNO"],
        "tenant_id": tenant_id,
    })


async def test_refresh_success(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    ts = TokenService()
    raw, token_hash = ts.generate_refresh_token()
    refresh_repo = RefreshTokenRepository(session=db_session)
    token = await refresh_repo.create({
        "user_id": user.id,
        "token_hash": token_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": raw},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    old_token = await refresh_repo.find_by_hash(token_hash)
    assert old_token.revoked_at is not None


async def test_refresh_with_nonexistent_token(client: AsyncClient):
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": str(uuid.uuid4())},
    )
    assert response.status_code == 401


async def test_logout_revokes_token(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    ts = TokenService()
    raw, token_hash = ts.generate_refresh_token()
    refresh_repo = RefreshTokenRepository(session=db_session)
    token = await refresh_repo.create({
        "user_id": user.id,
        "token_hash": token_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    access = ts.create_access_token(user)
    response = await client.post(
        "/api/auth/logout",
        json={"refresh_token": raw},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 200
    found = await refresh_repo.find_by_hash(token_hash)
    assert found.revoked_at is not None


async def test_logout_without_auth(client: AsyncClient):
    response = await client.post(
        "/api/auth/logout",
        json={"refresh_token": str(uuid.uuid4())},
    )
    assert response.status_code == 401
