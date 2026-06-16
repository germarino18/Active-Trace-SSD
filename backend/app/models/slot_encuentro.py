import enum

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String, Time, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class DiaSemana(str, enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


class SlotEncuentro(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Plantilla de encuentro recurrente (E9).

    Define un slot semanal con día, hora, fecha de inicio y cantidad de
    instancias a generar. `cant_semanas = 0` + `fecha_unica` no nula indica
    un encuentro único sin recurrencia.

    `dictado_id` es el contexto académico (ADR-006, D2).
    `asignacion_id` es nullable porque un COORDINADOR puede crear slots
    que serán cubiertos por otro docente (D3).
    """

    __tablename__ = "slot_encuentro"

    dictado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dictado.id", ondelete="CASCADE"),
        nullable=False,
    )
    asignacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asignacion.id", ondelete="SET NULL"),
        nullable=True,
    )
    titulo = Column(String(255), nullable=False)
    hora = Column(Time(timezone=False), nullable=False)
    dia_semana = Column(String(20), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    cant_semanas = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    fecha_unica = Column(Date, nullable=True)
    meet_url = Column(String(500), nullable=True)
    vig_desde = Column(Date, nullable=False)
    vig_hasta = Column(Date, nullable=True)

    __table_args__ = (
        Index("ix_slot_encuentro_tenant_dictado", "tenant_id", "dictado_id"),
        Index("ix_slot_encuentro_tenant_asignacion", "tenant_id", "asignacion_id"),
    )
