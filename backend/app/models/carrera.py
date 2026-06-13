from sqlalchemy import Column, Index, String, text

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Carrera(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Carrera del catálogo del tenant (E1).

    `codigo` es único por tenant entre carreras vivas (D4). `estado` es
    Activa/Inactiva (D7), modelado como String validado en Pydantic.
    """

    __tablename__ = "carrera"

    codigo = Column(String(50), nullable=False)
    nombre = Column(String(255), nullable=False)
    estado = Column(String(20), nullable=False, default="Activa", server_default="Activa")

    __table_args__ = (
        Index(
            "ix_carrera_codigo_tenant",
            "tenant_id",
            "codigo",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
