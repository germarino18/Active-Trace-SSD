import uuid

import pyotp
import pytest
from httpx import AsyncClient

from app.repositories.user_repository import UserRepository
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService
from app.services.auth.two_factor_service import TwoFactorService


async def _create_user(db_session, tenant_id, email="2fa-endpoint@example.com"):
    repo = UserRepository(session=db_session, tenant_id=tenant_id)
    pw_hash = PasswordService.hash_password("TestP@ss1")
    return await repo.create({
        "email": email,
        "password_hash": pw_hash,
        "display_name": "2FA User",
        "roles": ["ALUMNO"],
        "tenant_id": tenant_id,
    })


async def test_enroll_requires_auth(client: AsyncClient):
    response = await client.post("/api/auth/2fa/enroll")
    assert response.status_code == 401


async def test_enroll_generates_secret(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    ts = TokenService()
    access = await ts.create_access_token(user, db_session)
    response = await client.post(
        "/api/auth/2fa/enroll",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "secret" in data
    assert "qr_uri" in data
    assert data["qr_uri"].startswith("otpauth://totp/")

    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    updated = await repo.find_by_id(user.id)
    assert updated.totp_secret is not None


async def test_enroll_when_already_enabled(client: AsyncClient, db_session, test_tenant):
    from app.core.security import encrypt_value, get_encryption_key
    user = await _create_user(db_session, test_tenant.id)
    svc = TwoFactorService()
    secret = svc.generate_secret(user.email)["secret"]
    encrypted = svc.encrypt_secret(secret)
    user.totp_secret = encrypted
    user.totp_enabled_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await db_session.flush()
    ts = TokenService()
    access = await ts.create_access_token(user, db_session)
    response = await client.post(
        "/api/auth/2fa/enroll",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 409


async def test_verify_with_valid_code(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    svc = TwoFactorService()
    secret = svc.generate_secret(user.email)["secret"]
    encrypted = svc.encrypt_secret(secret)
    user.totp_secret = encrypted
    await db_session.flush()
    ts = TokenService()
    access = await ts.create_access_token(user, db_session)
    totp = pyotp.TOTP(secret)
    code = totp.now()
    response = await client.post(
        "/api/auth/2fa/verify",
        json={"totp_code": code},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 200
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    updated = await repo.find_by_id(user.id)
    assert updated.totp_enabled_at is not None


async def test_verify_without_enrollment(client: AsyncClient, db_session, test_tenant):
    user = await _create_user(db_session, test_tenant.id)
    ts = TokenService()
    access = await ts.create_access_token(user, db_session)
    response = await client.post(
        "/api/auth/2fa/verify",
        json={"totp_code": "123456"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 400


async def test_disable_with_correct_password_and_totp(client: AsyncClient, db_session, test_tenant):
    from app.core.security import encrypt_value, get_encryption_key
    user = await _create_user(db_session, test_tenant.id)
    svc = TwoFactorService()
    secret = svc.generate_secret(user.email)["secret"]
    encrypted = svc.encrypt_secret(secret)
    user.totp_secret = encrypted
    user.totp_enabled_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await db_session.flush()
    ts = TokenService()
    access = await ts.create_access_token(user, db_session)
    totp = pyotp.TOTP(secret)
    code = totp.now()
    response = await client.post(
        "/api/auth/2fa/disable",
        json={"password": "TestP@ss1", "totp_code": code},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 200
    repo = UserRepository(session=db_session, tenant_id=test_tenant.id)
    updated = await repo.find_by_id(user.id)
    assert updated.totp_secret is None
    assert updated.totp_enabled_at is None
