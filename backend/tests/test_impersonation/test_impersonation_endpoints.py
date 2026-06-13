from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.models.audit_log import AuditLog
from tests.helpers import cleanup_permission_cache
from tests.test_impersonation.conftest import _FALLBACK_SECRET, make_token


async def _audit_records(db_session: AsyncSession, tenant_id, accion: str):
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.tenant_id == tenant_id, AuditLog.accion == accion)
    )
    return list(result.unique().scalars().all())


# ── 7.1: authorized same-tenant impersonation start ──────────────────────


async def test_authorized_impersonate_issues_token_with_actor_id(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    alumno_user,
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.post(
        f"/api/v1/auth/impersonate/{alumno_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    payload = jwt.decode(
        data["access_token"], _FALLBACK_SECRET, algorithms=["HS256"]
    )
    assert payload["sub"] == str(alumno_user.id)
    assert payload["actor_id"] == str(admin_user.id)

    await db_session.commit()
    records = await _audit_records(
        db_session, seeded_tenant.id, AccionAuditoria.IMPERSONACION_INICIAR
    )
    assert len(records) == 1
    assert records[0].actor_id == admin_user.id
    assert records[0].impersonado_id == alumno_user.id


# ── 7.2: unauthorized caller → 403, fail-closed ──────────────────────────


async def test_unauthorized_caller_gets_403_no_token_no_audit(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    alumno_user,
    admin_user,
):
    cleanup_permission_cache()
    token = make_token(alumno_user)  # ALUMNO lacks impersonacion:usar

    response = await client.post(
        f"/api/v1/auth/impersonate/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "access_token" not in response.json()

    await db_session.commit()
    records = await _audit_records(
        db_session, seeded_tenant.id, AccionAuditoria.IMPERSONACION_INICIAR
    )
    assert len(records) == 0


# ── 7.3: cross-tenant target rejected ────────────────────────────────────


async def test_cross_tenant_target_is_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    another_tenant_user,
):
    cleanup_permission_cache()
    token = make_token(admin_user)

    response = await client.post(
        f"/api/v1/auth/impersonate/{another_tenant_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (403, 404)
    assert "access_token" not in response.json()


# ── 7.4: end impersonation restores real actor ───────────────────────────


async def test_impersonate_end_restores_real_actor(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    alumno_user,
):
    cleanup_permission_cache()
    await db_session.commit()
    impersonation_token = make_token(alumno_user, actor_id=admin_user.id)

    response = await client.post(
        "/api/v1/auth/impersonate/end",
        headers={"Authorization": f"Bearer {impersonation_token}"},
    )

    assert response.status_code == 200, response.json()
    data = response.json()
    payload = jwt.decode(
        data["access_token"], _FALLBACK_SECRET, algorithms=["HS256"]
    )
    assert payload["sub"] == str(admin_user.id)
    assert "actor_id" not in payload

    await db_session.commit()
    records = await _audit_records(
        db_session, seeded_tenant.id, AccionAuditoria.IMPERSONACION_FINALIZAR
    )
    assert len(records) == 1
    assert records[0].actor_id == admin_user.id
    assert records[0].impersonado_id == alumno_user.id


# ── 7.5: end on a normal token (no actor_id) is rejected ─────────────────


async def test_impersonate_end_on_normal_token_is_rejected(
    client: AsyncClient,
    seeded_tenant,
    admin_user,
):
    cleanup_permission_cache()
    normal_token = make_token(admin_user)  # no actor_id

    response = await client.post(
        "/api/v1/auth/impersonate/end",
        headers={"Authorization": f"Bearer {normal_token}"},
    )

    assert response.status_code in (400, 401, 403)


# ── 7.7: act-as header on a normal request is ignored ────────────────────


async def test_act_as_header_on_normal_request_is_ignored(
    client: AsyncClient,
    seeded_tenant,
    admin_user,
    alumno_user,
):
    cleanup_permission_cache()
    token = make_token(admin_user)

    response = await client.post(
        "/api/auth/logout",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Act-As": str(alumno_user.id),
        },
        json={"refresh_token": "irrelevant"},
    )

    # Identity must resolve from the verified JWT (admin_user), not the header.
    # The endpoint should process normally as admin_user (200), proving the
    # act-as header had no effect on identity resolution.
    assert response.status_code == 200
