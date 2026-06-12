from sqlalchemy import Column, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Rol(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "rol"

    codigo = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ix_rol_codigo_tenant",
            "tenant_id",
            "codigo",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
