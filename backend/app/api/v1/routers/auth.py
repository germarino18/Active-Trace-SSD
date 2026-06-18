import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.api.dependencies.auth import get_current_user, get_rate_limiter
from app.api.dependencies.permissions import require_permission
from app.core.acciones_auditoria import AccionAuditoria
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.models.consumed_challenge_token import ConsumedChallengeToken
from app.models.refresh_token import RefreshToken
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.consumed_challenge_token_repository import ConsumedChallengeTokenRepository
from app.repositories.recovery_token_repository import RecoveryTokenRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.permission_service import PermissionResolver
from app.schemas.auth import (
    AuthenticateRequest,
    AuthenticateResponse,
    CurrentUser,
    Disable2FARequest,
    EnrollResponse,
    ForgotRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    ResetRequest,
    TokenResponse,
    Verify2FARequest,
)
from app.schemas.impersonation import ImpersonateEndResponse, ImpersonateResponse
from app.services.audit.audit_logger import AuditLogger
from app.services.auth.password_recovery_service import PasswordRecoveryService
from app.services.auth.password_service import PasswordService
from app.services.auth.rate_limiter import RateLimiter
from app.services.auth.token_service import TokenService
from app.services.auth.two_factor_service import TwoFactorService

router = APIRouter(tags=["auth"])
_password_service = PasswordService()
_two_factor_service = TwoFactorService()
ACCESS_TOKEN_EXPIRES_SECONDS = 1800


def _token_service(request: Request) -> TokenService:
    return TokenService(request.app.state.settings)


async def _find_user_by_email_any_tenant(db, email: str) -> User | None:
    query = select(User).where(User.email == email, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()


async def _resolve_tenant(db, tenant_id_or_slug: str) -> uuid.UUID:
    """Resolve X-Tenant-ID header to a tenant UUID.
    Accepts either a UUID or a slug (e.g. 'demo')."""
    # Try parsing as UUID first
    try:
        return uuid.UUID(tenant_id_or_slug)
    except ValueError:
        pass
    # Fallback: look up by slug
    result = await db.execute(
        select(Tenant.id).where(Tenant.slug == tenant_id_or_slug, Tenant.deleted_at.is_(None))
    )
    tenant_id = result.scalar_one_or_none()
    if tenant_id is None:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": f"Tenant not found for slug: {tenant_id_or_slug}",
        })
    return tenant_id


