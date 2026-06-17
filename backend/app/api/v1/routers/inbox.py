from uuid import UUID

from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.acciones_auditoria import AccionAuditoria
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.schemas.mensajeria import HiloResponse, MensajeResponse, ResponderRequest
from app.services.audit.audit_logger import AuditLogger
from app.services.mensajeria_service import MensajeriaService

router = APIRouter(
    prefix="/api/v1/inbox",
    tags=["inbox"],
    dependencies=[Depends(require_permission(Perm.INBOX_ACCEDER))],
)


def _mensajeria_service(db: AsyncSession, tenant_id: UUID) -> MensajeriaService:
    return MensajeriaService(db=db, tenant_id=tenant_id)


def _audit_logger(db: AsyncSession, tenant_id: UUID) -> AuditLogger:
    return AuditLogger(repository=AuditLogRepository(session=db, tenant_id=tenant_id))


async def _resolver_usuario_id(
    db: AsyncSession, tenant_id: UUID, user_id: UUID
) -> UUID:
    """Resuelve Usuario.id a partir de User.id."""
    repo = BaseRepository(model=Usuario, session=db, tenant_id=tenant_id)
    usuarios = await repo.find_by(user_id=user_id)
    if not usuarios:
        raise NotFoundException(resource="Usuario", id=user_id)
    return usuarios[0].id


@router.get("/hilos", response_model=list[HiloResponse])
async def list_hilos(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _mensajeria_service(db, current_user.tenant_id)
    usuario_id = await _resolver_usuario_id(db, current_user.tenant_id, current_user.user_id)
    return await service.list_hilos(usuario_id)


@router.get("/hilos/{hilo_id}", response_model=list[MensajeResponse])
async def get_hilo(
    hilo_id: UUID = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _mensajeria_service(db, current_user.tenant_id)
    usuario_id = await _resolver_usuario_id(db, current_user.tenant_id, current_user.user_id)
    return await service.get_hilo(hilo_id, usuario_id)


@router.post("/hilos/{hilo_id}/responder", response_model=MensajeResponse, status_code=201)
async def responder(
    data: ResponderRequest,
    request: Request,
    hilo_id: UUID = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _mensajeria_service(db, current_user.tenant_id)
    usuario_id = await _resolver_usuario_id(db, current_user.tenant_id, current_user.user_id)
    mensaje = await service.responder(hilo_id, usuario_id, data.contenido)

    audit = _audit_logger(db, current_user.tenant_id)
    await audit.log(
        current_user=current_user,
        accion=AccionAuditoria.MENSAJE_RESPONDER,
        detalle={"hilo_id": str(hilo_id)},
        filas_afectadas=1,
        request=request,
    )

    await db.commit()
    return mensaje
