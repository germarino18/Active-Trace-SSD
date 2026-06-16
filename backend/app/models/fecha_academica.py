import enum

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class TipoFechaAcademica(str, enum.Enum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class FechaAcademica(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "fecha_academica"

    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo = Column(String(30), nullable=False)
    numero = Column(Integer, nullable=False)
    periodo = Column(String(20), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False)
    titulo = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_fecha_academica_tenant_dictado", "tenant_id", "dictado_id"),
        Index("ix_fecha_academica_dictado_periodo", "dictado_id", "periodo"),
        UniqueConstraint(
            "tenant_id",
            "dictado_id",
            "tipo",
            "numero",
            name="uq_fecha_tenant_dictado_tipo_numero",
        ),
    )
