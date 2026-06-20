from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hilo_conversacion import HiloConversacion
from app.models.hilo_participante import HiloParticipante
from app.repositories.base import BaseRepository


class HiloRepository(BaseRepository[HiloConversacion]):
    """Repositorio para operaciones sobre hilos de conversación."""

    def __init__(self, session: AsyncSession, tenant_id: UUID | None = None):
        super().__init__(model=HiloConversacion, session=session, tenant_id=tenant_id)
        self._participante_repo = BaseRepository(
            model=HiloParticipante,
            session=session,
            tenant_id=tenant_id,
        )

    async def list_by_participante(self, usuario_id: UUID) -> list[HiloConversacion]:
        """Retorna todos los hilos donde el usuario es participante."""
        # Subquery: IDs de hilos donde el usuario participa
        subq = (
            select(HiloParticipante.hilo_id)
            .where(HiloParticipante.usuario_id == usuario_id)
        ).subquery()

        query = (
            select(self.model)
            .where(self.model.id.in_(select(subq)))
            .order_by(self.model.created_at.desc())
        )
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_id(self, hilo_id: UUID) -> HiloConversacion | None:
        """Retorna un hilo por ID (con scope de tenant)."""
        return await self.find_by_id(hilo_id)

    async def es_participante(self, hilo_id: UUID, usuario_id: UUID) -> bool:
        """Verifica si un usuario es participante de un hilo."""
        query = select(HiloParticipante).where(
            HiloParticipante.hilo_id == hilo_id,
            HiloParticipante.usuario_id == usuario_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def add_participante(self, hilo_id: UUID, usuario_id: UUID) -> HiloParticipante:
        """Agrega un participante a un hilo."""
        return await self._participante_repo.create({
            "hilo_id": hilo_id,
            "usuario_id": usuario_id,
        })

    async def actualizar_visto(self, hilo_id: UUID, usuario_id: UUID) -> None:
        """Actualiza el timestamp de última vista del participante."""
        from datetime import datetime, timezone

        query = select(HiloParticipante).where(
            HiloParticipante.hilo_id == hilo_id,
            HiloParticipante.usuario_id == usuario_id,
        )
        result = await self.session.execute(query)
        participante = result.scalar_one_or_none()
        if participante:
            participante.ultima_visto = datetime.now(timezone.utc)
            await self.session.flush()

    async def obtener_otro_participante(self, hilo_id: UUID, usuario_id: UUID) -> UUID | None:
        """Retorna el ID del otro participante del hilo (para hilos de 2 personas).

        Para hilos con 3+ participantes retorna None, ya que no existe
        un único "otro". El caller debe usar ultimo.remitente_id como fallback.
        """
        query = select(HiloParticipante.usuario_id).where(
            HiloParticipante.hilo_id == hilo_id,
            HiloParticipante.usuario_id != usuario_id,
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        if len(rows) == 1:
            return rows[0]
        return None
