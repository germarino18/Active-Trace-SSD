import uuid

from sqlalchemy import select

from app.models.umbral_materia import UmbralMateria
from app.repositories.base import BaseRepository


class UmbralMateriaRepository(BaseRepository[UmbralMateria]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=UmbralMateria, session=session, tenant_id=tenant_id)

    async def find_by_dictado(self, dictado_id: uuid.UUID) -> list[UmbralMateria]:
        query = select(self.model).where(
            self.model.dictado_id == dictado_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_asignacion_dictado(
        self, asignacion_id: uuid.UUID, dictado_id: uuid.UUID
    ) -> UmbralMateria | None:
        query = select(self.model).where(
            self.model.asignacion_id == asignacion_id,
            self.model.dictado_id == dictado_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def upsert(
        self,
        asignacion_id: uuid.UUID,
        dictado_id: uuid.UUID,
        umbral_pct: int,
        valores_aprobatorios: list[str] | None = None,
    ) -> UmbralMateria:
        existing = await self.find_by_asignacion_dictado(asignacion_id, dictado_id)
        if existing is not None:
            existing.umbral_pct = umbral_pct
            existing.valores_aprobatorios = valores_aprobatorios
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        return await self.create({
            "asignacion_id": asignacion_id,
            "dictado_id": dictado_id,
            "umbral_pct": umbral_pct,
            "valores_aprobatorios": valores_aprobatorios,
        })

    async def delete(self, asignacion_id: uuid.UUID, dictado_id: uuid.UUID) -> bool:
        existing = await self.find_by_asignacion_dictado(asignacion_id, dictado_id)
        if existing is None:
            return False
        await self.session.delete(existing)
        await self.session.flush()
        return True
