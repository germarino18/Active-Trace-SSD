import hashlib
import uuid

from starlette.requests import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.state_machine import StateMachine, TransitionError
from app.core.template_engine import TemplateEngine
from app.models.comunicacion import Comunicacion, ComunicacionEstado
from app.models.tenant import Tenant
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.comunicaciones import (
    ComunicacionPreview,
    ComunicacionRead,
    EnvioMasivoRequest,
    EnvioMasivoResponse,
    LoteResumen,
)
from app.services.audit.audit_logger import AuditLogger
from app.services.permission_service import PermissionResolver

_COMUNICACION_SM = StateMachine(
    state_enum=ComunicacionEstado,
    initial=ComunicacionEstado.PENDIENTE,
    transitions={
        ComunicacionEstado.PENDIENTE: [
            ComunicacionEstado.ENVIANDO,
            ComunicacionEstado.CANCELADO,
        ],
        ComunicacionEstado.ENVIANDO: [
            ComunicacionEstado.ENVIADO,
            ComunicacionEstado.ERROR,
        ],
    },
)

_APROBACION_PERMISO = "comunicacion:aprobar"

_TEMPLATE_ALLOWED_VARS = {
    "alumno_nombre",
    "alumno_apellido",
    "materia",
    "docente_nombre",
}


