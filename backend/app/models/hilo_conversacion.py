from sqlalchemy import Column, String

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class HiloConversacion(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Hilo de conversación en la mensajería interna entre usuarios (C-20).

    Los participantes se modelan en HiloParticipante (PK compuesta).
    Los mensajes individuales en Mensaje.
    """

    __tablename__ = "hilo_conversacion"

    asunto = Column(String(255), nullable=False)
