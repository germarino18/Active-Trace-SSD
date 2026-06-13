from sqlalchemy import Column, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Dictado(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Instancia de una materia en una carrera x cohorte concreta (ADR-006).

    Entidad raíz (D1): el re-anclaje de entidades downstream (Asignacion,
    Padron, Encuentro, etc.) a `dictado_id` se hace en sus respectivos
    changes (C-07+), no acá.

    La terna `(tenant_id, materia_id, carrera_id, cohorte_id)` es única
    entre dictados vivos (D4). `Dictado.carrera_id` MUST coincidir con
    `Cohorte.carrera_id` de la cohorte referida (D2, validado en Service).
    """

    __tablename__ = "dictado"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="CASCADE"),
        nullable=False,
    )
    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carrera.id", ondelete="CASCADE"),
        nullable=False,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="CASCADE"),
        nullable=False,
    )
    estado = Column(String(20), nullable=False, default="Activo", server_default="Activo")

    __table_args__ = (
        Index(
            "ix_dictado_terna_tenant",
            "tenant_id",
            "materia_id",
            "carrera_id",
            "cohorte_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
