from sqlalchemy import Column, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin


class UmbralMateria(BaseMixin, TenantMixin, Base):
    __tablename__ = "umbral_materia"

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
    umbral_pct = Column(Integer, nullable=False, default=60)
    valores_aprobatorios = Column(JSONB, nullable=True)

    __table_args__ = (
        Index(
            "ix_umbral_materia_tenant_asignacion_dictado",
            "tenant_id",
            "asignacion_id",
            "dictado_id",
            unique=True,
        ),
    )
