from sqlalchemy import Column, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, TenantMixin


class ResultadoEvaluacion(BaseMixin, TenantMixin, AuditMixin, Base):
    """Resultado/nota de un ALUMNO en una evaluación (E14).

    Inmutable una vez registrado: no se modifica ni elimina (D6).
    Un ALUMNO tiene UN SOLO resultado por evaluación (unique constraint).
    """

    __tablename__ = "resultado_evaluacion"

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
    nota_final = Column(String(255), nullable=False)

    __table_args__ = (
        Index(
            "ix_resultado_evaluacion_tenant_evaluacion",
            "tenant_id",
            "evaluacion_id",
        ),
        Index(
            "ix_resultado_evaluacion_tenant_alumno",
            "tenant_id",
            "alumno_id",
        ),
        UniqueConstraint(
            "evaluacion_id",
            "alumno_id",
            name="uq_resultado_evaluacion_alumno",
        ),
    )
