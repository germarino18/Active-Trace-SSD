import uuid

from sqlalchemy import select, update

from app.models.calificacion import Calificacion
from app.repositories.base import BaseRepository


class CalificacionRepository(BaseRepository[Calificacion]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Calificacion, session=session, tenant_id=tenant_id)

    async def bulk_create(self, entries: list[dict]) -> list[Calificacion]:
        tenant_id = self._get_effective_tenant_id()
        instances = []
        for data in entries:
            row_data = dict(data)
            if tenant_id is not None:
                row_data.setdefault("tenant_id", tenant_id)
            instance = Calificacion(**row_data)
            self.session.add(instance)
            instances.append(instance)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def find_by_dictado(self, dictado_id: uuid.UUID) -> list[Calificacion]:
        query = select(self.model).where(
            self.model.dictado_id == dictado_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def recalcular_aprobado_por_dictado(
        self,
        dictado_id: uuid.UUID,
        umbral_pct: int,
        valores_aprobatorios: list[str] | None = None,
    ) -> int:
        """Recalculate `aprobado` for all calificaciones in a dictado.

        - If nota_numerica exists: aprobado = nota_numerica >= umbral_pct
        - If only nota_textual: aprobado = nota_textual in valores_aprobatorios
        - If both exist: either condition can make it aprobado=True
        """
        califs = await self.find_by_dictado(dictado_id)
        if not califs:
            return 0

        updated = 0
        for c in califs:
            numerica_ok = False
            textual_ok = False

            if c.nota_numerica is not None:
                numerica_ok = float(c.nota_numerica) >= umbral_pct

            if c.nota_textual is not None and valores_aprobatorios:
                textual_ok = c.nota_textual in valores_aprobatorios

            if c.nota_numerica is not None and c.nota_textual is None:
                new_aprobado = numerica_ok
            elif c.nota_numerica is None and c.nota_textual is not None:
                new_aprobado = textual_ok
            else:
                new_aprobado = numerica_ok or textual_ok

            if c.aprobado != new_aprobado:
                c.aprobado = new_aprobado
                updated += 1

        if updated > 0:
            await self.session.flush()

        return updated

    async def find_by_dictado_and_entrada(
        self, dictado_id: uuid.UUID, entrada_padron_id: uuid.UUID
    ) -> list[Calificacion]:
        query = select(self.model).where(
            self.model.dictado_id == dictado_id,
            self.model.entrada_padron_id == entrada_padron_id,
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
