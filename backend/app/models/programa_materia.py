from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import BaseMixin, SoftDeleteMixin, TenantMixin


class ProgramaMateria(BaseMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "programa_materia"

    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    titulo = Column(String, nullable=False)
    referencia_archivo = Column(String, nullable=False)
    cargado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_programa_materia_tenant_dictado",
            "tenant_id",
            "dictado_id",
            unique=True,
        ),
    )
