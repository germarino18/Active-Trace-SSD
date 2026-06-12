import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select

from app.models.recovery_token import RecoveryToken
from app.models.user import User
from app.repositories.recovery_token_repository import RecoveryTokenRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.auth.password_service import PasswordService


class PasswordRecoveryService:
    def __init__(
        self,
        recovery_token_repo: RecoveryTokenRepository,
        refresh_token_repo: RefreshTokenRepository,
    ):
        self._recovery_token_repo = recovery_token_repo
        self._refresh_token_repo = refresh_token_repo
        self._token_ttl = timedelta(minutes=15)

    async def generate_recovery_token(self, user: User) -> str:
        raw = secrets.token_urlsafe(32)
        token_hash = sha256(raw.encode()).hexdigest()
        await self._recovery_token_repo.create({
            "user_id": user.id,
            "token_hash": token_hash,
            "expires_at": datetime.now(UTC) + self._token_ttl,
        })
        return raw

    async def validate_recovery_token(self, raw_token: str) -> tuple[User, RecoveryToken] | None:
        token_hash = sha256(raw_token.encode()).hexdigest()
        token = await self._recovery_token_repo.find_by_hash(token_hash)
        if token is None:
            return None
        if token.used_at is not None:
            return None
        if token.expires_at < datetime.now(UTC):
            return None
        query = select(User).where(User.id == token.user_id)
        result = await self._recovery_token_repo.session.execute(query)
        user = result.unique().scalar_one_or_none()
        if user is None or not user.is_active:
            return None
        return user, token

    async def complete_reset(self, user: User, new_password: str, token: RecoveryToken) -> None:
        password_service = PasswordService()
        user.password_hash = password_service.hash_password(new_password)
        await self._recovery_token_repo.mark_used(token.id)
        await self._refresh_token_repo.revoke_all_for_user(user.id)
