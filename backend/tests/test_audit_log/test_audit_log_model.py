from app.models.audit_log import AuditLog
from app.models.mixins import BaseMixin, TenantMixin


def test_audit_log_has_expected_columns():
    columns = AuditLog.__table__.columns
    expected = {
        "tenant_id",
        "fecha_hora",
        "actor_id",
        "impersonado_id",
        "materia_id",
        "accion",
        "detalle",
        "filas_afectadas",
        "ip",
        "user_agent",
    }
    assert expected.issubset(set(columns.keys()))


def test_audit_log_materia_id_is_nullable():
    assert AuditLog.__table__.columns["materia_id"].nullable is True


def test_audit_log_uses_base_and_tenant_mixin():
    assert issubclass(AuditLog, BaseMixin)
    assert issubclass(AuditLog, TenantMixin)


def test_audit_log_has_no_deleted_at_column():
    assert "deleted_at" not in AuditLog.__table__.columns.keys()
