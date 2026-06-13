from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.dictado import Dictado
from app.models.materia import Materia
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate,
    CohorteCreate,
    CohorteResponse,
    CohorteUpdate,
    DictadoCreate,
    DictadoResponse,
    DictadoUpdate,
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate,
)
from app.services.estructura.carrera_service import CarreraService
from app.services.estructura.cohorte_service import CohorteService
from app.services.estructura.dictado_service import DictadoService
from app.services.estructura.materia_service import MateriaService

router = APIRouter(prefix="/api/admin", tags=["estructura"])

# All estructura-academica endpoints require estructura:gestionar (D3/RBAC).
_estructura_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]


# ── Carreras ───────────────────────────────────────────────────────────


@router.get("/carreras", response_model=list[CarreraResponse], dependencies=_estructura_guard)
async def list_carreras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CarreraRepository(session=db, tenant_id=current_user.tenant_id)
    carreras = await repo.find_all(skip=skip, limit=limit)
    return [_carrera_to_response(c) for c in carreras]


@router.post("/carreras", response_model=CarreraResponse, status_code=201, dependencies=_estructura_guard)
async def create_carrera(
    data: CarreraCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _carrera_service(db, current_user.tenant_id)
    carrera = await service.create(data, current_user=current_user, request=request)
    await db.commit()
    return _carrera_to_response(carrera)


@router.get("/carreras/{carrera_id}", response_model=CarreraResponse, dependencies=_estructura_guard)
async def get_carrera(
    carrera_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CarreraRepository(session=db, tenant_id=current_user.tenant_id)
    carrera = await repo.find_by_id(carrera_id)
    if carrera is None:
        raise NotFoundException(resource="Carrera", id=carrera_id)
    return _carrera_to_response(carrera)


@router.put("/carreras/{carrera_id}", response_model=CarreraResponse, dependencies=_estructura_guard)
async def update_carrera(
    carrera_id: UUID,
    data: CarreraUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CarreraRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(carrera_id) is None:
        raise NotFoundException(resource="Carrera", id=carrera_id)
    service = _carrera_service(db, current_user.tenant_id)
    carrera = await service.update(carrera_id, data, current_user=current_user, request=request)
    await db.commit()
    return _carrera_to_response(carrera)


@router.delete("/carreras/{carrera_id}", response_model=CarreraResponse, dependencies=_estructura_guard)
async def delete_carrera(
    carrera_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CarreraRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(carrera_id) is None:
        raise NotFoundException(resource="Carrera", id=carrera_id)
    service = _carrera_service(db, current_user.tenant_id)
    carrera = await service.soft_delete(carrera_id, current_user=current_user, request=request)
    await db.commit()
    return _carrera_to_response(carrera)


# ── Materias ───────────────────────────────────────────────────────────


@router.get("/materias", response_model=list[MateriaResponse], dependencies=_estructura_guard)
async def list_materias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = MateriaRepository(session=db, tenant_id=current_user.tenant_id)
    materias = await repo.find_all(skip=skip, limit=limit)
    return [_materia_to_response(m) for m in materias]


@router.post("/materias", response_model=MateriaResponse, status_code=201, dependencies=_estructura_guard)
async def create_materia(
    data: MateriaCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _materia_service(db, current_user.tenant_id)
    materia = await service.create(data, current_user=current_user, request=request)
    await db.commit()
    return _materia_to_response(materia)


@router.get("/materias/{materia_id}", response_model=MateriaResponse, dependencies=_estructura_guard)
async def get_materia(
    materia_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = MateriaRepository(session=db, tenant_id=current_user.tenant_id)
    materia = await repo.find_by_id(materia_id)
    if materia is None:
        raise NotFoundException(resource="Materia", id=materia_id)
    return _materia_to_response(materia)


@router.put("/materias/{materia_id}", response_model=MateriaResponse, dependencies=_estructura_guard)
async def update_materia(
    materia_id: UUID,
    data: MateriaUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = MateriaRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(materia_id) is None:
        raise NotFoundException(resource="Materia", id=materia_id)
    service = _materia_service(db, current_user.tenant_id)
    materia = await service.update(materia_id, data, current_user=current_user, request=request)
    await db.commit()
    return _materia_to_response(materia)


@router.delete("/materias/{materia_id}", response_model=MateriaResponse, dependencies=_estructura_guard)
async def delete_materia(
    materia_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = MateriaRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(materia_id) is None:
        raise NotFoundException(resource="Materia", id=materia_id)
    service = _materia_service(db, current_user.tenant_id)
    materia = await service.soft_delete(materia_id, current_user=current_user, request=request)
    await db.commit()
    return _materia_to_response(materia)


# ── Cohortes ──────────────────────────────────────────────────────────


@router.get("/cohortes", response_model=list[CohorteResponse], dependencies=_estructura_guard)
async def list_cohortes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CohorteRepository(session=db, tenant_id=current_user.tenant_id)
    cohortes = await repo.find_all(skip=skip, limit=limit)
    return [_cohorte_to_response(c) for c in cohortes]


@router.post("/cohortes", response_model=CohorteResponse, status_code=201, dependencies=_estructura_guard)
async def create_cohorte(
    data: CohorteCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _cohorte_service(db, current_user.tenant_id)
    cohorte = await service.create(data, current_user=current_user, request=request)
    await db.commit()
    return _cohorte_to_response(cohorte)


@router.get("/cohortes/{cohorte_id}", response_model=CohorteResponse, dependencies=_estructura_guard)
async def get_cohorte(
    cohorte_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CohorteRepository(session=db, tenant_id=current_user.tenant_id)
    cohorte = await repo.find_by_id(cohorte_id)
    if cohorte is None:
        raise NotFoundException(resource="Cohorte", id=cohorte_id)
    return _cohorte_to_response(cohorte)


@router.put("/cohortes/{cohorte_id}", response_model=CohorteResponse, dependencies=_estructura_guard)
async def update_cohorte(
    cohorte_id: UUID,
    data: CohorteUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CohorteRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(cohorte_id) is None:
        raise NotFoundException(resource="Cohorte", id=cohorte_id)
    service = _cohorte_service(db, current_user.tenant_id)
    cohorte = await service.update(cohorte_id, data, current_user=current_user, request=request)
    await db.commit()
    return _cohorte_to_response(cohorte)


@router.delete("/cohortes/{cohorte_id}", response_model=CohorteResponse, dependencies=_estructura_guard)
async def delete_cohorte(
    cohorte_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CohorteRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(cohorte_id) is None:
        raise NotFoundException(resource="Cohorte", id=cohorte_id)
    service = _cohorte_service(db, current_user.tenant_id)
    cohorte = await service.soft_delete(cohorte_id, current_user=current_user, request=request)
    await db.commit()
    return _cohorte_to_response(cohorte)


# ── Dictados ──────────────────────────────────────────────────────────


@router.get("/dictados", response_model=list[DictadoResponse], dependencies=_estructura_guard)
async def list_dictados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DictadoRepository(session=db, tenant_id=current_user.tenant_id)
    dictados = await repo.find_all(skip=skip, limit=limit)
    return [_dictado_to_response(d) for d in dictados]


@router.post("/dictados", response_model=DictadoResponse, status_code=201, dependencies=_estructura_guard)
async def create_dictado(
    data: DictadoCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _dictado_service(db, current_user.tenant_id)
    dictado = await service.create(data, current_user=current_user, request=request)
    await db.commit()
    return _dictado_to_response(dictado)


@router.get("/dictados/{dictado_id}", response_model=DictadoResponse, dependencies=_estructura_guard)
async def get_dictado(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DictadoRepository(session=db, tenant_id=current_user.tenant_id)
    dictado = await repo.find_by_id(dictado_id)
    if dictado is None:
        raise NotFoundException(resource="Dictado", id=dictado_id)
    return _dictado_to_response(dictado)


@router.put("/dictados/{dictado_id}", response_model=DictadoResponse, dependencies=_estructura_guard)
async def update_dictado(
    dictado_id: UUID,
    data: DictadoUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DictadoRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(dictado_id) is None:
        raise NotFoundException(resource="Dictado", id=dictado_id)
    service = _dictado_service(db, current_user.tenant_id)
    dictado = await service.update(dictado_id, data, current_user=current_user, request=request)
    await db.commit()
    return _dictado_to_response(dictado)


@router.delete("/dictados/{dictado_id}", response_model=DictadoResponse, dependencies=_estructura_guard)
async def delete_dictado(
    dictado_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DictadoRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(dictado_id) is None:
        raise NotFoundException(resource="Dictado", id=dictado_id)
    service = _dictado_service(db, current_user.tenant_id)
    dictado = await service.soft_delete(dictado_id, current_user=current_user, request=request)
    await db.commit()
    return _dictado_to_response(dictado)


# ── Service factories ───────────────────────────────────────────────────


def _carrera_service(db: AsyncSession, tenant_id: UUID) -> CarreraService:
    return CarreraService(
        carrera_repo=CarreraRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


def _materia_service(db: AsyncSession, tenant_id: UUID) -> MateriaService:
    return MateriaService(
        materia_repo=MateriaRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


def _cohorte_service(db: AsyncSession, tenant_id: UUID) -> CohorteService:
    return CohorteService(
        cohorte_repo=CohorteRepository(session=db, tenant_id=tenant_id),
        carrera_repo=CarreraRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


def _dictado_service(db: AsyncSession, tenant_id: UUID) -> DictadoService:
    return DictadoService(
        dictado_repo=DictadoRepository(session=db, tenant_id=tenant_id),
        materia_repo=MateriaRepository(session=db, tenant_id=tenant_id),
        carrera_repo=CarreraRepository(session=db, tenant_id=tenant_id),
        cohorte_repo=CohorteRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


# ── Response mappers ─────────────────────────────────────────────────────


def _carrera_to_response(carrera: Carrera) -> CarreraResponse:
    return CarreraResponse(
        id=carrera.id,
        tenant_id=carrera.tenant_id,
        codigo=carrera.codigo,
        nombre=carrera.nombre,
        estado=carrera.estado,
        deleted_at=carrera.deleted_at is not None,
    )


def _materia_to_response(materia: Materia) -> MateriaResponse:
    return MateriaResponse(
        id=materia.id,
        tenant_id=materia.tenant_id,
        codigo=materia.codigo,
        nombre=materia.nombre,
        estado=materia.estado,
        deleted_at=materia.deleted_at is not None,
    )


def _cohorte_to_response(cohorte: Cohorte) -> CohorteResponse:
    return CohorteResponse(
        id=cohorte.id,
        tenant_id=cohorte.tenant_id,
        carrera_id=cohorte.carrera_id,
        nombre=cohorte.nombre,
        anio=cohorte.anio,
        vig_desde=cohorte.vig_desde,
        vig_hasta=cohorte.vig_hasta,
        estado=cohorte.estado,
        deleted_at=cohorte.deleted_at is not None,
    )


def _dictado_to_response(dictado: Dictado) -> DictadoResponse:
    return DictadoResponse(
        id=dictado.id,
        tenant_id=dictado.tenant_id,
        materia_id=dictado.materia_id,
        carrera_id=dictado.carrera_id,
        cohorte_id=dictado.cohorte_id,
        estado=dictado.estado,
        deleted_at=dictado.deleted_at is not None,
    )
