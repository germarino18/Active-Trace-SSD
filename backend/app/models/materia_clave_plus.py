"""MateriaClavePlus model — assigns a ClavePlus to a Materia with temporal validity (E23)."""

from sqlalchemy import Column, Date, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class MateriaClavePlus(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "materia_clave_plus"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="CASCADE"),
        nullable=False,
    )
    clave_plus_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clave_plus.id", ondelete="CASCADE"),
        nullable=False,
    )
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index(
            "ix_materia_clave_plus_tenant_materia",
            "tenant_id",
            "materia_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_materia_clave_plus_tenant_clave",
            "tenant_id",
            "clave_plus_id",
        ),
    )
