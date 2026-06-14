import uuid

from sqlalchemy import select

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Usuario, session=session, tenant_id=tenant_id)

    async def find_by_user_id(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Usuario | None:
        """Find the `usuario` profile (E4) linked 1:1 to a `users.id` (D1).

        Returns `None` if the auth identity has no `usuario` profile yet
        (e.g. a user created before migration 007's backfill ran, or a
        brand-new user that has not been onboarded). Callers (e.g.
        `TokenService.create_access_token`) treat this as "zero effective
        roles" — fail-closed (regla dura #10), not an error.
        """
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.user_id == user_id,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
