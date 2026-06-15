from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin


class VersionPadron(BaseMixin, TenantMixin, Base):
    __tablename__ = "version_padron"

    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    cargado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    cargado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    activa = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    __table_args__ = (
        Index(
            "ix_version_padron_tenant_dictado",
            "tenant_id",
            "dictado_id",
        ),
        Index(
            "ix_version_padron_dictado_activa",
            "tenant_id",
            "dictado_id",
            unique=True,
            postgresql_where=text("activa = true"),
        ),
    )
