from sqlalchemy import Column, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Materia(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Materia del catálogo único del tenant (E3, ADR-006).

    Pertenece a una Carrera y Cohorte. Su puesta en cursado concreto
    (docentes, horarios) se modela como `Dictado`.
    """

    __tablename__ = "materia"

    codigo = Column(String(50), nullable=True)
    nombre = Column(String(255), nullable=False)
    estado = Column(String(20), nullable=False, default="Activa", server_default="Activa")
    carrera_id = Column(UUID(as_uuid=True), ForeignKey("carrera.id", ondelete="SET NULL"), nullable=True)
    cohorte_id = Column(UUID(as_uuid=True), ForeignKey("cohorte.id", ondelete="SET NULL"), nullable=True)

    carrera = relationship("Carrera", lazy="select")
    cohorte = relationship("Cohorte", lazy="select")

    __table_args__ = (
        Index(
            "ix_materia_codigo_tenant",
            "tenant_id",
            "codigo",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_materia_carrera", "carrera_id"),
        Index("ix_materia_cohorte", "cohorte_id"),
    )
