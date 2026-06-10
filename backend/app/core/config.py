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
    encryption_key: str = Field(alias="ENCRYPTION_KEY", min_length=32, max_length=32)
    database_url_test: str | None = Field(alias="DATABASE_URL_TEST", default=None)
    access_token_expire_minutes: int = Field(
        alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=15, ge=1
    )
    otel_enabled: bool = Field(alias="OTEL_ENABLED", default=True)

    @field_validator("encryption_key")
    @classmethod
    def encryption_key_must_be_exactly_32(cls, v: str) -> str:
        if len(v) != 32:
            raise ValueError("ENCRYPTION_KEY must be exactly 32 characters")
        return v
