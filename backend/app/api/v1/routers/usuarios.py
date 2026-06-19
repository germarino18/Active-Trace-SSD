from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException
from app.core.permissions import Perm
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.rol_repository import RolRepository
from app.repositories.usuario_rol_repository import UsuarioRolRepository
from app.schemas.auth import CurrentUser
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.schemas.usuario_rol import UsuarioRolCreate, UsuarioRolResponse
from app.services.audit.audit_logger import AuditLogger
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/admin", tags=["usuarios"])

# All usuarios endpoints require usuarios:gestionar (D5/RBAC, Regla Dura #10).
_usuarios_guard = [Depends(require_permission(Perm.USUARIOS_GESTIONAR))]


@router.get("/usuarios", response_model=list[UsuarioResponse], dependencies=_usuarios_guard)
async def list_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UsuarioRepository(session=db, tenant_id=current_user.tenant_id)
    usuarios = await repo.find_all(skip=skip, limit=limit)
    return [_usuario_to_response(u) for u in usuarios]


@router.post("/usuarios", response_model=UsuarioResponse, status_code=201, dependencies=_usuarios_guard)
async def create_usuario(
    data: UsuarioCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = _usuario_service(db, current_user.tenant_id)
    usuario = await service.create(data, current_user=current_user, request=request)
    await db.commit()
    return _usuario_to_response(usuario)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse, dependencies=_usuarios_guard)
async def get_usuario(
    usuario_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UsuarioRepository(session=db, tenant_id=current_user.tenant_id)
    usuario = await repo.find_by_id(usuario_id)
    if usuario is None:
        raise NotFoundException(resource="Usuario", id=usuario_id)
    return _usuario_to_response(usuario)


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioResponse, dependencies=_usuarios_guard)
async def update_usuario(
    usuario_id: UUID,
    data: UsuarioUpdate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UsuarioRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(usuario_id) is None:
        raise NotFoundException(resource="Usuario", id=usuario_id)
    service = _usuario_service(db, current_user.tenant_id)
    usuario = await service.update(usuario_id, data, current_user=current_user, request=request)
    await db.commit()
    return _usuario_to_response(usuario)


@router.delete("/usuarios/{usuario_id}", response_model=UsuarioResponse, dependencies=_usuarios_guard)
async def delete_usuario(
    usuario_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UsuarioRepository(session=db, tenant_id=current_user.tenant_id)
    if await repo.find_by_id(usuario_id) is None:
        raise NotFoundException(resource="Usuario", id=usuario_id)
    service = _usuario_service(db, current_user.tenant_id)
    usuario = await service.soft_delete(usuario_id, current_user=current_user, request=request)
    await db.commit()
    return _usuario_to_response(usuario)


# ── Usuario-Rol assignments (TASK 4, C-34) ──────────────────────────────


@router.get(
    "/usuarios/{usuario_id}/roles",
    response_model=list[UsuarioRolResponse],
    dependencies=_usuarios_guard,
)
async def list_usuario_roles(
    usuario_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UsuarioRolRepository(session=db, tenant_id=current_user.tenant_id)
    rol_repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    assignments = await repo.find_by_usuario(usuario_id)
    rol_map = {r.id: r for r in await rol_repo.find_all()}
    result = []
    for a in assignments:
        rol = rol_map.get(a.rol_id)
        result.append(
            UsuarioRolResponse(
                id=a.id,
                usuario_id=a.usuario_id,
                rol_id=a.rol_id,
                rol_nombre=rol.nombre if rol else None,
                desde=a.desde,
                hasta=a.hasta,
                created_at=a.created_at,
            )
        )
    return result


@router.post(
    "/usuarios/{usuario_id}/roles",
    response_model=UsuarioRolResponse,
    status_code=201,
    dependencies=_usuarios_guard,
)
async def assign_usuario_rol(
    usuario_id: UUID,
    data: UsuarioRolCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    usuario_repo = UsuarioRepository(session=db, tenant_id=current_user.tenant_id)
    if await usuario_repo.find_by_id(usuario_id) is None:
        raise NotFoundException(resource="Usuario", id=usuario_id)

    rol_repo = RolRepository(session=db, tenant_id=current_user.tenant_id)
    rol = await rol_repo.find_by_id(data.rol_id)
    if rol is None:
        raise NotFoundException(resource="Rol", id=data.rol_id)

    repo = UsuarioRolRepository(session=db, tenant_id=current_user.tenant_id)
    create_data = data.model_dump()
    create_data["usuario_id"] = usuario_id
    create_data["tenant_id"] = current_user.tenant_id
    create_data["created_by_id"] = current_user.user_id
    create_data["updated_by_id"] = current_user.user_id
    assignment = await repo.create(create_data)
    await db.commit()

    audit_logger = AuditLogger(
        repository=AuditLogRepository(session=db, tenant_id=current_user.tenant_id)
    )
    await audit_logger.log(
        current_user=current_user,
        accion="usuario_rol.assign",
        detalle={"usuario_id": str(usuario_id), "rol_id": str(data.rol_id)},
        filas_afectadas=1,
        request=request,
    )

    return UsuarioRolResponse(
        id=assignment.id,
        usuario_id=assignment.usuario_id,
        rol_id=assignment.rol_id,
        rol_nombre=rol.nombre,
        desde=assignment.desde,
        hasta=assignment.hasta,
        created_at=assignment.created_at,
    )


@router.delete(
    "/usuarios/{usuario_id}/roles/{rol_id}",
    dependencies=_usuarios_guard,
)
async def remove_usuario_rol(
    usuario_id: UUID,
    rol_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UsuarioRolRepository(session=db, tenant_id=current_user.tenant_id)
    assignment = await repo.find_by_usuario_and_rol(usuario_id, rol_id)
    if assignment is None:
        raise NotFoundException(resource="UsuarioRol")
    await repo.hard_delete(assignment.id)
    await db.commit()

    audit_logger = AuditLogger(
        repository=AuditLogRepository(session=db, tenant_id=current_user.tenant_id)
    )
    await audit_logger.log(
        current_user=current_user,
        accion="usuario_rol.remove",
        detalle={"usuario_id": str(usuario_id), "rol_id": str(rol_id)},
        filas_afectadas=1,
        request=request,
    )

    return {"detail": "Rol removed from user"}


# ── Service factory ──────────────────────────────────────────────────────


def _usuario_service(db: AsyncSession, tenant_id: UUID) -> UsuarioService:
    return UsuarioService(
        usuario_repo=UsuarioRepository(session=db, tenant_id=tenant_id),
        audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
    )


# ── Response mapper ───────────────────────────────────────────────────────


def _usuario_to_response(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        tenant_id=usuario.tenant_id,
        user_id=usuario.user_id,
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        banco=usuario.banco,
        regional=usuario.regional,
        legajo=usuario.legajo,
        legajo_profesional=usuario.legajo_profesional,
        facturador=usuario.facturador,
        estado=usuario.estado,
        deleted_at=usuario.deleted_at is not None,
    )
