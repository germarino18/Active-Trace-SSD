from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.core.acciones_auditoria import AccionAuditoria
from app.core.dependencies import get_db
from app.core.exceptions import ValidationException
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.auth import CurrentUser
from app.schemas.perfil import PerfilResponse, PerfilUpdate
from app.services.audit.audit_logger import AuditLogger
from app.services.perfil_service import PerfilService

router = APIRouter(prefix="/api/v1", tags=["perfil"])


def _perfil_service(db: AsyncSession, tenant_id: UUID) -> PerfilService:
    return PerfilService(db=db, tenant_id=tenant_id)


def _audit_logger(db: AsyncSession, tenant_id: UUID) -> AuditLogger:
    return AuditLogger(repository=AuditLogRepository(session=db, tenant_id=tenant_id))


@router.get("/perfil", response_model=PerfilResponse)
async def get_perfil(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _perfil_service(db, current_user.tenant_id)
    usuario, email = await service.get_perfil(current_user.user_id)
    return PerfilResponse(
        id=usuario.id,
        user_id=usuario.user_id,
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        email=email,
        dni=usuario.dni,
        cuil=usuario.cuil,
        cbu=usuario.cbu,
        alias_cbu=usuario.alias_cbu,
        banco=usuario.banco,
        regional=usuario.regional,
        legajo=usuario.legajo,
        legajo_profesional=usuario.legajo_profesional,
        facturador=usuario.facturador,
        estado=usuario.estado,
    )


@router.patch("/perfil", response_model=PerfilResponse)
async def update_perfil(
    data: PerfilUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _perfil_service(db, current_user.tenant_id)
    try:
        usuario, email = await service.update_perfil(current_user.user_id, data)
    except ValueError as e:
        raise ValidationException(str(e))

    audit = _audit_logger(db, current_user.tenant_id)
    await audit.log(
        current_user=current_user,
        accion=AccionAuditoria.PERFIL_ACTUALIZAR,
        detalle={"cambios": list(data.model_dump(exclude_unset=True).keys())},
        filas_afectadas=1,
        request=request,
    )

    await db.commit()

    return PerfilResponse(
        id=usuario.id,
        user_id=usuario.user_id,
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        email=email,
        dni=usuario.dni,
        cuil=usuario.cuil,
        cbu=usuario.cbu,
        alias_cbu=usuario.alias_cbu,
        banco=usuario.banco,
        regional=usuario.regional,
        legajo=usuario.legajo,
        legajo_profesional=usuario.legajo_profesional,
        facturador=usuario.facturador,
        estado=usuario.estado,
    )
