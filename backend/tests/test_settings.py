import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_settings_valid_env():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="a" * 64,
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost:5432/db"
    assert settings.secret_key == "a" * 32
    assert settings.encryption_key == "a" * 64
    assert settings.access_token_expire_minutes == 15


def test_settings_default_expire_minutes():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="a" * 64,
    )
    assert settings.access_token_expire_minutes == 30


def test_settings_missing_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="a" * 64,
        )


def test_settings_missing_secret_key(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            ENCRYPTION_KEY="a" * 64,
        )


def test_settings_short_secret_key(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="short",
            ENCRYPTION_KEY="a" * 64,
        )


def test_settings_wrong_length_encryption_key(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="too-short",
        )


def test_settings_non_hex_encryption_key(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="z" * 64,
        )


def test_settings_invalid_expire_type(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="a" * 32,
            ENCRYPTION_KEY="a" * 64,
            ACCESS_TOKEN_EXPIRE_MINUTES="not-an-int",
        )
