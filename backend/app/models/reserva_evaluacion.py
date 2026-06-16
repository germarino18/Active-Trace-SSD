from sqlalchemy import Column, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, TenantMixin


class ReservaEvaluacion(BaseMixin, TenantMixin, AuditMixin, Base):
    """Reserva de turno de evaluación por un ALUMNO (E14).

    Cada reserva pertenece a una `Evaluacion` y a un `Usuario` (ALUMNO).
    El control de cupo se hace en el Service con FOR UPDATE (D2).

    No tiene SoftDeleteMixin porque la cancelación se modela como cambio
    de estado (Cancelada), no como borrado lógico (D6).
    """

    __tablename__ = "reserva_evaluacion"

    evaluacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evaluacion.id", ondelete="CASCADE"),
        nullable=False,
    )
    alumno_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha_hora = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    estado = Column(
        String(20),
        nullable=False,
        default="Activa",
        server_default="Activa",
    )

    __table_args__ = (
        Index(
            "ix_reserva_evaluacion_tenant_evaluacion",
            "tenant_id",
            "evaluacion_id",
        ),
        Index(
            "ix_reserva_evaluacion_tenant_alumno",
            "tenant_id",
            "alumno_id",
        ),
        UniqueConstraint(
            "evaluacion_id",
            "alumno_id",
            name="uq_reserva_evaluacion_alumno_activa",
            sqlite_on_conflict="ABORT",  # ignored by PostgreSQL
        ),
    )
