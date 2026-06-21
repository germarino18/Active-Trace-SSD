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

    async def upsert_for_actividad(
        self,
        entrada_padron_id: uuid.UUID,
        dictado_id: uuid.UUID,
        actividad_id: uuid.UUID,
        actividad_nombre: str,
        nota_numerica: float | None,
        nota_textual: str | None,
        aprobado: bool,
        origen: str = "Importado",
    ) -> Calificacion:
        """Upsert a Calificacion for a specific (entrada_padron_id, actividad_id).

        If a row already exists for this (tenant, entrada, actividad_id), update it.
        Otherwise create a new row. Tenant is injected from self.
        """
        tenant_id = self._get_effective_tenant_id()
        # Find existing row by (tenant, entrada_padron_id, actividad_id)
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.entrada_padron_id == entrada_padron_id,
            self.model.actividad_id == actividad_id,
        )
        result = await self.session.execute(query)
        existing = result.unique().scalar_one_or_none()

        if existing is not None:
            existing.nota_numerica = nota_numerica
            existing.nota_textual = nota_textual
            existing.aprobado = aprobado
            existing.actividad = actividad_nombre
            existing.origen = origen
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        data = {
            "entrada_padron_id": entrada_padron_id,
            "dictado_id": dictado_id,
            "actividad_id": actividad_id,
            "actividad": actividad_nombre,
            "nota_numerica": nota_numerica,
            "nota_textual": nota_textual,
            "aprobado": aprobado,
            "origen": origen,
        }
        if tenant_id is not None:
            data.setdefault("tenant_id", tenant_id)
        instance = Calificacion(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

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
