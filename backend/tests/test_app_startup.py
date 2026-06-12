from app.core.config import Settings
from app.main import create_app


async def test_app_creates_without_error():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/activia_trace",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="a" * 64,
        OTEL_ENABLED=False,
    )
    app = create_app(settings)
    assert app.title == "activia-trace"
    assert app.version == "0.1.0"


async def test_app_has_health_route():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/activia_trace",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="a" * 64,
        OTEL_ENABLED=False,
    )
    app = create_app(settings)
    routes = [r.path for r in app.routes]
    assert "/health" in routes
