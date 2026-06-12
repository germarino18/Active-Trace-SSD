import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session):
        super().__init__(model=RefreshToken, session=session, tenant_id=None)

    async def create(self, data: dict) -> RefreshToken:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def find_by_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(self.model).where(self.model.token_hash == token_hash)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def revoke(self, token_id: uuid.UUID) -> None:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == token_id)
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.flush()
