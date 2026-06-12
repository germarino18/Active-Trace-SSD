import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update

from app.api.dependencies.auth import get_current_user, get_rate_limiter
from app.core.dependencies import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.recovery_token_repository import RecoveryTokenRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
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
from app.services.auth.password_recovery_service import PasswordRecoveryService
from app.services.auth.password_service import PasswordService
from app.services.auth.rate_limiter import RateLimiter
from app.services.auth.token_service import TokenService
from app.services.auth.two_factor_service import TwoFactorService

router = APIRouter(tags=["auth"])
_password_service = PasswordService()
_two_factor_service = TwoFactorService()
ACCESS_TOKEN_EXPIRES_SECONDS = 1800


def _token_service():
    return TokenService()


async def _find_user_by_email_any_tenant(db, email: str) -> User | None:
    query = select(User).where(User.email == email, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()


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
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "X-Tenant-ID header is required",
        })
    try:
        tenant_id = uuid.UUID(tenant_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail={
            "code": "validation_error",
            "message": "Invalid X-Tenant-ID format",
        })
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
    ts = _token_service()
    if user.totp_enabled_at is not None:
        challenge_token = ts.create_challenge_token(user)
        return AuthenticateResponse(
            challenge_token=challenge_token,
            requires_2fa=True,
        )
    refresh_token_raw, refresh_token_hash = ts.generate_refresh_token()
    refresh_repo = RefreshTokenRepository(session=db)
    await refresh_repo.create({
        "user_id": user.id,
        "token_hash": refresh_token_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    access_token = ts.create_access_token(user)
    return AuthenticateResponse(
        access_token=access_token,
        refresh_token=refresh_token_raw,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
    )


@router.post(
    "/api/auth/login",
    response_model=TokenResponse,
    summary="Phase 2: complete login with TOTP code",
)
async def login(
    body: LoginRequest,
    db=Depends(get_db),
):
    ts = _token_service()
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
    refresh_token_raw, refresh_token_hash = ts.generate_refresh_token()
    refresh_repo = RefreshTokenRepository(session=db)
    await refresh_repo.create({
        "user_id": user.id,
        "token_hash": refresh_token_hash,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
    })
    access_token = ts.create_access_token(user)
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
    ts = _token_service()
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
    access_token = ts.create_access_token(user)
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
