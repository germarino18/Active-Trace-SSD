from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        extra="forbid",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str = Field(alias="DATABASE_URL")
    secret_key: str = Field(alias="SECRET_KEY", min_length=32)
    encryption_key: str = Field(alias="ENCRYPTION_KEY", min_length=64, max_length=64)
    database_url_test: str | None = Field(alias="DATABASE_URL_TEST", default=None)
    access_token_expire_minutes: int = Field(
        alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30, ge=1
    )
    otel_enabled: bool = Field(alias="OTEL_ENABLED", default=True)

    @field_validator("encryption_key")
    @classmethod
    def encryption_key_must_be_64_hex(cls, v: str) -> str:
        if len(v) != 64:
            raise ValueError("ENCRYPTION_KEY must be exactly 64 hex characters (32 bytes)")
        try:
            bytes.fromhex(v)
        except ValueError as exc:
            raise ValueError("ENCRYPTION_KEY must be a valid 64-character hex string") from exc
        return v
