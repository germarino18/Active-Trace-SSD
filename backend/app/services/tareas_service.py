"""Service for tareas (internal task management with state machine)."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.core.state_machine import StateMachine, TransitionError
from app.models.tarea import ComentarioTarea, Tarea, TareaEstado
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.tarea_repository import TareaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.tareas import (
    ComentarioCreate,
    ComentarioRead,
    TareaCreate,
    TareaCreatePropia,
    TareaRead,
    TareaUpdateEstado,
    TareaUpdatePropia,
)
from app.services.audit.audit_logger import AuditLogger


_TAREA_STATE_MACHINE = StateMachine(
    state_enum=TareaEstado,
    initial=TareaEstado.PENDIENTE,
    transitions={
        TareaEstado.PENDIENTE: [TareaEstado.EN_PROGRESO, TareaEstado.CANCELADA],
        TareaEstado.EN_PROGRESO: [TareaEstado.RESUELTA, TareaEstado.CANCELADA],
        TareaEstado.RESUELTA: [TareaEstado.EN_PROGRESO],
        TareaEstado.CANCELADA: [],
    },
)

_REOPEN_ROLES = {"COORDINADOR", "ADMIN"}


class TareasService:
    def __init__(
        self,
        tarea_repo: TareaRepository,
        audit_repo: AuditLogRepository,
        usuario_repo: UsuarioRepository,
        session: AsyncSession,
    ):
        self._repo = tarea_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._usuario_repo = usuario_repo
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "TareasService":
        return cls(
            tarea_repo=TareaRepository(session=session, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            usuario_repo=UsuarioRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def create_tarea(
        self,
        data: TareaCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> TareaRead:
        usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
        if not usuarios:
            raise NotFoundException(resource="Usuario", id=current_user.user_id)
        usuario = usuarios[0]

        tarea = await self._repo.create({
            "asignado_a": data.asignado_a,
            "asignado_por": usuario.id,
            "materia_id": data.materia_id,
            "descripcion": data.descripcion,
            "contexto_id": data.contexto_id,
            "estado": TareaEstado.PENDIENTE.value,
        })
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.TAREA_CREAR,
            detalle={
                "tarea_id": str(tarea.id),
                "asignado_a": str(data.asignado_a),
                "descripcion": data.descripcion,
            },
            filas_afectadas=1,
            request=request,
        )
        return TareaRead.model_validate(tarea)

    async def create_tarea_propia(
        self,
        data: TareaCreatePropia,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> TareaRead:
        """Create a task assigned to and owned by current_user (no delegation)."""
        usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
        if not usuarios:
            raise NotFoundException(resource="Usuario", id=current_user.user_id)
        usuario = usuarios[0]

        tarea = await self._repo.create({
            "asignado_a": usuario.id,
            "asignado_por": usuario.id,
            "materia_id": data.materia_id,
            "descripcion": data.descripcion,
            "estado": TareaEstado.PENDIENTE.value,
        })
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.TAREA_CREAR,
            detalle={
                "tarea_id": str(tarea.id),
                "asignado_a": str(usuario.id),
                "descripcion": data.descripcion,
            },
            filas_afectadas=1,
            request=request,
        )
        return TareaRead.model_validate(tarea)

    async def update_tarea_propia(
        self,
        tarea_id: uuid.UUID,
        data: TareaUpdatePropia,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> TareaRead:
        """Update own tarea (owner-only, 404 if not owned or not found)."""
        usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
        if not usuarios:
            raise NotFoundException(resource="Tarea", id=tarea_id)
        usuario = usuarios[0]

        tarea = await self._repo.find_own_tarea(tarea_id, owner_id=usuario.id)
        if tarea is None:
            raise NotFoundException(resource="Tarea", id=tarea_id)

        if data.estado is not None:
            current_estado = TareaEstado(tarea.estado)
            target_estado = data.estado
            try:
                _TAREA_STATE_MACHINE.validate_transition(current_estado, target_estado)
            except TransitionError as e:
                raise ValidationException(message=str(e)) from e
            tarea.estado = target_estado.value

        if data.descripcion is not None:
            tarea.descripcion = data.descripcion

        if data.materia_id is not None:
            tarea.materia_id = data.materia_id

        await self._session.flush()
        await self._session.refresh(tarea)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.TAREA_ACTUALIZAR,
            detalle={"tarea_id": str(tarea_id)},
            filas_afectadas=1,
            request=request,
        )
        return await self.get_tarea(tarea_id, current_user)

    async def cambiar_estado(
        self,
        id: uuid.UUID,
        data: TareaUpdateEstado,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> TareaRead:
        tarea = await self._repo.find_by_id(id)
        if tarea is None:
            raise NotFoundException(resource="Tarea", id=id)

        current_estado = TareaEstado(tarea.estado)
        target_estado = data.estado

        try:
            _TAREA_STATE_MACHINE.validate_transition(current_estado, target_estado)
        except TransitionError as e:
            raise ValidationException(message=str(e)) from e

        if current_estado == TareaEstado.RESUELTA and target_estado == TareaEstado.EN_PROGRESO:
            if not any(r in current_user.roles for r in _REOPEN_ROLES):
                raise ForbiddenException(action="Reabrir tarea resuelta")

        tarea.estado = target_estado.value
        await self._session.flush()

        if data.comentario:
            usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
            autor_id = usuarios[0].id if usuarios else current_user.user_id
            comentario = ComentarioTarea(
                tenant_id=tarea.tenant_id,
                tarea_id=tarea.id,
                autor_id=autor_id,
                texto=data.comentario,
            )
            self._session.add(comentario)
            await self._session.flush()

        await self._session.refresh(tarea)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.TAREA_ACTUALIZAR_ESTADO,
            detalle={
                "tarea_id": str(id),
                "de": current_estado.value,
                "a": target_estado.value,
            },
            filas_afectadas=1,
            request=request,
        )

        return await self.get_tarea(id, current_user)

    async def get_mis_tareas(
        self,
        current_user: CurrentUser,
        estado: str | None = None,
        materia_id: uuid.UUID | None = None,
        texto: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[TareaRead]:
        usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
        if not usuarios:
            return []
        usuario = usuarios[0]
        tareas = await self._repo.find_by_asignado(
            usuario_id=usuario.id,
            estado=estado,
            materia_id=materia_id,
            texto=texto,
            skip=skip,
            limit=limit,
        )
        return [TareaRead.model_validate(t) for t in tareas]

    async def get_all_managed(
        self,
        current_user: CurrentUser,
        estado: str | None = None,
        materia_id: uuid.UUID | None = None,
        asignado_a_id: uuid.UUID | None = None,
        texto: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[TareaRead]:
        tareas = await self._repo.find_all_managed(
            estado=estado,
            materia_id=materia_id,
            asignado_a_id=asignado_a_id,
            texto=texto,
            skip=skip,
            limit=limit,
        )
        return [TareaRead.model_validate(t) for t in tareas]

    async def get_tarea(self, id: uuid.UUID, current_user: CurrentUser) -> TareaRead:
        tarea = await self._repo.get_with_comments(id)
        if tarea is None:
            raise NotFoundException(resource="Tarea", id=id)
        return TareaRead.model_validate(tarea)

    async def delete_tarea(
        self,
        id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        tarea = await self._repo.find_by_id(id)
        if tarea is None:
            raise NotFoundException(resource="Tarea", id=id)
        await self._repo.soft_delete(id)
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.TAREA_ELIMINAR,
            detalle={"tarea_id": str(id)},
            filas_afectadas=1,
            request=request,
        )

    async def agregar_comentario(
        self,
        tarea_id: uuid.UUID,
        texto: str,
        current_user: CurrentUser,
    ) -> ComentarioRead:
        tarea = await self._repo.find_by_id(tarea_id)
        if tarea is None:
            raise NotFoundException(resource="Tarea", id=tarea_id)

        usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
        if not usuarios:
            raise NotFoundException(resource="Usuario", id=current_user.user_id)
        autor_id = usuarios[0].id

        comentario = ComentarioTarea(
            tenant_id=current_user.tenant_id,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=texto,
        )
        self._session.add(comentario)
        await self._session.flush()
        await self._session.refresh(comentario)
        return ComentarioRead.model_validate(comentario)
