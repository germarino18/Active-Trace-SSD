import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.routers.admin import router as admin_router
from app.api.v1.routers.asignaciones import router as asignaciones_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.equipos import router as equipos_router
from app.api.v1.routers.estructura import router as estructura_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.calificaciones import router as calificaciones_router
from app.api.v1.routers.padron import router as padron_router
from app.api.v1.routers.usuarios import router as usuarios_router
from app.core.config import Settings
from app.core.database import init_engine
from app.core.exceptions import (
    AppException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    TenantMismatchException,
    UnauthorizedException,
    ValidationException,
)
from app.integrations.moodle_ws import MoodleException
from app.core.logging import setup_logging
from app.core.observability import setup_observability
from app.core.tenancy import TenantMiddleware

logger = logging.getLogger(__name__)

STATUS_CODE_MAP: dict[str, int] = {
    NotFoundException.__name__: 404,
    ForbiddenException.__name__: 403,
    TenantMismatchException.__name__: 403,
    UnauthorizedException.__name__: 401,
    ValidationException.__name__: 422,
    RateLimitException.__name__: 429,
}


def _get_status_code(exc: AppException) -> int:
    return STATUS_CODE_MAP.get(type(exc).__name__, 500)


async def _app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=_get_status_code(exc),
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def _moodle_exception_handler(request: Request, exc: MoodleException) -> JSONResponse:
    logger.warning("Moodle WS error: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "moodle_error",
                "message": exc.message,
                "details": {"retry_after": exc.retry_after},
            }
        },
    )


async def _unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
                "details": None,
            }
        },
    )


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
    app.state.settings = settings
    app.add_exception_handler(AppException, _app_exception_handler)
    app.add_exception_handler(MoodleException, _moodle_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
    app.add_middleware(TenantMiddleware)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(estructura_router)
    app.include_router(usuarios_router)
    app.include_router(asignaciones_router)
    app.include_router(equipos_router)
    app.include_router(calificaciones_router)
    app.include_router(padron_router)
    return app
