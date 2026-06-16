from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, TenantMixin


class AlumnoConvocado(BaseMixin, TenantMixin, AuditMixin, Base):
    """Alumno habilitado para una convocatoria de coloquio (tabla intermedia).

    Permite importar alumnos a una convocatoria independientemente de
    si después reservan o no. El unique constraint garantiza que un
    alumno no se importe dos veces a la misma convocatoria (idempotencia).
    """

    __tablename__ = "alumno_convocado"

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

    __table_args__ = (
        Index(
            "ix_alumno_convocado_tenant_evaluacion",
            "tenant_id",
            "evaluacion_id",
        ),
        Index(
            "ix_alumno_convocado_tenant_alumno",
            "tenant_id",
            "alumno_id",
        ),
        UniqueConstraint(
            "evaluacion_id",
            "alumno_id",
            name="uq_alumno_convocado_evaluacion_alumno",
        ),
    )
