from typing import Any

from starlette.requests import Request

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.auth import CurrentUser


class AuditLogger:
    """Reusable audit-logging helper with real-actor attribution (D4).

    Attribution rule, derived from `CurrentUser`:
    - Impersonation session (`current_user.actor_id` set):
      `actor_id` = real actor, `impersonado_id` = `current_user.user_id` (sub).
    - Normal session (`current_user.actor_id` is None):
      `actor_id` = `current_user.user_id`, `impersonado_id` = None.

    An explicit `impersonado_id` override takes precedence over the
    derived value. This covers actions such as `IMPERSONACION_INICIAR`,
    where the acting session is the real actor's NORMAL session but the
    audit record must reference the user about to be impersonated.
    """

    def __init__(self, repository: AuditLogRepository):
        self._repository = repository

    async def log(
        self,
        *,
        current_user: CurrentUser,
        accion: str,
        detalle: dict[str, Any] | None,
        filas_afectadas: int | None,
        request: Request,
        materia_id=None,
        impersonado_id=None,
    ) -> AuditLog:
        if current_user.actor_id is not None:
            actor_id = current_user.actor_id
            derived_impersonado_id = current_user.user_id
        else:
            actor_id = current_user.user_id
            derived_impersonado_id = None

        if impersonado_id is None:
            impersonado_id = derived_impersonado_id

        ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        return await self._repository.create({
            "tenant_id": current_user.tenant_id,
            "actor_id": actor_id,
            "impersonado_id": impersonado_id,
            "materia_id": materia_id,
            "accion": accion,
            "detalle": detalle,
            "filas_afectadas": filas_afectadas,
            "ip": ip,
            "user_agent": user_agent,
        })
