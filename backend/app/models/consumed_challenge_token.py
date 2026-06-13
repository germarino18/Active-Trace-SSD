import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, UUID

from app.models.base import Base


class ConsumedChallengeToken(Base):
    __tablename__ = "consumed_challenge_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = Column(UUID(as_uuid=True), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime(timezone=True), nullable=False)
