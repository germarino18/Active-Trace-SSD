"""Repository for Tarea and ComentarioTarea entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tarea import Tarea
from app.repositories.base import BaseRepository


class TareaRepository(BaseRepository[Tarea]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Tarea, session=session, tenant_id=tenant_id)

    async def find_by_asignado(
        self,
        usuario_id: uuid.UUID,
        estado: str | None = None,
        materia_id: uuid.UUID | None = None,
        texto: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Tarea]:
        query = select(self.model).where(self.model.asignado_a == usuario_id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)

        if estado is not None:
            query = query.where(self.model.estado == estado)
        if materia_id is not None:
            query = query.where(self.model.materia_id == materia_id)
        if texto:
            query = query.where(self.model.descripcion.ilike(f"%{texto}%"))

        query = query.order_by(self.model.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_all_managed(
        self,
        estado: str | None = None,
        materia_id: uuid.UUID | None = None,
        asignado_a_id: uuid.UUID | None = None,
        texto: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Tarea]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)

        if estado is not None:
            query = query.where(self.model.estado == estado)
        if materia_id is not None:
            query = query.where(self.model.materia_id == materia_id)
        if asignado_a_id is not None:
            query = query.where(self.model.asignado_a == asignado_a_id)
        if texto:
            query = query.where(self.model.descripcion.ilike(f"%{texto}%"))

        query = query.order_by(self.model.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_with_comments(self, tarea_id: uuid.UUID) -> Tarea | None:
        query = (
            select(self.model)
            .options(selectinload(self.model.comentarios))
            .where(self.model.id == tarea_id)
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
