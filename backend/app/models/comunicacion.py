import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin
from app.core.crypto import EncryptedString


class ComunicacionEstado(str, enum.Enum):
    PENDIENTE = "Pendiente"
    ENVIANDO = "Enviando"
    ENVIADO = "Enviado"
    ERROR = "Error"
    CANCELADO = "Cancelado"


class Comunicacion(BaseMixin, TenantMixin, Base):
    __tablename__ = "comunicacion"

    enviado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="CASCADE"),
        nullable=False,
    )
    destinatario = Column(EncryptedString, nullable=False)
    destinatario_hash = Column(String(64), nullable=False)
    asunto = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=False)
    estado = Column(
        String(20),
        nullable=False,
        default=ComunicacionEstado.PENDIENTE.value,
        server_default=text("'Pendiente'"),
    )
    lote_id = Column(UUID(as_uuid=True), nullable=False)
    enviado_at = Column(DateTime(timezone=True), nullable=True)
    reintentos = Column(Integer, nullable=False, default=0, server_default=text("0"))

    __table_args__ = (
        Index("ix_comunicacion_tenant_lote", "tenant_id", "lote_id"),
        Index("ix_comunicacion_tenant_estado", "tenant_id", "estado"),
    )
