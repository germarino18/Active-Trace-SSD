"""SalarioPlus model — additional salary by group and role with temporal validity (E18)."""

from sqlalchemy import Column, Date, Index, Numeric, String, text

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class SalarioPlus(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "salario_plus"

    grupo = Column(String(50), nullable=False)
    rol = Column(String(30), nullable=False)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index(
            "ix_salario_plus_tenant_grupo_rol_vigencia",
            "tenant_id",
            "grupo",
            "rol",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_salario_plus_tenant_desde",
            "tenant_id",
            "desde",
        ),
    )
