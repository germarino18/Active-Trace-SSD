from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin


class AuditLog(BaseMixin, TenantMixin, Base):
    """Append-only audit trail entry (E-AUD).

    No `SoftDeleteMixin`: this table is append-only by design, enforced
    both by this repository's missing mutation surface and by a
    PostgreSQL trigger (migration 004) that rejects UPDATE/DELETE.
    """

    __tablename__ = "audit_log"

    fecha_hora = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    impersonado_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    materia_id = Column(UUID(as_uuid=True), nullable=True)
    accion = Column(String(100), nullable=False)
    detalle = Column(JSONB, nullable=True)
    filas_afectadas = Column(Integer, nullable=True)
    ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_audit_log_tenant_id", "tenant_id"),
        Index("ix_audit_log_fecha_hora", "fecha_hora"),
    )
