import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import get_db
from app.core.tenancy import TenantContext
from app.repositories.user_repository import UserRepository
from app.schemas.auth import CurrentUser
from app.services.auth.rate_limiter import RateLimiter
from app.services.auth.token_service import TokenService

_bearer = HTTPBearer(auto_error=False)
_rate_limiter = RateLimiter()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db=Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Missing Authorization header",
        })
    token = credentials.credentials
    token_service = TokenService(request.app.state.settings)
    try:
        payload = token_service.verify_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid token",
        })
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    roles = payload.get("roles", [])
    actor_id = payload.get("actor_id")
    if not user_id or not tenant_id:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid token claims",
        })
    TenantContext.set(uuid.UUID(tenant_id))
    return CurrentUser(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id),
        roles=roles,
        actor_id=uuid.UUID(actor_id) if actor_id else None,
    )


async def get_rate_limiter() -> RateLimiter:
    return _rate_limiter
