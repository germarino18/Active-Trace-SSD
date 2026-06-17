from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Mensaje(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Mensaje individual dentro de un hilo de conversación (C-20)."""

    __tablename__ = "mensaje"

    hilo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("hilo_conversacion.id"),
        nullable=False,
    )
    remitente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id"),
        nullable=False,
    )
    contenido = Column(Text, nullable=False)
