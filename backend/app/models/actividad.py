"""Actividad model — representa una actividad evaluable dentro de un dictado (C-25).

Una actividad es la unidad de evaluación dentro de un dictado (TP, parcial, etc.).
Calificacion.actividad (string legacy) se mantiene intacto; actividad_id es la FK
opcional que apunta a esta tabla.
"""

from sqlalchemy import Column, Date, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Actividad(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Actividad evaluable dentro de un dictado.

    `tipo` es un string libre (ej. "TP", "Parcial", "Final", "Coloquio").
    `fecha_limite` es nullable — actividades sin fecha_limite no generan
    atrasado-null, sólo desaprobadas.
    """

    __tablename__ = "actividad"

    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False)
    fecha_limite = Column(Date, nullable=True)

    __table_args__ = (
        Index("ix_actividad_tenant_dictado", "tenant_id", "dictado_id"),
    )
