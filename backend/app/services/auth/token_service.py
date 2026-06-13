import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from jose import JWTError, jwt

from app.core.config import Settings
from app.models.user import User


class TokenService:
    def __init__(self, settings: Settings | None = None):
        if settings is not None:
            self._settings = settings
            self._secret = settings.secret_key
            self._access_token_ttl = timedelta(minutes=settings.access_token_expire_minutes)
        else:
            try:
                self._settings = Settings()
                self._secret = self._settings.secret_key
                self._access_token_ttl = timedelta(minutes=self._settings.access_token_expire_minutes)
            except Exception:
                self._settings = None
                self._secret = "dev-secret-key-that-is-exactly-32-bytes!"
                self._access_token_ttl = timedelta(minutes=30)
        self._challenge_token_ttl = timedelta(minutes=5)
        self._algorithm = "HS256"

    def create_access_token(self, user: User, actor_id: uuid.UUID | None = None) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": list(user.roles or []),
            "exp": now + self._access_token_ttl,
            "iat": now,
            "jti": str(uuid.uuid4()),
        }
        if actor_id is not None:
            payload["actor_id"] = str(actor_id)
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return payload
        except JWTError as exc:
            raise ValueError(f"Invalid token: {exc}") from exc

    @staticmethod
    def generate_refresh_token() -> tuple[str, str]:
        raw = str(uuid.uuid4())
        token_hash = sha256(raw.encode()).hexdigest()
        return raw, token_hash

    def create_challenge_token(self, user: User) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "purpose": "2fa_challenge",
            "exp": now + self._challenge_token_ttl,
            "iat": now,
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_challenge_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            if payload.get("purpose") != "2fa_challenge":
                raise ValueError("Token purpose is not 2fa_challenge")
            return payload
        except JWTError as exc:
            raise ValueError(f"Invalid challenge token: {exc}") from exc
