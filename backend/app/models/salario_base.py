"""SalarioBase model — salary base by role with temporal validity (E17)."""

import enum

from sqlalchemy import Column, Date, Enum, Index, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class RolSalario(str, enum.Enum):
    PROFESOR = "PROFESOR"
    TUTOR = "TUTOR"
    NEXO = "NEXO"
    COORDINADOR = "COORDINADOR"


class SalarioBase(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "salario_base"

    rol = Column(String(30), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index(
            "ix_salario_base_tenant_rol_vigencia",
            "tenant_id",
            "rol",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_salario_base_tenant_desde",
            "tenant_id",
            "desde",
        ),
    )