@router.post(
    "/api/auth/authenticate",
    response_model=AuthenticateResponse,
    summary="Phase 1: validate credentials, optionally return challenge token",
)
async def authenticate(
    body: AuthenticateRequest,
    request: Request,
    db=Depends(get_db),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
    x_tenant_id: str | None = Header(
        default=None,
        alias="X-Tenant-ID",
        description="UUID or slug of the tenant to authenticate against (required)",
    ),
):
    ip = request.client.host if request.client else "unknown"
    if not rate_limiter.check(ip, body.email):
        retry_after = rate_limiter.get_retry_after(ip, body.email)
        raise HTTPException(
            status_code=429,
            detail={
                "code": "rate_limit",
                "message": "Too many requests",
                "details": {"retry_after": retry_after},
            },
            headers={"Retry-After": str(retry_after)},
        )
    tenant_id_str = x_tenant_id
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "X-Tenant-ID header is required",
        })
    tenant_id = await _resolve_tenant(db, tenant_id_str)
    user_repo = UserRepository(session=db, tenant_id=tenant_id)
    user = await user_repo.find_by_email(tenant_id, body.email)
    if user is None or not _password_service.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid credentials",
        })
    if not user.is_active:
        raise HTTPException(status_code=403, detail={
            "code": "forbidden",
            "message": "Account is disabled",
        })
    ts = _token_service(request)
    if user.totp_enabled_at is not None:
        challenge_token = ts.create_challenge_token(user)
        return AuthenticateResponse(
            challenge_token=challenge_token,
            requires_2fa=True,
            tenant_id=str(tenant_id),
        )
    refresh_token_raw, refresh_token_hash = ts.generate_refresh_token()
    refresh_repo = RefreshTokenRepository(session=db)
    await refresh_repo.create({
        "user_id": user.id,
        "token_hash": refresh_token_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    access_token = await ts.create_access_token(user, db)
    return AuthenticateResponse(
        access_token=access_token,
        refresh_token=refresh_token_raw,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
        tenant_id=str(tenant_id),
    )


@router.post(
    "/api/auth/login",
    response_model=TokenResponse,
    summary="Phase 2: complete login with TOTP code",
)
async def login(
    body: LoginRequest,
    request: Request,
    db=Depends(get_db),
):
    ts = _token_service(request)
    try:
        payload = ts.verify_challenge_token(body.challenge_token)
    except ValueError:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid or expired challenge token",
        })
    user_id = uuid.UUID(payload["sub"])
    tenant_id = uuid.UUID(payload["tenant_id"])
    user_repo = UserRepository(session=db, tenant_id=tenant_id)
    user = await user_repo.find_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid or expired challenge token",
        })
    if user.totp_secret is None:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "2FA is not configured for this user",
        })
    decrypted_secret = _two_factor_service.decrypt_secret(user.totp_secret)
    if not _two_factor_service.verify_code(decrypted_secret, body.totp_code):
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid TOTP code",
        })
    jti = uuid.UUID(payload["jti"])
    challenge_repo = ConsumedChallengeTokenRepository(session=db)
    if await challenge_repo.find_by_jti(jti) is not None:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Challenge token already used",
        })
    try:
        await challenge_repo.create({
            "jti": jti,
            "user_id": user.id,
            "expires_at": datetime.fromtimestamp(payload["exp"], tz=UTC),
        })
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Challenge token already used",
        })
    refresh_token_raw, refresh_token_hash = ts.generate_refresh_token()
    refresh_repo = RefreshTokenRepository(session=db)
    await refresh_repo.create({
        "user_id": user.id,
        "token_hash": refresh_token_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    access_token = await ts.create_access_token(user, db)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_raw,
        expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
    )


@router.post(
    "/api/auth/refresh",
    response_model=TokenResponse,
    summary="Refresh access token with rotation",
)
async def refresh(
    body: RefreshRequest,
    request: Request,
    db=Depends(get_db),
):
    token_hash = sha256(body.refresh_token.encode()).hexdigest()
    refresh_repo = RefreshTokenRepository(session=db)
    token = await refresh_repo.find_by_hash(token_hash)
    if token is None:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid refresh token",
        })
    if token.revoked_at is not None:
        await refresh_repo.revoke_all_for_user(token.user_id)
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Refresh token has been revoked",
        })
    if token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Refresh token has expired",
        })
    user_repo = UserRepository(session=db, tenant_id=None)
    user = await user_repo.find_by_id(token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "User not found or inactive",
        })
    await refresh_repo.revoke(token.id)
    ts = _token_service(request)
    new_raw, new_hash = ts.generate_refresh_token()
    new_token = await refresh_repo.create({
        "user_id": user.id,
        "token_hash": new_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    await refresh_repo.session.execute(
        update(RefreshToken)
        .where(RefreshToken.id == token.id)
        .values(replaced_by=new_token.id)
    )
    await refresh_repo.session.flush()
    access_token = await ts.create_access_token(user, db)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw,
        expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
    )


@router.post(
    "/api/auth/logout",
    summary="Revoke refresh token",
)
async def logout(
    body: LogoutRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    token_hash = sha256(body.refresh_token.encode()).hexdigest()
    refresh_repo = RefreshTokenRepository(session=db)
    token = await refresh_repo.find_by_hash(token_hash)
    if token is not None:
        await refresh_repo.revoke(token.id)
    return {"message": "Logged out successfully"}


@router.post(
    "/api/auth/2fa/enroll",
    response_model=EnrollResponse,
    summary="Generate TOTP secret for 2FA enrollment",
)
async def enroll_2fa(
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepository(session=db, tenant_id=current_user.tenant_id)
    user = await user_repo.find_by_id(current_user.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail={
            "code": "not_found",
            "message": "User not found",
        })
    if user.totp_enabled_at is not None:
        raise HTTPException(status_code=409, detail={
            "code": "conflict",
            "message": "2FA is already enabled. Disable first to re-enroll.",
        })
    result = _two_factor_service.generate_secret(user.email)
    encrypted = _two_factor_service.encrypt_secret(result["secret"])
    user.totp_secret = encrypted
    await db.flush()
    return EnrollResponse(secret=result["secret"], qr_uri=result["qr_uri"])


@router.post(
    "/api/auth/2fa/verify",
    summary="Verify TOTP code and enable 2FA",
)
async def verify_2fa(
    body: Verify2FARequest,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepository(session=db, tenant_id=current_user.tenant_id)
    user = await user_repo.find_by_id(current_user.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail={
            "code": "not_found",
            "message": "User not found",
        })
    if user.totp_secret is None:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "No pending enrollment. Call /2fa/enroll first.",
        })
    decrypted = _two_factor_service.decrypt_secret(user.totp_secret)
    if not _two_factor_service.verify_code(decrypted, body.totp_code):
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid TOTP code",
        })
    user.totp_enabled_at = datetime.now(UTC)
    await db.flush()
    return {"message": "2FA enabled successfully"}


@router.post(
    "/api/auth/2fa/disable",
    summary="Disable 2FA (requires password + TOTP)",
)
async def disable_2fa(
    body: Disable2FARequest,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepository(session=db, tenant_id=current_user.tenant_id)
    user = await user_repo.find_by_id(current_user.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail={
            "code": "not_found",
            "message": "User not found",
        })
    if not _password_service.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid password",
        })
    if user.totp_secret is None:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "2FA is not configured",
        })
    decrypted = _two_factor_service.decrypt_secret(user.totp_secret)
    if not _two_factor_service.verify_code(decrypted, body.totp_code):
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid TOTP code",
        })
    user.totp_secret = None
    user.totp_enabled_at = None
    await db.flush()
    return {"message": "2FA disabled successfully"}


