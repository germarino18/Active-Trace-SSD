import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.audit.audit_logger import AuditLogger


class UsuarioService:
    """Reglas de negocio del ABM de `Usuario` (E4, D1/D5).

    Flujo Routers -> Services -> Repositories -> Models (regla dura #11).
    Identidad y tenant siempre desde `CurrentUser` (JWT verificado, reglas
    duras #8/#9). Mutaciones se auditan vía `AuditLogger`.
    """

    def __init__(self, usuario_repo: UsuarioRepository, audit_repo: AuditLogRepository):
        self._repo = usuario_repo
        self._audit = AuditLogger(repository=audit_repo)

    async def create(
        self,
        data: UsuarioCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Usuario:
        create_data = data.model_dump()

        usuario = await self._repo.create(create_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.USUARIO_CREAR,
            detalle={"id": str(usuario.id), "user_id": str(usuario.user_id)},
            filas_afectadas=1,
            request=request,
        )
        return usuario

    async def update(
        self,
        usuario_id: uuid.UUID,
        data: UsuarioUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Usuario:
        update_data = data.model_dump(exclude_unset=True)
        if "estado" in update_data and update_data["estado"] is not None:
            update_data["estado"] = update_data["estado"].value

        usuario = await self._repo.update(usuario_id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.USUARIO_ACTUALIZAR,
            detalle={"id": str(usuario.id), "cambios": list(update_data.keys())},
            filas_afectadas=1,
            request=request,
        )
        return usuario

    async def soft_delete(
        self,
        usuario_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Usuario:
        usuario = await self._repo.soft_delete(usuario_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.USUARIO_ELIMINAR,
            detalle={"id": str(usuario.id)},
            filas_afectadas=1,
            request=request,
        )
        return usuario