class ComunicacionesService:
    def __init__(
        self,
        comunicacion_repo: ComunicacionRepository,
        audit_repo: AuditLogRepository,
        materia_repo: MateriaRepository,
        usuario_repo: UsuarioRepository,
        session: AsyncSession,
    ):
        self._repo = comunicacion_repo
        self._materia_repo = materia_repo
        self._usuario_repo = usuario_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "ComunicacionesService":
        """Convenience factory for router dependency injection."""
        from app.repositories.usuario_repository import UsuarioRepository
        return cls(
            comunicacion_repo=ComunicacionRepository(session=session, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            materia_repo=MateriaRepository(session=session, tenant_id=tenant_id),
            usuario_repo=UsuarioRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def preview(
        self,
        template_engine: TemplateEngine,
        asunto_template: str,
        cuerpo_template: str,
        destinatario_info: dict[str, str],
    ) -> ComunicacionPreview:
        asunto = template_engine.render(asunto_template, destinatario_info)
        cuerpo = template_engine.render(cuerpo_template, destinatario_info)
        return ComunicacionPreview(asunto=asunto, cuerpo=cuerpo)

    async def enqueue_masivo(
        self,
        envio_data: EnvioMasivoRequest,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> EnvioMasivoResponse:
        materia = await self._materia_repo.find_by_id(envio_data.materia_id)
        if materia is None:
            raise NotFoundException(resource="Materia", id=envio_data.materia_id)

        tenant = await self._load_tenant(current_user.tenant_id)

        template_engine = TemplateEngine(allowed_variables=_TEMPLATE_ALLOWED_VARS)

        enviado_por = await self._resolve_enviado_por(current_user.user_id)
        docente_nombre = await self._resolve_docente_nombre(current_user.user_id)

        lote_id = uuid.uuid4()
        comunicaciones_creadas: list[Comunicacion] = []

        for dest in envio_data.destinatarios:
            values = {
                "alumno_nombre": dest.destinatario_nombre,
                "alumno_apellido": dest.destinatario_apellido,
                "materia": materia.nombre,
                "docente_nombre": docente_nombre,
            }
            asunto = template_engine.render(envio_data.asunto_template, values)
            cuerpo = template_engine.render(envio_data.cuerpo_template, values)
            destinatario_hash = hashlib.sha256(
                dest.destinatario_email.encode("utf-8")
            ).hexdigest()

            com = await self._repo.create(
                {
                    "enviado_por": enviado_por,
                    "materia_id": envio_data.materia_id,
                    "destinatario": dest.destinatario_email,
                    "destinatario_hash": destinatario_hash,
                    "asunto": asunto,
                    "cuerpo": cuerpo,
                    "lote_id": lote_id,
                }
            )
            comunicaciones_creadas.append(com)

        if not tenant.aprobacion_comunicaciones:
            for com in comunicaciones_creadas:
                _COMUNICACION_SM.validate_transition(
                    ComunicacionEstado(com.estado),
                    ComunicacionEstado.ENVIANDO,
                )
                await self._repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COMUNICACION_ENVIAR,
            detalle={
                "lote_id": str(lote_id),
                "total": len(comunicaciones_creadas),
                "materia_id": str(envio_data.materia_id),
                "auto_aprobado": not tenant.aprobacion_comunicaciones,
            },
            filas_afectadas=len(comunicaciones_creadas),
            request=request,
        )

        return EnvioMasivoResponse(
            lote_id=lote_id,
            total=len(comunicaciones_creadas),
        )

    async def aprobar_lote(
        self,
        lote_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        await self._check_aprobacion_permiso(current_user)

        comunicaciones = await self._repo.get_by_lote(lote_id)
        if not comunicaciones:
            raise NotFoundException(resource="Lote", id=lote_id)

        aprobadas = 0
        for com in comunicaciones:
            try:
                _COMUNICACION_SM.validate_transition(
                    ComunicacionEstado(com.estado),
                    ComunicacionEstado.ENVIANDO,
                )
                await self._repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)
                aprobadas += 1
            except TransitionError:
                continue

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COMUNICACION_ENVIAR,
            detalle={
                "lote_id": str(lote_id),
                "aprobadas": aprobadas,
                "total": len(comunicaciones),
            },
            filas_afectadas=aprobadas,
            request=request,
        )

    async def aprobar_individual(
        self,
        comunicacion_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        await self._check_aprobacion_permiso(current_user)

        com = await self._repo.find_by_id(comunicacion_id)
        if com is None:
            raise NotFoundException(resource="Comunicacion", id=comunicacion_id)

        _COMUNICACION_SM.validate_transition(
            ComunicacionEstado(com.estado),
            ComunicacionEstado.ENVIANDO,
        )
        await self._repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COMUNICACION_ENVIAR,
            detalle={
                "comunicacion_id": str(comunicacion_id),
                "lote_id": str(com.lote_id),
                "accion": "aprobar_individual",
            },
            filas_afectadas=1,
            request=request,
        )

    async def cancelar_lote(
        self,
        lote_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        await self._check_aprobacion_permiso(current_user)

        comunicaciones = await self._repo.get_by_lote(lote_id)
        if not comunicaciones:
            raise NotFoundException(resource="Lote", id=lote_id)

        canceladas = 0
        for com in comunicaciones:
            try:
                _COMUNICACION_SM.validate_transition(
                    ComunicacionEstado(com.estado),
                    ComunicacionEstado.CANCELADO,
                )
                await self._repo.update_estado(com.id, ComunicacionEstado.CANCELADO)
                canceladas += 1
            except TransitionError:
                continue

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COMUNICACION_ENVIAR,
            detalle={
                "lote_id": str(lote_id),
                "canceladas": canceladas,
                "total": len(comunicaciones),
                "accion": "cancelar_lote",
            },
            filas_afectadas=canceladas,
            request=request,
        )

    async def cancelar_individual(
        self,
        comunicacion_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        await self._check_aprobacion_permiso(current_user)

        com = await self._repo.find_by_id(comunicacion_id)
        if com is None:
            raise NotFoundException(resource="Comunicacion", id=comunicacion_id)

        _COMUNICACION_SM.validate_transition(
            ComunicacionEstado(com.estado),
            ComunicacionEstado.CANCELADO,
        )
        await self._repo.update_estado(com.id, ComunicacionEstado.CANCELADO)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COMUNICACION_ENVIAR,
            detalle={
                "comunicacion_id": str(comunicacion_id),
                "lote_id": str(com.lote_id),
                "accion": "cancelar_individual",
            },
            filas_afectadas=1,
            request=request,
        )

    async def get_estado(self, comunicacion_id: uuid.UUID) -> ComunicacionRead:
        com = await self._repo.find_by_id(comunicacion_id)
        if com is None:
            raise NotFoundException(resource="Comunicacion", id=comunicacion_id)
        return ComunicacionRead.model_validate(com)

    async def get_resumen_lote(self, lote_id: uuid.UUID) -> LoteResumen:
        counts = await self._repo.count_by_lote(lote_id)
        if counts["total"] == 0:
            raise NotFoundException(resource="Lote", id=lote_id)
        return LoteResumen(
            lote_id=lote_id,
            total=counts["total"],
            pendientes=counts["Pendiente"],
            enviados=counts["Enviado"],
            errores=counts["Error"],
            cancelados=counts["Cancelado"],
        )

    async def _load_tenant(self, tenant_id: uuid.UUID) -> Tenant:
        query = select(Tenant).where(Tenant.id == tenant_id)
        result = await self._session.execute(query)
        tenant = result.unique().scalar_one_or_none()
        if tenant is None:
            raise NotFoundException(resource="Tenant", id=tenant_id)
        return tenant

    async def _resolve_enviado_por(self, user_id: uuid.UUID) -> uuid.UUID:
        """Resolve User.id → Usuario.id for the enviado_por FK."""
        usuarios = await self._usuario_repo.find_by(user_id=user_id)
        if usuarios:
            return usuarios[0].id
        return user_id

    async def _resolve_docente_nombre(self, user_id: uuid.UUID) -> str:
        usuarios = await self._usuario_repo.find_by(user_id=user_id)
        if usuarios:
            u = usuarios[0]
            return f"{u.nombre} {u.apellidos}".strip()
        return "Docente"

    async def _check_aprobacion_permiso(self, current_user: CurrentUser) -> None:
        resolver = PermissionResolver(session=self._session)
        permissions = await resolver.get_effective_permissions(
            current_user.tenant_id, current_user.roles
        )
        if _APROBACION_PERMISO not in permissions:
            raise ForbiddenException(action=_APROBACION_PERMISO)
