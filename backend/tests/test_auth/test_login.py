import uuid

import pytest
from httpx import AsyncClient

from app.core.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService


async def _create_test_user(db_session, tenant_id, email="login@example.com", password="TestP@ss1", roles=None):
    repo = UserRepository(session=db_session, tenant_id=tenant_id)
    pw_hash = PasswordService.hash_password(password)
    user = await repo.create({
        "email": email,
        "password_hash": pw_hash,
        "display_name": "Test User",
        "roles": roles or ["ALUMNO"],
        "tenant_id": tenant_id,
    })
    return user


async def test_login_success_without_2fa(client: AsyncClient, db_session, test_tenant):
    await _create_test_user(db_session, test_tenant.id)
    response = await client.post(
        "/api/auth/authenticate",
        json={"email": "login@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800
    assert data["requires_2fa"] is False
    assert data.get("challenge_token") is None


async def test_login_invalid_password(client: AsyncClient, db_session, test_tenant):
    await _create_test_user(db_session, test_tenant.id)
    response = await client.post(
        "/api/auth/authenticate",
        json={"email": "login@example.com", "password": "WrongP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    assert response.status_code == 401


async def test_login_nonexistent_email(client: AsyncClient, db_session, test_tenant):
    response = await client.post(
        "/api/auth/authenticate",
        json={"email": "noone@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    assert response.status_code == 401


async def test_login_inactive_user(client: AsyncClient, db_session, test_tenant):
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    user = await repo.create({
        "email": "inactive@example.com",
        "password_hash": pw_hash,
        "display_name": "Inactive",
        "is_active": False,
        "roles": ["ALUMNO"],
        "tenant_id": test_tenant.id,
    })
    response = await client.post(
        "/api/auth/authenticate",
        json={"email": "inactive@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    assert response.status_code == 403


async def test_login_with_2fa_flow(client: AsyncClient, db_session, test_tenant):
    import pyotp
    from app.services.auth.two_factor_service import TwoFactorService
    from app.core.security import encrypt_value, get_encryption_key

    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    secret = pyotp.random_base32()
    key = get_encryption_key()
    encrypted = encrypt_value(secret, key)
    user = await repo.create({
        "email": "2fa@example.com",
        "password_hash": pw_hash,
        "display_name": "2FA User",
        "roles": ["ALUMNO"],
        "tenant_id": test_tenant.id,
        "totp_secret": encrypted,
        "totp_enabled_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    })
    response = await client.post(
        "/api/auth/authenticate",
        json={"email": "2fa@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_2fa"] is True
    assert "challenge_token" in data
    assert data.get("access_token") is None

    totp = pyotp.TOTP(secret)
    code = totp.now()
    response2 = await client.post(
        "/api/auth/login",
        json={"challenge_token": data["challenge_token"], "totp_code": code},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert "access_token" in data2
    assert "refresh_token" in data2


async def test_challenge_token_reuse_prevented(client: AsyncClient, db_session, test_tenant):
    import pyotp
    from app.core.security import encrypt_value, get_encryption_key

    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    secret = pyotp.random_base32()
    key = get_encryption_key()
    encrypted = encrypt_value(secret, key)
    user = await repo.create({
        "email": "reuse@example.com",
        "password_hash": pw_hash,
        "display_name": "Reuse",
        "roles": ["ALUMNO"],
        "tenant_id": test_tenant.id,
        "totp_secret": encrypted,
        "totp_enabled_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    })
    auth_resp = await client.post(
        "/api/auth/authenticate",
        json={"email": "reuse@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    challenge = auth_resp.json()["challenge_token"]
    totp = pyotp.TOTP(secret)
    code = totp.now()
    await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge, "totp_code": code},
    )
    response2 = await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge, "totp_code": code},
    )
    assert response2.status_code == 401


async def test_wrong_totp_does_not_consume_challenge(client: AsyncClient, db_session, test_tenant):
    import pyotp
    from app.core.security import encrypt_value, get_encryption_key

    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    secret = pyotp.random_base32()
    key = get_encryption_key()
    encrypted = encrypt_value(secret, key)
    await repo.create({
        "email": "retry@example.com",
        "password_hash": pw_hash,
        "display_name": "Retry",
        "roles": ["ALUMNO"],
        "tenant_id": test_tenant.id,
        "totp_secret": encrypted,
        "totp_enabled_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    })
    auth_resp = await client.post(
        "/api/auth/authenticate",
        json={"email": "retry@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    challenge = auth_resp.json()["challenge_token"]
    totp = pyotp.TOTP(secret)
    correct_code = totp.now()
    wrong_code = "000000" if correct_code != "000000" else "111111"

    response_wrong = await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge, "totp_code": wrong_code},
    )
    assert response_wrong.status_code == 401

    response_correct = await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge, "totp_code": correct_code},
    )
    assert response_correct.status_code == 200
    data = response_correct.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_fresh_challenge_token_after_reuse_blocked(client: AsyncClient, db_session, test_tenant):
    import pyotp
    from app.core.security import encrypt_value, get_encryption_key

    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    secret = pyotp.random_base32()
    key = get_encryption_key()
    encrypted = encrypt_value(secret, key)
    await repo.create({
        "email": "fresh@example.com",
        "password_hash": pw_hash,
        "display_name": "Fresh",
        "roles": ["ALUMNO"],
        "tenant_id": test_tenant.id,
        "totp_secret": encrypted,
        "totp_enabled_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    })
    totp = pyotp.TOTP(secret)

    # First full login cycle.
    auth_resp1 = await client.post(
        "/api/auth/authenticate",
        json={"email": "fresh@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    challenge1 = auth_resp1.json()["challenge_token"]
    code1 = totp.now()
    login1 = await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge1, "totp_code": code1},
    )
    assert login1.status_code == 200

    # Replaying the first challenge token must fail.
    replay = await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge1, "totp_code": code1},
    )
    assert replay.status_code == 401

    # A fresh re-authentication (new challenge token) must still succeed.
    auth_resp2 = await client.post(
        "/api/auth/authenticate",
        json={"email": "fresh@example.com", "password": "TestP@ss1"},
        headers={"X-Tenant-ID": str(test_tenant.id)},
    )
    challenge2 = auth_resp2.json()["challenge_token"]
    code2 = totp.now()
    login2 = await client.post(
        "/api/auth/login",
        json={"challenge_token": challenge2, "totp_code": code2},
    )
    assert login2.status_code == 200
    data2 = login2.json()
    assert "access_token" in data2
    assert "refresh_token" in data2
