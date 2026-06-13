from sqlalchemy import Column, Index, String, text

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Materia(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Materia del catálogo único del tenant (E3, ADR-006).

    Solo definición de catálogo; su puesta en cursado se modela como
    `Dictado`. `codigo` es único por tenant entre materias vivas (D4).
    """

    __tablename__ = "materia"

    codigo = Column(String(50), nullable=False)
    nombre = Column(String(255), nullable=False)
    estado = Column(String(20), nullable=False, default="Activa", server_default="Activa")

    __table_args__ = (
        Index(
            "ix_materia_codigo_tenant",
            "tenant_id",
            "codigo",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
