import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.health import router as health_router
from app.core.config import Settings
from app.core.database import init_engine
from app.core.logging import setup_logging
from app.core.observability import setup_observability

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        setup_logging()
        logger.info("Starting activia-trace application")
        init_engine(settings.database_url)
        setup_observability(settings, app)
        yield
        from app.core.database import close_engine
        await close_engine()
        logger.info("activia-trace application stopped")

    app = FastAPI(
        title="activia-trace",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    return app
