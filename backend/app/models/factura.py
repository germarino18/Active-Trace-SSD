"""Factura model — invoice from teachers who invoice their fees (E20)."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, text, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class EstadoFactura(str, enum.Enum):
    PENDIENTE = "Pendiente"
    ABONADA = "Abonada"


class Factura(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "factura"

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    periodo = Column(String(7), nullable=False)  # AAAA-MM
    detalle = Column(Text, nullable=True)
    referencia_archivo = Column(String(500), nullable=True)
    tamano_kb = Column(Numeric(10, 2), nullable=True)
    estado = Column(String(20), nullable=False, default=EstadoFactura.PENDIENTE.value)
    cargada_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    abonada_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "ix_factura_tenant_usuario",
            "tenant_id",
            "usuario_id",
        ),
        Index(
            "ix_factura_tenant_periodo",
            "tenant_id",
            "periodo",
        ),
        Index(
            "ix_factura_tenant_estado",
            "tenant_id",
            "estado",
        ),
    )
