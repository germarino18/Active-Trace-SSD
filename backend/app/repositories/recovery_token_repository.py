import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update

from app.models.recovery_token import RecoveryToken
from app.repositories.base import BaseRepository


class RecoveryTokenRepository(BaseRepository[RecoveryToken]):
    def __init__(self, session):
        super().__init__(model=RecoveryToken, session=session, tenant_id=None)

    async def create(self, data: dict) -> RecoveryToken:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def find_by_hash(self, token_hash: str) -> RecoveryToken | None:
        query = select(self.model).where(self.model.token_hash == token_hash)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def mark_used(self, token_id: uuid.UUID) -> None:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == token_id)
            .values(used_at=datetime.now(UTC))
        )
        await self.session.flush()
