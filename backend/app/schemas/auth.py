from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuthenticateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    challenge_token: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthenticateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str | None = None
    refresh_token: str | None = None
    challenge_token: str | None = None
    requires_2fa: bool = False
    token_type: str | None = "bearer"
    expires_in: int | None = None


class CurrentUser(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    tenant_id: UUID
    roles: list[str]


class EnrollResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    secret: str
    qr_uri: str


class Verify2FARequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    totp_code: str = Field(..., min_length=6, max_length=6)


class Disable2FARequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class ForgotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(..., max_length=255)


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)
