from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class EvaluacionMateria(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Evaluación vinculada directamente a materia y cohorte.

    Modela eventos de evaluación (parcial, TP, coloquio) a nivel de
    materia+cohorte, independiente del sistema de coloquios (E14).
    """

    __tablename__ = "evaluacion_materia"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="CASCADE"),
        nullable=False,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="CASCADE"),
        nullable=True,
    )
    tipo = Column(String(30), nullable=False)
    instancia = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)
    titulo = Column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_evaluacion_materia_tenant_materia", "tenant_id", "materia_id"),
    )
