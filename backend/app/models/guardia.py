from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, TenantMixin


class Guardia(BaseMixin, TenantMixin, AuditMixin, Base):
    """Registro de guardia de atención a alumnos (E11).

    `asignacion_id` es no nullable porque siempre identifica quién cubre
    la guardia (D4). `dictado_id` es el contexto académico (ADR-006, D2).

    No tiene SoftDeleteMixin porque las guardias se conservan como
    histórico aunque se cancelen.
    """

    __tablename__ = "guardia"

    asignacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asignacion.id", ondelete="CASCADE"),
        nullable=False,
    )
    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    dia = Column(String(20), nullable=False)
    horario = Column(String(50), nullable=False)
    estado = Column(
        String(20),
        nullable=False,
        default="Pendiente",
        server_default="Pendiente",
    )
    comentarios = Column(Text, nullable=True)
    creada_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_guardia_tenant_dictado", "tenant_id", "dictado_id"),
        Index("ix_guardia_tenant_asignacion", "tenant_id", "asignacion_id"),
        Index("ix_guardia_tenant_estado", "tenant_id", "estado"),
    )
