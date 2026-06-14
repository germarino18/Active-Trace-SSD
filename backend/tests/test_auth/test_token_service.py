import datetime
import uuid
from datetime import UTC, datetime as dt, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService

_HOY = datetime.date.today()


async def _make_user(db_session: AsyncSession, tenant_id, roles=None, email=None) -> User:
    pw = PasswordService()
    email = email or f"{uuid.uuid4().hex}@example.com"
    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=pw.hash_password("Password123!"),
        display_name="Test User",
        roles=roles or [],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def _make_usuario_con_asignacion(
    db_session: AsyncSession, tenant_id, user: User, rol: str, *, desde=None, hasta=None
) -> Usuario:
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await usuario_repo.create({"user_id": user.id, "nombre": "N", "apellidos": "A"})

    asignacion_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    await asignacion_repo.create(
        {
            "usuario_id": usuario.id,
            "rol": rol,
            "desde": desde or (_HOY - datetime.timedelta(days=1)),
            "hasta": hasta,
        }
    )
    return usuario


def _get_ts(secret="a" * 32):
    ts = TokenService()
    ts._secret = secret
    ts._algorithm = "HS256"
    ts._access_token_ttl = timedelta(minutes=30)
    ts._challenge_token_ttl = timedelta(minutes=5)
    return ts


def _make_user_in_memory(tenant_id=None):
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant_id or uuid.uuid4(),
        email="test@example.com",
        password_hash="hash",
        display_name="Test User",
        roles=["ALUMNO"],
    )


# ── 6.2 RED: roles claim derives from Vigente asignaciones, NOT users.roles ─


async def test_create_access_token_roles_come_from_vigente_asignaciones(
    db_session: AsyncSession, test_tenant
):
    """A user with `users.roles=["ALUMNO"]` (stale/deprecated, D3) but a
    Vigente PROFESOR asignacion gets `roles=["PROFESOR"]` in the JWT — the
    claim is sourced from Asignacion, not from `users.roles`."""
    user = await _make_user(db_session, test_tenant.id, roles=["ALUMNO"])
    await _make_usuario_con_asignacion(db_session, test_tenant.id, user, "PROFESOR")

    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)

    assert payload["roles"] == ["PROFESOR"]


async def test_create_access_token_excludes_vencida_asignacion_role(
    db_session: AsyncSession, test_tenant
):
    """A user whose only PROFESOR asignacion is Vencida gets no PROFESOR in
    the `roles` claim (spec: jwt-tokens, Scenario "Expired assignments are
    excluded from the roles claim")."""
    user = await _make_user(db_session, test_tenant.id, roles=["PROFESOR"])
    await _make_usuario_con_asignacion(
        db_session,
        test_tenant.id,
        user,
        "PROFESOR",
        desde=_HOY - datetime.timedelta(days=60),
        hasta=_HOY - datetime.timedelta(days=1),
    )

    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)

    assert "PROFESOR" not in payload["roles"]
    assert payload["roles"] == []


async def test_create_access_token_user_without_usuario_has_empty_roles(
    db_session: AsyncSession, test_tenant
):
    """A user with no `Usuario` profile at all (no backfill, no asignacion)
    gets an empty `roles` claim — fail-closed (regla dura #10), not a
    fallback to `users.roles`."""
    user = await _make_user(db_session, test_tenant.id, roles=["ADMIN"])

    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)

    assert payload["roles"] == []


async def test_create_access_token_multirol_returns_distinct_sorted_roles(
    db_session: AsyncSession, test_tenant
):
    """Multiple Vigente asignaciones with different roles all appear in the
    claim, DISTINCT and order-independent (sorted for determinism)."""
    user = await _make_user(db_session, test_tenant.id, roles=[])
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuario = await usuario_repo.create({"user_id": user.id, "nombre": "N", "apellidos": "A"})
    asignacion_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
    for rol in ("PROFESOR", "TUTOR"):
        await asignacion_repo.create(
            {
                "usuario_id": usuario.id,
                "rol": rol,
                "desde": _HOY - datetime.timedelta(days=1),
                "hasta": None,
            }
        )

    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)

    assert payload["roles"] == ["PROFESOR", "TUTOR"]


# ── Pre-existing TokenService tests (now async w/ db_session) ────────────


async def test_create_access_token_has_correct_claims(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id)
    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)
    assert payload["sub"] == str(user.id)
    assert payload["tenant_id"] == str(user.tenant_id)
    assert payload["roles"] == []
    assert "exp" in payload
    assert "iat" in payload


async def test_create_access_token_without_actor_id_has_no_actor_id_claim(
    db_session: AsyncSession, test_tenant
):
    user = await _make_user(db_session, test_tenant.id)
    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)
    assert "actor_id" not in payload


async def test_create_access_token_with_actor_id_embeds_claim(
    db_session: AsyncSession, test_tenant
):
    user = await _make_user(db_session, test_tenant.id)
    actor_id = uuid.uuid4()
    ts = _get_ts()
    token = await ts.create_access_token(user, db_session, actor_id=actor_id)
    payload = ts.verify_access_token(token)
    assert payload["actor_id"] == str(actor_id)
    assert payload["sub"] == str(user.id)
    assert "jti" in payload


async def test_access_token_expires_in_30_minutes(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id)
    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)
    exp = dt.fromtimestamp(payload["exp"], tz=UTC)
    iat = dt.fromtimestamp(payload["iat"], tz=UTC)
    assert abs((exp - iat).total_seconds() - 1800) < 5


async def test_verify_access_token_with_valid_token(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id)
    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
    payload = ts.verify_access_token(token)
    assert payload["sub"] == str(user.id)


async def test_tampered_token_raises_error(db_session: AsyncSession, test_tenant):
    user = await _make_user(db_session, test_tenant.id)
    ts = _get_ts()
    token = await ts.create_access_token(user, db_session)
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
    user = _make_user_in_memory()
    ts = _get_ts()
    token = ts.create_challenge_token(user)
    payload = ts.verify_challenge_token(token)
    assert payload["purpose"] == "2fa_challenge"
    assert payload["sub"] == str(user.id)
    assert payload["tenant_id"] == str(user.tenant_id)


def test_verify_expired_challenge_token_raises():
    user = _make_user_in_memory()
    ts = _get_ts()
    from jose import jwt
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "purpose": "2fa_challenge",
        "exp": dt.now(UTC) - timedelta(hours=1),
        "iat": dt.now(UTC) - timedelta(hours=1),
        "jti": str(uuid.uuid4()),
    }
    expired = jwt.encode(payload, "a" * 32, algorithm="HS256")
    with pytest.raises(ValueError, match="Invalid challenge token"):
        ts.verify_challenge_token(expired)
