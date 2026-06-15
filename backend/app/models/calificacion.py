import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin


class CalificacionOrigen(str, enum.Enum):
    IMPORTADO = "Importado"
    MANUAL = "Manual"


class Calificacion(BaseMixin, TenantMixin, Base):
    __tablename__ = "calificacion"

    entrada_padron_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entrada_padron.id", ondelete="CASCADE"),
        nullable=False,
    )
    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    actividad = Column(String(255), nullable=False)
    nota_numerica = Column(Numeric(5, 2), nullable=True)
    nota_textual = Column(String(100), nullable=True)
    aprobado = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    origen = Column(String(20), nullable=False, default="Importado", server_default="Importado")
    importado_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_calificacion_tenant_dictado", "tenant_id", "dictado_id"),
        Index("ix_calificacion_tenant_entrada", "tenant_id", "entrada_padron_id"),
    )
