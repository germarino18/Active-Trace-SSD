from datetime import date
import uuid

from sqlalchemy import and_, or_, select

from app.models.dictado import Dictado
from app.repositories.base import BaseRepository


class DictadoRepository(BaseRepository[Dictado]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Dictado, session=session, tenant_id=tenant_id)

    async def find_by_materia(self, materia_id: uuid.UUID) -> list[Dictado]:
        query = select(self.model).where(
            self.model.materia_id == materia_id,
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_terna(
        self,
        tenant_id: uuid.UUID,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> Dictado | None:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.materia_id == materia_id,
            self.model.carrera_id == carrera_id,
            self.model.cohorte_id == cohorte_id,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_all_filtered(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activa: bool | None = None,
        q: str | None = None,
        vigente: bool | None = None,
    ) -> list[Dictado]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)

        if activa is not None:
            query = query.where(self.model.estado == ("Activo" if activa else "Inactivo"))

        if q:
            query = query.where(self.model.estado.ilike(f"%{q}%"))

        if vigente:
            today = date.today()
            query = query.where(
                or_(
                    self.model.vig_desde.is_(None),
                    and_(
                        self.model.vig_desde <= today,
                        self.model.vig_hasta >= today,
                    ),
                )
            )

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
