import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.auth import CurrentUser
from app.services.audit.audit_logger import AuditLogger


async def _create_user(db_session: AsyncSession, tenant_id):
    from app.models.user import User

    user = User(
        tenant_id=tenant_id,
        email=f"logger-{uuid.uuid4().hex[:8]}@test.edu",
        password_hash="hash",
        display_name="Logger Actor",
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


def _make_request(ip: str = "203.0.113.5", user_agent: str = "pytest-agent"):
    scope = {
        "type": "http",
        "client": (ip, 12345),
        "headers": [(b"user-agent", user_agent.encode())],
    }
    return Request(scope)


async def test_log_attribution_normal_session(db_session: AsyncSession, test_tenant):
    actor = await _create_user(db_session, test_tenant.id)
    current_user = CurrentUser(
        user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None
    )
    repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logger = AuditLogger(repository=repo)

    record = await logger.log(
        current_user=current_user,
        accion=AccionAuditoria.IMPERSONACION_INICIAR,
        detalle={"target": "someone"},
        filas_afectadas=1,
        request=_make_request(),
    )

    assert record.actor_id == actor.id
    assert record.impersonado_id is None
    assert record.tenant_id == test_tenant.id


async def test_log_attribution_impersonation_session(db_session: AsyncSession, test_tenant):
    real_actor = await _create_user(db_session, test_tenant.id)
    impersonated_user = await _create_user(db_session, test_tenant.id)
    current_user = CurrentUser(
        user_id=impersonated_user.id,
        tenant_id=test_tenant.id,
        roles=["ALUMNO"],
        actor_id=real_actor.id,
    )
    repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logger = AuditLogger(repository=repo)

    record = await logger.log(
        current_user=current_user,
        accion=AccionAuditoria.IMPERSONACION_FINALIZAR,
        detalle=None,
        filas_afectadas=0,
        request=_make_request(),
    )

    assert record.actor_id == real_actor.id
    assert record.impersonado_id == impersonated_user.id


async def test_log_impersonado_id_override_takes_precedence(
    db_session: AsyncSession, test_tenant
):
    """When starting an impersonation session (IMPERSONACION_INICIAR), the
    current session is the REAL actor's normal session (actor_id is None),
    but the audit record must reference the TARGET user being impersonated.
    An explicit `impersonado_id` override must take precedence over the
    derived-from-session attribution (D4)."""
    real_actor = await _create_user(db_session, test_tenant.id)
    target_user = await _create_user(db_session, test_tenant.id)
    current_user = CurrentUser(
        user_id=real_actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None
    )
    repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logger = AuditLogger(repository=repo)

    record = await logger.log(
        current_user=current_user,
        accion=AccionAuditoria.IMPERSONACION_INICIAR,
        detalle={"target_user_id": str(target_user.id)},
        filas_afectadas=1,
        request=_make_request(),
        impersonado_id=target_user.id,
    )

    assert record.actor_id == real_actor.id
    assert record.impersonado_id == target_user.id


async def test_log_persists_accion_detalle_filas_afectadas_and_request_metadata(
    db_session: AsyncSession, test_tenant
):
    actor = await _create_user(db_session, test_tenant.id)
    current_user = CurrentUser(
        user_id=actor.id, tenant_id=test_tenant.id, roles=["ADMIN"], actor_id=None
    )
    repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logger = AuditLogger(repository=repo)

    record = await logger.log(
        current_user=current_user,
        accion=AccionAuditoria.IMPERSONACION_INICIAR,
        detalle={"key": "value", "n": 3},
        filas_afectadas=7,
        request=_make_request(ip="198.51.100.9", user_agent="custom-agent/1.0"),
    )

    assert record.accion == AccionAuditoria.IMPERSONACION_INICIAR
    assert record.detalle == {"key": "value", "n": 3}
    assert record.filas_afectadas == 7
    assert record.ip == "198.51.100.9"
    assert record.user_agent == "custom-agent/1.0"
    assert record.materia_id is None
