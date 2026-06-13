import uuid

from sqlalchemy import select

from app.models.consumed_challenge_token import ConsumedChallengeToken
from app.repositories.base import BaseRepository


class ConsumedChallengeTokenRepository(BaseRepository[ConsumedChallengeToken]):
    def __init__(self, session):
        super().__init__(model=ConsumedChallengeToken, session=session, tenant_id=None)

    async def create(self, data: dict) -> ConsumedChallengeToken:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def find_by_jti(self, jti: uuid.UUID) -> ConsumedChallengeToken | None:
        query = select(self.model).where(self.model.jti == jti)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
