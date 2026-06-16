import uuid
from datetime import date

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro
from app.repositories.base import BaseRepository


class SlotEncuentroRepository(BaseRepository[SlotEncuentro]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=SlotEncuentro, session=session, tenant_id=tenant_id)

    async def list_by_dictado(self, dictado_id: uuid.UUID) -> list[SlotEncuentro]:
        return await self.find_by(dictado_id=dictado_id)


class InstanciaEncuentroRepository(BaseRepository[InstanciaEncuentro]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(
            model=InstanciaEncuentro, session=session, tenant_id=tenant_id
        )

    async def list_by_dictado(self, dictado_id: uuid.UUID) -> list[InstanciaEncuentro]:
        return await self.find_by(dictado_id=dictado_id)

    async def list_by_slot(self, slot_id: uuid.UUID) -> list[InstanciaEncuentro]:
        return await self.find_by(slot_id=slot_id)

    async def list_by_tenant(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        estado: str | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InstanciaEncuentro]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)

        filters = []
        if dictado_id is not None:
            filters.append(self.model.dictado_id == dictado_id)
        if estado is not None:
            filters.append(self.model.estado == estado)
        if fecha_desde is not None:
            filters.append(self.model.fecha >= fecha_desde)
        if fecha_hasta is not None:
            filters.append(self.model.fecha <= fecha_hasta)

        if filters:
            query = query.where(or_(*filters) if len(filters) == 1 else filters[0])
            for f in filters[1:]:
                query = query.where(f)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def update_estado(
        self, id: uuid.UUID, estado: str, extra: dict | None = None
    ) -> InstanciaEncuentro:
        update_data: dict = {"estado": estado}
        if extra:
            update_data.update(extra)
        return await self.update(id, update_data)

    async def bulk_create(
        self, instances_data: list[dict]
    ) -> list[InstanciaEncuentro]:
        created: list[InstanciaEncuentro] = []
        for data in instances_data:
            instance = self.model(**data)
            self.session.add(instance)
            created.append(instance)
        await self.session.flush()
        for instance in created:
            await self.session.refresh(instance)
        return created
