"""ClavePlus model — category of subjects for salary plus (E22)."""

from sqlalchemy import Column, Date, Index, String, text

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class ClavePlus(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "clave_plus"

    codigo = Column(String(30), nullable=False)
    descripcion = Column(String(255), nullable=False)
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index(
            "ix_clave_plus_tenant_codigo",
            "tenant_id",
            "codigo",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
