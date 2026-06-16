"""Service for avisos (announcements) with acknowledgment tracking."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException
from app.models.aviso import Aviso, AcknowledgmentAviso, AlcanceAviso
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.aviso_repository import AvisoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.avisos import (
    AcknowledgmentStats,
    AvisoCreate,
    AvisoRead,
    AvisoUpdate,
    AvisoVisibleRead,
    ConfirmResponse,
)
from app.services.audit.audit_logger import AuditLogger


class AvisoService:
    def __init__(
        self,
        aviso_repo: AvisoRepository,
        audit_repo: AuditLogRepository,
        usuario_repo: UsuarioRepository,
        session: AsyncSession,
    ):
        self._repo = aviso_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._usuario_repo = usuario_repo
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "AvisoService":
        return cls(
            aviso_repo=AvisoRepository(session=session, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            usuario_repo=UsuarioRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def create_aviso(
        self,
        data: AvisoCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> AvisoRead:
        aviso = await self._repo.create(data.model_dump())
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.AVISO_CREAR,
            detalle={
                "aviso_id": str(aviso.id),
                "titulo": aviso.titulo,
                "alcance": aviso.alcance,
            },
            filas_afectadas=1,
            request=request,
        )
        return AvisoRead.model_validate(aviso)

    async def update(
        self,
        id: uuid.UUID,
        data: AvisoUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> AvisoRead:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        aviso = await self._repo.update(id, update_data)
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.AVISO_ACTUALIZAR,
            detalle={
                "aviso_id": str(id),
                "changes": update_data,
            },
            filas_afectadas=1,
            request=request,
        )
        return AvisoRead.model_validate(aviso)

    async def delete(
        self,
        id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        await self._repo.soft_delete(id)
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.AVISO_ELIMINAR,
            detalle={"aviso_id": str(id)},
            filas_afectadas=1,
            request=request,
        )

    async def get_by_id(self, id: uuid.UUID) -> AvisoRead:
        aviso = await self._repo.find_by_id(id)
        if aviso is None:
            raise NotFoundException(resource="Aviso", id=id)
        return AvisoRead.model_validate(aviso)

    async def get_all_managed(self, skip: int = 0, limit: int = 100) -> list[AvisoRead]:
        avisos = await self._repo.find_all_managed(skip=skip, limit=limit)
        return [AvisoRead.model_validate(a) for a in avisos]

    async def get_visible(self, current_user: CurrentUser) -> list[AvisoVisibleRead]:
        usuario = await self._resolve_usuario(current_user.user_id)
        materia_ids, cohorte_ids = await self._resolve_user_context(current_user)
        avisos = await self._repo.find_visible(
            usuario_id=usuario.id,
            roles=current_user.roles,
            materia_ids=materia_ids,
            cohorte_ids=cohorte_ids,
        )
        confirmed_ids = await self._get_confirmed_aviso_ids(usuario.id)
        return [
            AvisoVisibleRead(
                **{k: getattr(a, k) for k in AvisoVisibleRead.model_fields if hasattr(a, k)},
                acknowledged=a.id in confirmed_ids,
            )
            for a in avisos
        ]

    async def get_pendientes(self, current_user: CurrentUser) -> list[AvisoVisibleRead]:
        usuario = await self._resolve_usuario(current_user.user_id)
        materia_ids, cohorte_ids = await self._resolve_user_context(current_user)
        avisos = await self._repo.find_pending_ack(
            usuario_id=usuario.id,
            roles=current_user.roles,
            materia_ids=materia_ids,
            cohorte_ids=cohorte_ids,
        )
        return [
            AvisoVisibleRead(
                **{k: getattr(a, k) for k in AvisoVisibleRead.model_fields if hasattr(a, k)},
                acknowledged=False,
            )
            for a in avisos
        ]

    async def confirmar(
        self,
        aviso_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> ConfirmResponse:
        aviso = await self._repo.find_by_id(aviso_id)
        if aviso is None:
            raise NotFoundException(resource="Aviso", id=aviso_id)

        usuario = await self._resolve_usuario(current_user.user_id)
        ack_repo = AcknowledgmentRepository(
            session=self._session,
            tenant_id=current_user.tenant_id,
        )
        existing = await ack_repo.find_by(
            aviso_id=aviso_id,
            usuario_id=usuario.id,
        )
        if not existing:
            await ack_repo.create({
                "aviso_id": aviso_id,
                "usuario_id": usuario.id,
            })
            await self._audit.log(
                current_user=current_user,
                accion=AccionAuditoria.AVISO_CONFIRMAR,
                detalle={
                    "aviso_id": str(aviso_id),
                    "titulo": aviso.titulo,
                },
                filas_afectadas=1,
                request=request,
            )

        return ConfirmResponse(acknowledged=True)

    async def get_stats(
        self,
        aviso_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> AcknowledgmentStats:
        aviso = await self._repo.find_by_id(aviso_id)
        if aviso is None:
            raise NotFoundException(resource="Aviso", id=aviso_id)

        counts = await self._repo.count_acknowledgments(aviso_id)
        return AcknowledgmentStats(
            total=counts["total"],
            confirmados=counts["confirmados"],
            pendientes=counts["total"] - counts["confirmados"],
        )

    async def _resolve_usuario(self, user_id: uuid.UUID) -> Usuario:
        usuarios = await self._usuario_repo.find_by(user_id=user_id)
        if not usuarios:
            raise NotFoundException(resource="Usuario", id=user_id)
        return usuarios[0]

    async def _resolve_user_context(
        self, current_user: CurrentUser
    ) -> tuple[list[uuid.UUID], list[uuid.UUID]]:
        usuarios = await self._usuario_repo.find_by(user_id=current_user.user_id)
        if not usuarios:
            return [], []
        usuario = usuarios[0]
        from app.repositories.asignacion_repository import AsignacionRepository
        asignacion_repo = AsignacionRepository(
            session=self._session,
            tenant_id=current_user.tenant_id,
        )
        asignaciones = await asignacion_repo.find_mis_equipos_vigentes(
            tenant_id=current_user.tenant_id,
            usuario_id=usuario.id,
        )
        materia_ids = list({a.materia_id for a in asignaciones if a.materia_id is not None})
        cohorte_ids = list({a.cohorte_id for a in asignaciones if a.cohorte_id is not None})
        return materia_ids, cohorte_ids

    async def _get_confirmed_aviso_ids(self, usuario_id: uuid.UUID) -> set[uuid.UUID]:
        from app.models.aviso import AcknowledgmentAviso
        query = select(AcknowledgmentAviso.aviso_id).where(
            AcknowledgmentAviso.usuario_id == usuario_id,
            AcknowledgmentAviso.deleted_at.is_(None),
        )
        result = await self._session.execute(query)
        return set(result.scalars().all())


class AcknowledgmentRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        self.session = session
        self.tenant_id = tenant_id

    async def find_by(self, **filters) -> list:
        from sqlalchemy import select as sa_select
        query = sa_select(AcknowledgmentAviso).where(
            *[getattr(AcknowledgmentAviso, k) == v for k, v in filters.items()],
            AcknowledgmentAviso.deleted_at.is_(None),
        )
        if self.tenant_id is not None:
            query = query.where(AcknowledgmentAviso.tenant_id == self.tenant_id)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def create(self, data: dict) -> AcknowledgmentAviso:
        if self.tenant_id is not None:
            data.setdefault("tenant_id", self.tenant_id)
        instance = AcknowledgmentAviso(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
