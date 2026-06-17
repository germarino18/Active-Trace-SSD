import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.perfil import PerfilUpdate


class PerfilService:
    """Servicio para consultar y actualizar el perfil propio del usuario autenticado."""

    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID):
        self._db = db
        self._tenant_id = tenant_id
        self._usuario_repo = BaseRepository(
            model=Usuario,
            session=db,
            tenant_id=tenant_id,
        )

    async def get_perfil(self, user_id: uuid.UUID) -> tuple[Usuario, str]:
        """Retorna (usuario, email) del usuario autenticado.

        Raises NotFoundException si no existe fila en `usuario` para este user_id.
        """
        usuarios = await self._usuario_repo.find_by(user_id=user_id)
        if not usuarios:
            raise NotFoundException(resource="Perfil", id=user_id)
        usuario = usuarios[0]

        # Obtener email desde la tabla `users` (no se duplica en `usuario`)
        user_query = select(User.email).where(User.id == user_id)
        result = await self._db.execute(user_query)
        email_row = result.scalar_one_or_none()
        email = email_row if email_row else ""

        return usuario, email

    async def update_perfil(
        self,
        user_id: uuid.UUID,
        data: PerfilUpdate,
    ) -> tuple[Usuario, str]:
        """Actualiza los campos editables del perfil.

        Raises NotFoundException si no existe fila en `usuario`.
        Retorna (usuario_actualizado, email).
        """
        usuarios = await self._usuario_repo.find_by(user_id=user_id)
        if not usuarios:
            raise NotFoundException(resource="Perfil", id=user_id)
        usuario = usuarios[0]

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No se proporcionaron campos editables")

        for key, value in update_data.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)

        await self._db.flush()
        await self._db.refresh(usuario)

        # Obtener email
        user_query = select(User.email).where(User.id == user_id)
        result = await self._db.execute(user_query)
        email_row = result.scalar_one_or_none()
        email = email_row if email_row else ""

        return usuario, email
