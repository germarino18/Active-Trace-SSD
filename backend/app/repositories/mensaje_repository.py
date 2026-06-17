from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mensaje import Mensaje
from app.repositories.base import BaseRepository


class MensajeRepository(BaseRepository[Mensaje]):
    """Repositorio para operaciones sobre mensajes."""

    def __init__(self, session: AsyncSession, tenant_id: UUID | None = None):
        super().__init__(model=Mensaje, session=session, tenant_id=tenant_id)

    async def list_by_hilo(self, hilo_id: UUID) -> list[Mensaje]:
        """Retorna los mensajes de un hilo ordenados cronológicamente."""
        query = (
            select(self.model)
            .where(self.model.hilo_id == hilo_id)
            .order_by(self.model.created_at.asc())
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_ultimo_mensaje(self, hilo_id: UUID) -> Mensaje | None:
        """Retorna el mensaje más reciente de un hilo."""
        query = (
            select(self.model)
            .where(self.model.hilo_id == hilo_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def count_no_leidos(self, hilo_id: UUID, usuario_id: UUID, ultima_visto) -> int:
        """Cuenta mensajes no leídos en un hilo para un usuario."""
        query = select(func.count()).where(
            self.model.hilo_id == hilo_id,
            self.model.remitente_id != usuario_id,
        )
        if ultima_visto is not None:
            query = query.where(self.model.created_at > ultima_visto)
        result = await self.session.execute(query)
        return result.scalar_one()
