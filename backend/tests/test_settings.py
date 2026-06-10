import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_settings_valid_env():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="b" * 32,
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost:5432/db"
    assert settings.secret_key == "a" * 32
    assert settings.encryption_key == "b" * 32
    assert settings.access_token_expire_minutes == 15


def test_settings_default_expire_minutes():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="b" * 32,
    )
    assert settings.access_token_expire_minutes == 15


def test_settings_missing_database_url():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="b" * 32,
        )


def test_settings_missing_secret_key():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            ENCRYPTION_KEY="b" * 32,
        )


def test_settings_short_secret_key():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="short",
            ENCRYPTION_KEY="b" * 32,
        )


def test_settings_wrong_length_encryption_key():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="wrong-length-key",
        )


def test_settings_invalid_expire_type():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="b" * 32,
            ACCESS_TOKEN_EXPIRE_MINUTES="not-an-int",
        )
