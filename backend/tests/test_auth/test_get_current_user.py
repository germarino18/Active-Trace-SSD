import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.api.dependencies.auth import get_current_user
from app.schemas.auth import CurrentUser
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


# ── Task 5.4: CurrentUser.actor_id ───────────────────────────────────────


def test_current_user_actor_id_defaults_to_none():
    cu = CurrentUser(user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), roles=["ALUMNO"])
    assert cu.actor_id is None


def test_current_user_accepts_actor_id():
    actor_id = uuid.uuid4()
    cu = CurrentUser(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), roles=["ADMIN"], actor_id=actor_id
    )
    assert cu.actor_id == actor_id


# ── Task 5.5: get_current_user reads actor_id from payload ──────────────


# Must match the test settings fixture's SECRET_KEY (tests/conftest.py)
_TEST_SECRET = "a" * 32


def _make_request():
    from starlette.requests import Request

    from app.core.config import Settings

    class _FakeAppState:
        settings = Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/activia_trace",
            SECRET_KEY=_TEST_SECRET,
            ENCRYPTION_KEY="a" * 64,
            OTEL_ENABLED=False,
        )

    class _FakeApp:
        state = _FakeAppState()

    scope = {"type": "http", "headers": [], "app": _FakeApp()}
    return Request(scope)


async def test_get_current_user_normal_token_has_no_actor_id():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    token = _make_token(user_id=user_id, tenant_id=tenant_id, secret=_TEST_SECRET)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    current_user = await get_current_user(
        request=_make_request(), credentials=credentials, db=None
    )

    assert current_user.user_id == user_id
    assert current_user.actor_id is None


async def test_get_current_user_impersonation_token_has_actor_id():
    real_actor_id = uuid.uuid4()
    target_user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    payload = {
        "sub": str(target_user_id),
        "tenant_id": str(tenant_id),
        "roles": ["ALUMNO"],
        "actor_id": str(real_actor_id),
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, _TEST_SECRET, algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    current_user = await get_current_user(
        request=_make_request(), credentials=credentials, db=None
    )

    assert current_user.user_id == target_user_id
    assert current_user.actor_id == real_actor_id
