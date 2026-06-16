"""Repository for Aviso and AcknowledgmentAviso entities."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso, AcknowledgmentAviso
from app.repositories.base import BaseRepository


class AvisoRepository(BaseRepository[Aviso]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Aviso, session=session, tenant_id=tenant_id)

    async def find_visible(
        self,
        usuario_id: uuid.UUID,
        roles: list[str],
        materia_ids: list[uuid.UUID],
        cohorte_ids: list[uuid.UUID],
    ) -> list[Aviso]:
        now = datetime.now(timezone.utc)
        query = select(self.model).where(
            self.model.deleted_at.is_(None),
            self.model.activo.is_(True),
            self.model.inicio_en <= now,
            self.model.fin_en >= now,
        )
        query = self._apply_tenant_scope(query)

        alcance_filter = (self.model.alcance == "GLOBAL")
        if roles:
            alcance_filter = alcance_filter | (
                (self.model.alcance == "POR_ROL") & self.model.rol_destino.in_(roles)
            )
        if materia_ids:
            alcance_filter = alcance_filter | (
                (self.model.alcance == "POR_MATERIA") & self.model.materia_id.in_(materia_ids)
            )
        if cohorte_ids:
            alcance_filter = alcance_filter | (
                (self.model.alcance == "POR_COHORTE") & self.model.cohorte_id.in_(cohorte_ids)
            )

        query = query.where(alcance_filter)
        query = query.order_by(self.model.orden.asc(), self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_pending_ack(
        self,
        usuario_id: uuid.UUID,
        roles: list[str],
        materia_ids: list[uuid.UUID],
        cohorte_ids: list[uuid.UUID],
    ) -> list[Aviso]:
        now = datetime.now(timezone.utc)
        tenant_id = self._get_effective_tenant_id()
        subq_where = [
            AcknowledgmentAviso.usuario_id == usuario_id,
            AcknowledgmentAviso.deleted_at.is_(None),
        ]
        if tenant_id is not None:
            subq_where.append(AcknowledgmentAviso.tenant_id == tenant_id)
        subq = (
            select(AcknowledgmentAviso.aviso_id)
            .where(*subq_where)
            .subquery()
        )
        query = select(self.model).where(
            self.model.deleted_at.is_(None),
            self.model.activo.is_(True),
            self.model.requiere_ack.is_(True),
            self.model.inicio_en <= now,
            self.model.fin_en >= now,
            self.model.id.notin_(select(subq.c.aviso_id)),
        )
        query = self._apply_tenant_scope(query)

        alcance_filter = (self.model.alcance == "GLOBAL")
        if roles:
            alcance_filter = alcance_filter | (
                (self.model.alcance == "POR_ROL") & self.model.rol_destino.in_(roles)
            )
        if materia_ids:
            alcance_filter = alcance_filter | (
                (self.model.alcance == "POR_MATERIA") & self.model.materia_id.in_(materia_ids)
            )
        if cohorte_ids:
            alcance_filter = alcance_filter | (
                (self.model.alcance == "POR_COHORTE") & self.model.cohorte_id.in_(cohorte_ids)
            )

        query = query.where(alcance_filter)
        query = query.order_by(self.model.orden.asc(), self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_all_managed(self, skip: int = 0, limit: int = 100) -> list[Aviso]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = query.order_by(self.model.orden.asc(), self.model.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def count_acknowledgments(self, aviso_id: uuid.UUID) -> dict[str, int]:
        tenant_id = self._get_effective_tenant_id()
        total_q = select(func.count(AcknowledgmentAviso.id)).where(
            AcknowledgmentAviso.aviso_id == aviso_id,
            AcknowledgmentAviso.deleted_at.is_(None),
        )
        if tenant_id is not None:
            total_q = total_q.where(AcknowledgmentAviso.tenant_id == tenant_id)
        total_result = await self.session.execute(total_q)
        total = total_result.scalar_one()

        return {
            "total": total,
            "confirmados": total,
            "pendientes": 0,
        }
