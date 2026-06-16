import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class TareaEstado(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    RESUELTA = "RESUELTA"
    CANCELADA = "CANCELADA"


class Tarea(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "tarea"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="SET NULL"),
        nullable=True,
    )
    asignado_a = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    asignado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    estado = Column(
        String(20), nullable=False, default=TareaEstado.PENDIENTE.value
    )
    descripcion = Column(Text, nullable=False)
    contexto_id = Column(UUID(as_uuid=True), nullable=True)

    comentarios = relationship(
        "ComentarioTarea",
        foreign_keys="ComentarioTarea.tarea_id",
        order_by="ComentarioTarea.creado_at",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_tarea_tenant_asignado_estado", "tenant_id", "asignado_a", "estado"),
        Index("ix_tarea_tenant_estado_materia", "tenant_id", "estado", "materia_id"),
    )


class ComentarioTarea(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "comentario_tarea"

    tarea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tarea.id", ondelete="CASCADE"),
        nullable=False,
    )
    autor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    texto = Column(Text, nullable=False)
    creado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_comentario_tarea_tarea_creado", "tarea_id", "creado_at"),
    )
