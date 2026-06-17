from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class HiloParticipante(Base):
    """Participante de un hilo de conversación (C-20).

    PK compuesta natural (hilo_id, usuario_id). No hereda mixins estándar
    porque la PK no es `id` UUID. `ultima_visto` permite determinar si hay
    mensajes no leídos.
    """

    __tablename__ = "hilo_participante"
    __table_args__ = (
        PrimaryKeyConstraint("hilo_id", "usuario_id"),
    )

    hilo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("hilo_conversacion.id"),
        nullable=False,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id"),
        nullable=False,
    )
    ultima_visto = Column(DateTime(timezone=True), nullable=True)
