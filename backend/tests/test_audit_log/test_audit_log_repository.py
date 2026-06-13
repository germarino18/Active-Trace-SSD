import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_log_repository import AuditLogRepository


async def _create_user(db_session: AsyncSession, tenant_id):
    from app.models.user import User

    user = User(
        tenant_id=tenant_id,
        email=f"audit-{uuid.uuid4().hex[:8]}@test.edu",
        password_hash="hash",
        display_name="Audit Actor",
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def test_create_persists_tenant_scoped_record(db_session: AsyncSession, test_tenant):
    actor = await _create_user(db_session, test_tenant.id)
    repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)

    record = await repo.create({
        "actor_id": actor.id,
        "accion": "IMPERSONACION_INICIAR",
        "detalle": {"foo": "bar"},
        "filas_afectadas": 1,
        "ip": "127.0.0.1",
        "user_agent": "pytest",
    })

    assert record.id is not None
    assert record.tenant_id == test_tenant.id
    assert record.accion == "IMPERSONACION_INICIAR"


def test_repository_exposes_no_update_or_delete_methods():
    assert not hasattr(AuditLogRepository, "update")
    assert not hasattr(AuditLogRepository, "soft_delete")
    assert not hasattr(AuditLogRepository, "hard_delete")


async def test_tenant_scoped_list_returns_only_caller_tenant_records(
    db_session: AsyncSession, test_tenant, another_tenant
):
    actor_a = await _create_user(db_session, test_tenant.id)
    actor_b = await _create_user(db_session, another_tenant.id)

    repo_a = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    repo_b = AuditLogRepository(session=db_session, tenant_id=another_tenant.id)

    await repo_a.create({
        "actor_id": actor_a.id,
        "accion": "IMPERSONACION_INICIAR",
        "filas_afectadas": 1,
    })
    await repo_b.create({
        "actor_id": actor_b.id,
        "accion": "IMPERSONACION_FINALIZAR",
        "filas_afectadas": 1,
    })

    records_a = await repo_a.find_all()
    assert all(r.tenant_id == test_tenant.id for r in records_a)
    assert any(r.accion == "IMPERSONACION_INICIAR" for r in records_a)
    assert not any(r.accion == "IMPERSONACION_FINALIZAR" for r in records_a)
