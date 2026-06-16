import uuid

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi import File as FileForm
from fastapi import Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.schemas.programas import ProgramaMateriaRead, ProgramaMateriaUpdate
from app.services.programas_service import ProgramasService

_gestionar_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]

router = APIRouter(
    prefix="/api/v1/programas",
    tags=["programas"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=ProgramaMateriaRead, status_code=201, dependencies=_gestionar_guard)
async def upload_programa(
    dictado_id: uuid.UUID = Form(...),
    titulo: str = Form(...),
    archivo: UploadFile = FileForm(...),
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    service = ProgramasService.create(db, current_user.tenant_id)
    result = await service.upload_programa(
        dictado_id, titulo, archivo, current_user=current_user, request=request
    )
    await db.commit()
    return result


@router.patch("/{id}", response_model=ProgramaMateriaRead, dependencies=_gestionar_guard)
async def update_programa(
    id: uuid.UUID,
    titulo: str = Form(None),
    archivo: UploadFile = FileForm(None),
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    service = ProgramasService.create(db, current_user.tenant_id)
    data = ProgramaMateriaUpdate(titulo=titulo)
    result = await service.update_programa(
        id, data, archivo_opcional=archivo, current_user=current_user, request=request
    )
    await db.commit()
    return result


@router.get("/{id}", response_model=ProgramaMateriaRead, dependencies=_gestionar_guard)
async def get_programa(
    id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgramasService.create(db, current_user.tenant_id)
    return await service.get_programa(id, current_user=current_user)


@router.get("/por-dictado/{dictado_id}", response_model=ProgramaMateriaRead, dependencies=_gestionar_guard)
async def get_programa_by_dictado(
    dictado_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgramasService.create(db, current_user.tenant_id)
    return await service.get_by_dictado(dictado_id, current_user=current_user)


@router.delete("/{id}", status_code=204, dependencies=_gestionar_guard)
async def delete_programa(
    id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    service = ProgramasService.create(db, current_user.tenant_id)
    await service.delete_programa(id, current_user=current_user, request=request)
    await db.commit()


@router.get("/{id}/descargar", dependencies=_gestionar_guard)
async def download_programa(
    id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgramasService.create(db, current_user.tenant_id)
    return await service.download_programa(id, current_user=current_user)
