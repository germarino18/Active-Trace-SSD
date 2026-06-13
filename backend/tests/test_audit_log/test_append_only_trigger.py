"""DB-level append-only enforcement (D2): a raw SQL UPDATE or DELETE against
`audit_log` must be rejected by the PostgreSQL trigger installed in
migration 004 — independent of the application/repository layer.
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_log_repository import AuditLogRepository


async def _create_user(db_session: AsyncSession, tenant_id):
    from app.models.user import User

    user = User(
        tenant_id=tenant_id,
        email=f"trigger-{uuid.uuid4().hex[:8]}@test.edu",
        password_hash="hash",
        display_name="Trigger Actor",
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def audit_record(db_session: AsyncSession, test_tenant):
    actor = await _create_user(db_session, test_tenant.id)
    repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    record = await repo.create({
        "actor_id": actor.id,
        "accion": "IMPERSONACION_INICIAR",
        "detalle": {"k": "v"},
        "filas_afectadas": 1,
    })
    await db_session.commit()
    return record


async def test_raw_sql_update_is_rejected(db_session: AsyncSession, audit_record):
    record_id = audit_record.id

    with pytest.raises(DBAPIError):
        await db_session.execute(
            text("UPDATE audit_log SET accion = 'TAMPERED' WHERE id = :id"),
            {"id": record_id},
        )
    await db_session.rollback()

    result = await db_session.execute(
        text("SELECT accion FROM audit_log WHERE id = :id"), {"id": record_id}
    )
    assert result.scalar() == "IMPERSONACION_INICIAR"


async def test_raw_sql_delete_is_rejected(db_session: AsyncSession, audit_record):
    record_id = audit_record.id

    with pytest.raises(DBAPIError):
        await db_session.execute(
            text("DELETE FROM audit_log WHERE id = :id"),
            {"id": record_id},
        )
    await db_session.rollback()

    result = await db_session.execute(
        text("SELECT 1 FROM audit_log WHERE id = :id"), {"id": record_id}
    )
    assert result.scalar() == 1
