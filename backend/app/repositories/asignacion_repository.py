import datetime
import uuid

from sqlalchemy import or_, select

from app.models.asignacion import Asignacion
from app.repositories.base import BaseRepository


class AsignacionRepository(BaseRepository[Asignacion]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Asignacion, session=session, tenant_id=tenant_id)

    async def find_roles_vigentes(
        self, tenant_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> set[str]:
        """DISTINCT `rol` of alive, Vigente asignaciones (D3).

        Vigente <=> `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`.
        `estado_vigencia` is never stored; it is computed here from dates.
        """
        hoy = datetime.date.today()
        query = select(Asignacion.rol).where(
            Asignacion.tenant_id == tenant_id,
            Asignacion.usuario_id == usuario_id,
            Asignacion.deleted_at.is_(None),
            Asignacion.desde <= hoy,
            or_(Asignacion.hasta.is_(None), Asignacion.hasta >= hoy),
        )
        result = await self.session.execute(query)
        return {row[0] for row in result}
