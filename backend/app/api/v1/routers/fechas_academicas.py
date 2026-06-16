import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.fechas_academicas import (
    FechaAcademicaCreate,
    FechaAcademicaRead,
    FechaAcademicaUpdate,
    LmsContentFragment,
)
from app.services.fechas_academicas_service import FechasAcademicasService

_gestionar_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]

router = APIRouter(
    prefix="/api/v1/fechas-academicas",
    tags=["fechas-academicas"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=FechaAcademicaRead, status_code=201, dependencies=_gestionar_guard)
async def create_fecha(
    data: FechaAcademicaCreate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    result = await service.create_fecha(data, current_user=current_user, request=request)
    await db.commit()
    return result


@router.patch("/{id}", response_model=FechaAcademicaRead, dependencies=_gestionar_guard)
async def update_fecha(
    id: uuid.UUID,
    data: FechaAcademicaUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    result = await service.update_fecha(id, data, current_user=current_user, request=request)
    await db.commit()
    return result


@router.get("/calendario", response_model=dict[str, list[FechaAcademicaRead]], dependencies=_gestionar_guard)
async def calendario_fechas(
    dictado_id: uuid.UUID = Query(...),
    periodo: str | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    return await service.list_calendar(dictado_id, periodo, current_user=current_user)


@router.get("/fragmento-lms", response_model=LmsContentFragment, dependencies=_gestionar_guard)
async def fragmento_lms(
    dictado_id: uuid.UUID = Query(...),
    periodo: str | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    return await service.generate_lms_fragment(dictado_id, periodo, current_user=current_user)


@router.get("", response_model=list[FechaAcademicaRead], dependencies=_gestionar_guard)
async def list_fechas(
    dictado_id: uuid.UUID = Query(...),
    periodo: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    return await service.list_fechas(
        dictado_id, periodo, skip, limit, current_user=current_user
    )


@router.get("/{id}", response_model=FechaAcademicaRead, dependencies=_gestionar_guard)
async def get_fecha(
    id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    return await service.get_fecha(id, current_user=current_user)


@router.delete("/{id}", status_code=204, dependencies=_gestionar_guard)
async def delete_fecha(
    id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    service = FechasAcademicasService.create(db, current_user.tenant_id)
    await service.delete_fecha(id, current_user=current_user, request=request)
    await db.commit()
