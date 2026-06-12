import uuid

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=User, session=session, tenant_id=tenant_id)

    async def find_by_email(self, tenant_id: uuid.UUID, email: str) -> User | None:
        query = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.email == email,
        )
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_by_id(self, id: uuid.UUID) -> User | None:
        query = select(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
