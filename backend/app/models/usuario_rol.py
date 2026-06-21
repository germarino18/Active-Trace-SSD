from sqlalchemy import Column, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class UsuarioRol(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Vínculo directo Usuario <-> Rol con vigencia opcional.

    Complementa a `Asignacion` (que vincula usuario+rol+contexto académico).
    `UsuarioRol` es un vínculo simple sin contexto académico, para roles
    tenant-globales o como simplificación del ABM de usuarios.
    """

    __tablename__ = "usuario_rol"

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    rol_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rol.id", ondelete="CASCADE"),
        nullable=False,
    )
    desde = Column(Date, nullable=True)
    hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index("ix_usuario_rol_tenant_usuario", "tenant_id", "usuario_id"),
    )