@router.get(
    "/api/auth/me",
    summary="Get current user profile (identity, roles, permissions)",
)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepository(session=db, tenant_id=current_user.tenant_id)
    user = await user_repo.find_by_id(current_user.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail={
            "code": "not_found",
            "message": "User not found",
        })

    nombre = user.display_name
    apellido = ""
    usuario_repo = UsuarioRepository(session=db, tenant_id=current_user.tenant_id)
    usuario_profile = await usuario_repo.find_by_user_id(current_user.tenant_id, current_user.user_id)
    if usuario_profile is not None:
        nombre = usuario_profile.nombre
        apellido = usuario_profile.apellidos

    resolver = PermissionResolver(db)
    permissions = await resolver.get_effective_permissions(
        current_user.tenant_id, current_user.roles
    )

    return {
        "id": str(current_user.user_id),
        "email": user.email,
        "nombre": nombre,
        "apellido": apellido,
        "roles": current_user.roles,
        "permissions": sorted(permissions),
        "tenant_id": str(current_user.tenant_id),
    }


@router.post(
    "/api/auth/forgot",
    summary="Request password reset token",
)
async def forgot(
    body: ForgotRequest,
    db=Depends(get_db),
):
    user = await _find_user_by_email_any_tenant(db, body.email)
    if user is not None and user.is_active:
        refresh_repo = RefreshTokenRepository(session=db)
        recovery_repo = RecoveryTokenRepository(session=db)
        recovery_service = PasswordRecoveryService(
            recovery_token_repo=recovery_repo,
            refresh_token_repo=refresh_repo,
        )
        await recovery_service.generate_recovery_token(user)
    return {"message": "If the email exists, a recovery link has been sent"}


@router.post(
    "/api/auth/reset",
    summary="Reset password with recovery token",
)
async def reset(
    body: ResetRequest,
    db=Depends(get_db),
):
    if body.new_password != body.new_password_confirm:
        raise HTTPException(status_code=422, detail={
            "code": "validation_error",
            "message": "Passwords do not match",
        })
    refresh_repo = RefreshTokenRepository(session=db)
    recovery_repo = RecoveryTokenRepository(session=db)
    recovery_service = PasswordRecoveryService(
        recovery_token_repo=recovery_repo,
        refresh_token_repo=refresh_repo,
    )
    result = await recovery_service.validate_recovery_token(body.token)
    if result is None:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Invalid or expired recovery token",
        })
    user, token = result
    await recovery_service.complete_reset(user, body.new_password, token)
    return {"message": "Password reset successfully"}


@router.post(
    "/api/v1/auth/impersonate/end",
    response_model=ImpersonateEndResponse,
    summary="End an impersonation session, restoring the real actor",
)
async def impersonate_end(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    if current_user.actor_id is None:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "No active impersonation session",
        })

    real_actor_id = current_user.actor_id
    user_repo = UserRepository(session=db, tenant_id=current_user.tenant_id)
    actor_results = await user_repo.find_by(id=real_actor_id)
    actor = actor_results[0] if actor_results else None
    if actor is None or not actor.is_active:
        raise HTTPException(status_code=401, detail={
            "code": "unauthorized",
            "message": "Real actor not found",
        })

    ts = _token_service(request)
    access_token = await ts.create_access_token(actor, db)

    audit_repo = AuditLogRepository(session=db, tenant_id=current_user.tenant_id)
    audit_logger = AuditLogger(repository=audit_repo)
    await audit_logger.log(
        current_user=current_user,
        accion=AccionAuditoria.IMPERSONACION_FINALIZAR,
        detalle={"impersonado_id": str(current_user.user_id)},
        filas_afectadas=1,
        request=request,
    )
    await db.commit()

    return ImpersonateEndResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
    )


@router.post(
    "/api/v1/auth/impersonate/{user_id}",
    response_model=ImpersonateResponse,
    summary="Start an impersonation session over a same-tenant target user",
    dependencies=[Depends(require_permission(Perm.IMPERSONACION_USAR))],
)
async def impersonate(
    user_id: uuid.UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepository(session=db, tenant_id=current_user.tenant_id)
    target_results = await user_repo.find_by(id=user_id)
    target = target_results[0] if target_results else None
    if target is None or not target.is_active:
        raise HTTPException(status_code=404, detail={
            "code": "not_found",
            "message": "Target user not found",
        })

    ts = _token_service(request)
    access_token = await ts.create_access_token(target, db, actor_id=current_user.user_id)

    audit_repo = AuditLogRepository(session=db, tenant_id=current_user.tenant_id)
    audit_logger = AuditLogger(repository=audit_repo)
    await audit_logger.log(
        current_user=current_user,
        accion=AccionAuditoria.IMPERSONACION_INICIAR,
        detalle={"target_user_id": str(target.id)},
        filas_afectadas=1,
        request=request,
        impersonado_id=target.id,
    )
    await db.commit()

    return ImpersonateResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
    )
