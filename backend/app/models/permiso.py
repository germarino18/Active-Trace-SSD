from sqlalchemy import Column, Index, String, Text, text

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Permiso(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "permiso"

    codigo = Column(String(100), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    modulo = Column(String(50), nullable=False)

    __table_args__ = (
        Index(
            "ix_permiso_codigo_tenant",
            "tenant_id",
            "codigo",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
