from sqlalchemy import ARRAY, Column, Date, ForeignKey, Index, String, VARCHAR, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Asignacion(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Vínculo Usuario <-> Rol <-> contexto académico con vigencia (E5).

    `rol` es uno de ALUMNO|PROFESOR|TUTOR|COORDINADOR|NEXO|ADMIN|FINANZAS
    (los 7 códigos sembrados en C-04). El contexto académico
    (`dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`) es nullable; todos
    NULL significa rol tenant-global. `responsable_id` modela la jerarquía
    docente (a quién rinde cuentas el asignado).

    `estado_vigencia` (Vigente|Vencida) es DERIVADO por fechas (D3), NO una
    columna: Vigente <=> `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`.
    Se calcula en Service/repository (`AsignacionRepository.find_roles_vigentes`),
    nunca se persiste.

    Soft-delete siempre (regla dura #13): una asignación vencida se conserva
    en el histórico y no otorga permisos (no se borra).
    """

    __tablename__ = "asignacion"

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    rol = Column(String(50), nullable=False)
    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=True,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="CASCADE"),
        nullable=True,
    )
    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carrera.id", ondelete="CASCADE"),
        nullable=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="CASCADE"),
        nullable=True,
    )
    comisiones = Column(ARRAY(VARCHAR), nullable=False, server_default=text("'{}'::varchar[]"))
    responsable_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=True,
    )
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index("ix_asignacion_usuario_tenant", "tenant_id", "usuario_id"),
        Index("ix_asignacion_rol_tenant", "tenant_id", "rol"),
    )
