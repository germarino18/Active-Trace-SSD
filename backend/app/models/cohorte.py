from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Cohorte(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Cohorte de una carrera (E2).

    El par `(tenant_id, carrera_id, nombre)` es único entre cohortes
    vivas (D4). Una cohorte "abierta" tiene `vig_hasta IS NULL`; una
    carrera Inactiva no admite cohortes abiertas (D5).
    """

    __tablename__ = "cohorte"

    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carrera.id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    anio = Column(Integer, nullable=True)
    vig_desde = Column(Date, nullable=True)
    vig_hasta = Column(Date, nullable=True)
    estado = Column(String(20), nullable=False, default="Activa", server_default="Activa")

    __table_args__ = (
        Index(
            "ix_cohorte_nombre_tenant",
            "tenant_id",
            "carrera_id",
            "nombre",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
