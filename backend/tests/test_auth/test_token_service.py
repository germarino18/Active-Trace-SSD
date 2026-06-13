import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.models.user import User
from app.services.auth.token_service import TokenService


def _make_user(tenant_id=None):
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant_id or uuid.uuid4(),
        email="test@example.com",
        password_hash="hash",
        display_name="Test User",
        roles=["ALUMNO"],
    )


def _get_ts(secret="a" * 32):
    ts = TokenService()
    ts._secret = secret
    ts._algorithm = "HS256"
    ts._access_token_ttl = timedelta(minutes=30)
    ts._challenge_token_ttl = timedelta(minutes=5)
    return ts


def test_create_access_token_has_correct_claims():
    user = _make_user()
    ts = _get_ts()
    token = ts.create_access_token(user)
    payload = ts.verify_access_token(token)
    assert payload["sub"] == str(user.id)
    assert payload["tenant_id"] == str(user.tenant_id)
    assert payload["roles"] == ["ALUMNO"]
    assert "exp" in payload
    assert "iat" in payload


def test_create_access_token_without_actor_id_has_no_actor_id_claim():
    user = _make_user()
    ts = _get_ts()
    token = ts.create_access_token(user)
    payload = ts.verify_access_token(token)
    assert "actor_id" not in payload


def test_create_access_token_with_actor_id_embeds_claim():
    user = _make_user()
    actor_id = uuid.uuid4()
    ts = _get_ts()
    token = ts.create_access_token(user, actor_id=actor_id)
    payload = ts.verify_access_token(token)
    assert payload["actor_id"] == str(actor_id)
    assert payload["sub"] == str(user.id)
    assert "jti" in payload


def test_access_token_expires_in_30_minutes():
    user = _make_user()
    ts = _get_ts()
    token = ts.create_access_token(user)
    payload = ts.verify_access_token(token)
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    iat = datetime.fromtimestamp(payload["iat"], tz=UTC)
    assert abs((exp - iat).total_seconds() - 1800) < 5


def test_verify_access_token_with_valid_token():
    user = _make_user()
    ts = _get_ts()
    token = ts.create_access_token(user)
    payload = ts.verify_access_token(token)
    assert payload["sub"] == str(user.id)


def test_tampered_token_raises_error():
    user = _make_user()
    ts = _get_ts()
    token = ts.create_access_token(user)
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(ValueError, match="Invalid token"):
        ts.verify_access_token(tampered)


def test_generate_refresh_token_returns_pair():
    raw, token_hash = TokenService.generate_refresh_token()
    assert isinstance(raw, str)
    assert isinstance(token_hash, str)
    assert len(raw) > 0
    assert len(token_hash) == 64


def test_create_challenge_token_has_correct_claims():
    user = _make_user()
    ts = _get_ts()
    token = ts.create_challenge_token(user)
    payload = ts.verify_challenge_token(token)
    assert payload["purpose"] == "2fa_challenge"
    assert payload["sub"] == str(user.id)
    assert payload["tenant_id"] == str(user.tenant_id)


def test_verify_expired_challenge_token_raises():
    user = _make_user()
    ts = _get_ts()
    from jose import jwt
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "purpose": "2fa_challenge",
        "exp": datetime.now(UTC) - timedelta(hours=1),
        "iat": datetime.now(UTC) - timedelta(hours=1),
        "jti": str(uuid.uuid4()),
    }
    expired = jwt.encode(payload, "a" * 32, algorithm="HS256")
    with pytest.raises(ValueError, match="Invalid challenge token"):
        ts.verify_challenge_token(expired)
