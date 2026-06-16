import enum

from sqlalchemy import Column, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, TenantMixin


class TipoEvaluacion(str, enum.Enum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class EstadoEvaluacion(str, enum.Enum):
    ACTIVA = "Activa"
    CERRADA = "Cerrada"


class Evaluacion(BaseMixin, TenantMixin, AuditMixin, Base):
    """Convocatoria de evaluación / coloquio (E14).

    Define una instancia de evaluación formal con tipo, instancia,
    ventana de inscripción y cupo máximo.

    `dictado_id` es el contexto académico (ADR-006, D1).
    No tiene SoftDeleteMixin porque el cierre se modela como cambio
    de estado (Cerrada), no como borrado lógico (D6).
    """

    __tablename__ = "evaluacion"

    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo = Column(String(30), nullable=False)
    instancia = Column(String(255), nullable=False)
    dias_disponibles = Column(
        Integer, nullable=False, default=10, server_default=text("10")
    )
    cupo_maximo = Column(Integer, nullable=False)
    estado = Column(
        String(20),
        nullable=False,
        default="Activa",
        server_default="Activa",
    )

    __table_args__ = (
        Index("ix_evaluacion_tenant_dictado", "tenant_id", "dictado_id"),
        Index("ix_evaluacion_tenant_estado", "tenant_id", "estado"),
    )
