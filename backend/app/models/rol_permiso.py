from sqlalchemy import Boolean, Column, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin


class RolPermiso(BaseMixin, TenantMixin, Base):
    __tablename__ = "rol_permiso"

    rol_id = Column(
        UUID(as_uuid=True), ForeignKey("rol.id", ondelete="CASCADE"), nullable=False
    )
    permiso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permiso.id", ondelete="CASCADE"),
        nullable=False,
    )
    es_propio = Column(Boolean, nullable=False, server_default=text("false"))

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "rol_id", "permiso_id", name="uq_rol_permiso"
        ),
    )
