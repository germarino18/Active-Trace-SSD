from sqlalchemy import Column, Date, ForeignKey, Index, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, TenantMixin


class InstanciaEncuentro(BaseMixin, TenantMixin, AuditMixin, Base):
    """Encuentro concreto (E10).

    Puede ser derivada de un `SlotEncuentro` (slot_id no nulo) o creada
    como instancia independiente (slot_id nulo, fecha y hora propios).

    `dictado_id` es el contexto académico (ADR-006, D2).
    `asignacion_id` se hereda del slot pero puede modificarse
    individualmente (D3).

    No tiene SoftDeleteMixin porque las instancias son eventos que se
    conservan como histórico aunque se cancelen.
    """

    __tablename__ = "instancia_encuentro"

    slot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("slot_encuentro.id", ondelete="SET NULL"),
        nullable=True,
    )
    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    asignacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asignacion.id", ondelete="SET NULL"),
        nullable=True,
    )
    fecha = Column(Date, nullable=False)
    hora = Column(Time(timezone=False), nullable=False)
    titulo = Column(String(255), nullable=False)
    estado = Column(
        String(20),
        nullable=False,
        default="Programado",
        server_default="Programado",
    )
    meet_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    comentario = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_instancia_tenant_dictado", "tenant_id", "dictado_id"),
        Index("ix_instancia_tenant_slot", "tenant_id", "slot_id"),
        Index("ix_instancia_tenant_estado", "tenant_id", "estado"),
    )
