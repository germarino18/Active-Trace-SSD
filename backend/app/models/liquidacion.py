"""Liquidacion model — period salary settlement for a teacher (E19)."""

import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class EstadoLiquidacion(str, enum.Enum):
    ABIERTA = "Abierta"
    CERRADA = "Cerrada"


class Liquidacion(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "liquidacion"

    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="RESTRICT"),
        nullable=False,
    )
    periodo = Column(String(7), nullable=False)  # AAAA-MM
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    rol = Column(String(30), nullable=False)
    comisiones = Column(Text, nullable=True)
    monto_base = Column(Numeric(12, 2), nullable=False)
    monto_plus = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    total = Column(Numeric(12, 2), nullable=False)
    es_nexo = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    excluido_por_factura = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    estado = Column(String(20), nullable=False, default=EstadoLiquidacion.ABIERTA.value)

    __table_args__ = (
        Index(
            "ix_liquidacion_tenant_periodo_cohorte",
            "tenant_id",
            "periodo",
            "cohorte_id",
        ),
        Index(
            "ix_liquidacion_tenant_usuario_periodo",
            "tenant_id",
            "usuario_id",
            "periodo",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_liquidacion_tenant_estado",
            "tenant_id",
            "estado",
        ),
    )
