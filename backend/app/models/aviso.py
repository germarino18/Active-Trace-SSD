import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class AlcanceAviso(str, enum.Enum):
    GLOBAL = "GLOBAL"
    POR_MATERIA = "POR_MATERIA"
    POR_COHORTE = "POR_COHORTE"
    POR_ROL = "POR_ROL"


class SeveridadAviso(str, enum.Enum):
    INFO = "INFO"
    ADVERTENCIA = "ADVERTENCIA"
    CRITICO = "CRITICO"


class Aviso(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "aviso"

    alcance = Column(String(20), nullable=False)
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="SET NULL"),
        nullable=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="SET NULL"),
        nullable=True,
    )
    rol_destino = Column(String(50), nullable=True)
    severidad = Column(String(20), nullable=False, default=SeveridadAviso.INFO.value)
    titulo = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=False)
    inicio_en = Column(DateTime(timezone=True), nullable=False)
    fin_en = Column(DateTime(timezone=True), nullable=False)
    orden = Column(Integer, nullable=False, default=0, server_default=text("0"))
    activo = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    requiere_ack = Column(Boolean, nullable=False, default=False, server_default=text("false"))

    __table_args__ = (
        Index("ix_aviso_tenant_alcance_activo", "tenant_id", "alcance", "activo"),
        Index("ix_aviso_tenant_materia", "tenant_id", "materia_id"),
        Index("ix_aviso_tenant_cohorte", "tenant_id", "cohorte_id"),
    )


class AcknowledgmentAviso(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "acknowledgment_aviso"

    aviso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("aviso.id", ondelete="CASCADE"),
        nullable=False,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    confirmado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_ack_aviso_aviso_usuario",
            "aviso_id",
            "usuario_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_ack_aviso_tenant_aviso", "tenant_id", "aviso_id"),
        Index("ix_ack_aviso_tenant_usuario", "tenant_id", "usuario_id"),
    )
