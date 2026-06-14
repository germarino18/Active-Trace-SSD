import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.user import User
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.usuario_repository import UsuarioRepository


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

    async def create_access_token(
        self, user: User, db: AsyncSession, actor_id: uuid.UUID | None = None
    ) -> str:
        """Issue an access token whose `roles` claim is derived from the
        user's alive, Vigente `Asignacion` rows (D3) — the source of truth
        for effective roles, replacing the deprecated `users.roles`.

        If the user has no `Usuario` profile (e.g. never onboarded), the
        effective roles are an empty set: fail-closed (regla dura #10), not
        a fallback to `users.roles`.
        """
        now = datetime.now(UTC)
        roles: list[str] = []
        usuario_repo = UsuarioRepository(session=db, tenant_id=user.tenant_id)
        usuario = await usuario_repo.find_by_user_id(user.tenant_id, user.id)
        if usuario is not None:
            asignacion_repo = AsignacionRepository(session=db, tenant_id=user.tenant_id)
            roles = sorted(await asignacion_repo.find_roles_vigentes(user.tenant_id, usuario.id))
        payload = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": roles,
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
