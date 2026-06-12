import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.exceptions import TenantMismatchException

_tenant_ctx: ContextVar[uuid.UUID | None] = ContextVar("tenant_id", default=None)


class TenantContext:
    @staticmethod
    def get() -> uuid.UUID | None:
        return _tenant_ctx.get()

    @staticmethod
    def set(tenant_id: uuid.UUID) -> None:
        _tenant_ctx.set(tenant_id)

    @staticmethod
    def reset() -> None:
        _tenant_ctx.set(None)


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        tenant_id_str = request.headers.get("X-Tenant-ID")
        if tenant_id_str:
            try:
                tenant_id = uuid.UUID(tenant_id_str)
                TenantContext.set(tenant_id)
            except ValueError:
                pass
        try:
            response = await call_next(request)
        finally:
            TenantContext.reset()
        return response


async def get_tenant_id(request: Request | None = None) -> uuid.UUID:
    tenant_id = TenantContext.get()
    if tenant_id is not None:
        return tenant_id
    if request is not None:
        tenant_id_str = request.headers.get("X-Tenant-ID")
        if tenant_id_str:
            try:
                return uuid.UUID(tenant_id_str)
            except ValueError:
                pass
    raise TenantMismatchException(
        details={"reason": "No tenant context found in request"}
    )


async def set_tenant_context(tenant_id: uuid.UUID) -> None:
    TenantContext.set(tenant_id)
