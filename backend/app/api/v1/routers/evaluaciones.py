from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.models.evaluacion_materia import EvaluacionMateria
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.evaluacion_materia_repository import EvaluacionMateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.evaluacion_materia import (
    EvaluacionMateriaCreate,
    EvaluacionMateriaResponse,
    EvaluacionMateriaUpdate,
)
from app.services.audit.audit_logger import AuditLogger

router = APIRouter(prefix="/api/v1/evaluaciones", tags=["evaluaciones"])

_gestionar_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]


@router.get("", response_model=list[EvaluacionMateriaResponse])
async def list_evaluaciones(
    materia_id: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = EvaluacionMateriaRepository(session=db, tenant_id=current_user.tenant_id)
    evaluaciones = await repo.list_by_tenant(materia_id=materia_id, skip=skip, limit=limit)
    return [_evaluacion_to_response(e) for e in evaluaciones]


@router.post("", response_model=EvaluacionMateriaResponse, status_code=201, dependencies=_gestionar_guard)
async def create_evaluacion(
    data: EvaluacionMateriaCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = EvaluacionMateriaRepository(session=db, tenant_id=current_user.tenant_id)
    audit_logger = AuditLogger(repository=AuditLogRepository(session=db, tenant_id=current_user.tenant_id))
    create_data = data.model_dump()
    create_data["created_by_id"] = current_user.user_id
    create_data["updated_by_id"] = current_user.user_id
    evaluacion = await repo.create(create_data)
    await db.commit()
    await audit_logger.log(
        current_user=current_user,
        accion="evaluacion_materia.create",
        detalle=data.model_dump(mode="json"),
        filas_afectadas=1,
        request=request,
    )
    return _evaluacion_to_response(evaluacion)


@router.put("/{evaluacion_id}", response_model=EvaluacionMateriaResponse, dependencies=_gestionar_guard)
async def update_evaluacion(
    evaluacion_id: UUID,
    data: EvaluacionMateriaUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = EvaluacionMateriaRepository(session=db, tenant_id=current_user.tenant_id)
    evaluacion = await repo.find_by_id(evaluacion_id)
    if evaluacion is None:
        raise NotFoundException(resource="EvaluacionMateria", id=evaluacion_id)
    audit_logger = AuditLogger(repository=AuditLogRepository(session=db, tenant_id=current_user.tenant_id))
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_by_id"] = current_user.user_id
    evaluacion = await repo.update(evaluacion_id, update_data)
    await db.commit()
    old_serializable = {}
    for c in EvaluacionMateria.__table__.columns:
        v = getattr(evaluacion, c.name)
        if hasattr(v, "isoformat"):
            old_serializable[c.name] = v.isoformat()
        elif isinstance(v, (bytes, bytearray)):
            old_serializable[c.name] = v.hex()
        else:
            old_serializable[c.name] = str(v) if hasattr(v, "int") else v
    new_serializable = {}
    for k, v in update_data.items():
        if hasattr(v, "isoformat"):
            new_serializable[k] = v.isoformat()
        elif isinstance(v, (bytes, bytearray)):
            new_serializable[k] = v.hex()
        else:
            new_serializable[k] = str(v) if hasattr(v, "int") else v
    await audit_logger.log(
        current_user=current_user,
        accion="evaluacion_materia.update",
        detalle={"old": old_serializable, "new": new_serializable},
        filas_afectadas=1,
        request=request,
    )
    return _evaluacion_to_response(evaluacion)


@router.delete("/{evaluacion_id}", response_model=EvaluacionMateriaResponse, dependencies=_gestionar_guard)
async def delete_evaluacion(
    evaluacion_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = EvaluacionMateriaRepository(session=db, tenant_id=current_user.tenant_id)
    evaluacion = await repo.find_by_id(evaluacion_id)
    if evaluacion is None:
        raise NotFoundException(resource="EvaluacionMateria", id=evaluacion_id)
    audit_logger = AuditLogger(repository=AuditLogRepository(session=db, tenant_id=current_user.tenant_id))
    old_data = {}
    for c in EvaluacionMateria.__table__.columns:
        v = getattr(evaluacion, c.name)
        if hasattr(v, "isoformat"):
            old_data[c.name] = v.isoformat()
        elif isinstance(v, (bytes, bytearray)):
            old_data[c.name] = v.hex()
        else:
            old_data[c.name] = str(v) if hasattr(v, "int") else v
    evaluacion = await repo.soft_delete(evaluacion_id)
    await db.commit()
    await audit_logger.log(
        current_user=current_user,
        accion="evaluacion_materia.delete",
        detalle=old_data,
        filas_afectadas=1,
        request=request,
    )
    return _evaluacion_to_response(evaluacion)


def _evaluacion_to_response(e: EvaluacionMateria) -> EvaluacionMateriaResponse:
    return EvaluacionMateriaResponse(
        id=e.id,
        materia_id=e.materia_id,
        cohorte_id=e.cohorte_id,
        tipo=e.tipo,
        instancia=e.instancia,
        fecha=e.fecha,
        titulo=e.titulo,
        deleted_at=e.deleted_at is not None,
    )
