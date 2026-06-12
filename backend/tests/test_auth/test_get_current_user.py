import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.services.auth.token_service import TokenService


def _make_token(user_id=None, tenant_id=None, roles=None, secret="a" * 32):
    payload = {
        "sub": str(user_id or uuid.uuid4()),
        "tenant_id": str(tenant_id or uuid.uuid4()),
        "roles": roles or ["ALUMNO"],
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _get_ts(secret="a" * 32):
    ts = TokenService()
    ts._secret = secret
    ts._algorithm = "HS256"
    return ts


def test_valid_token_returns_current_user():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    token = _make_token(user_id=user_id, tenant_id=tenant_id, roles=["ADMIN", "PROFESOR"])
    ts = _get_ts()
    payload = ts.verify_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["roles"] == ["ADMIN", "PROFESOR"]


def test_expired_token_raises():
    ts = _get_ts()
    payload = {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "roles": ["ALUMNO"],
        "exp": datetime.now(UTC) - timedelta(hours=1),
        "iat": datetime.now(UTC) - timedelta(hours=1),
        "jti": str(uuid.uuid4()),
    }
    expired = jwt.encode(payload, "a" * 32, algorithm="HS256")
    with pytest.raises(ValueError, match="Invalid token"):
        ts.verify_access_token(expired)


def test_invalid_signature_raises():
    token = _make_token(secret="b" * 32)
    ts = _get_ts(secret="a" * 32)
    with pytest.raises(ValueError, match="Invalid token"):
        ts.verify_access_token(token)
