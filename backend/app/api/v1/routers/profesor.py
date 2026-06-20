"""Router del panel docente (C-25 §4, §6, §7, §8, §9, §10).

Endpoints:
  GET  /api/v1/profesor/dashboard                                           — §4
  GET  /api/v1/profesor/dictados/{dictado_id}/metricas                      — §4
  GET  /api/v1/profesor/dictados/{dictado_id}/padron                        — §6 (lista el padrón)
  GET  /api/v1/profesor/dictados/{dictado_id}/alumnos-disponibles           — §6 (picker de alta)
  POST /api/v1/profesor/dictados/{dictado_id}/padron/alumnos                — §6 (alta alumno single/bulk)
  POST /api/v1/profesor/dictados/{dictado_id}/padron/alumnos/bulk-baja      — §6 (baja masiva)
  DELETE /api/v1/profesor/dictados/{dictado_id}/padron/alumnos/{ep_id}     — §6
  GET  /api/v1/profesor/dictados/{dictado_id}/padron/export-csv             — §6
  GET  /api/v1/profesor/atrasados                                           — §7b (cross-materia)
  GET  /api/v1/profesor/dictados/{dictado_id}/atrasados                     — §7
  POST /api/v1/profesor/dictados/{dictado_id}/comunicado-atrasado-null      — §8
  POST /api/v1/profesor/comunicado-atrasados-flexible                       — §10 (actividad opcional)
  GET  /api/v1/profesor/dictados/{dictado_id}/equipo                        — §9
"""

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.core.dependencies import get_db
from app.core.permissions import Perm
from app.schemas.auth import CurrentUser
from app.services.profesor_service import ProfesorService

router = APIRouter(prefix="/api/v1/profesor", tags=["profesor"])


# ── §4 Dashboard y métricas ────────────────────────────────────────────────────


@router.get("/dashboard")
async def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard del profesor: materias, alumnos, encuentros, atrasados."""
    service = ProfesorService.create(db, current_user.tenant_id)
    return await service.get_dashboard(current_user)


@router.get(
    "/dictados/{dictado_id}/metricas",
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_metricas_dictado(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Métricas de un dictado (total_alumnos, aprobados, atrasados, promedio)."""
    service = ProfesorService.create(db, current_user.tenant_id)
    return await service.get_metricas_dictado(dictado_id)


# ── §6 Gestión padrón ─────────────────────────────────────────────────────────


@router.get(
    "/dictados/{dictado_id}/padron",
    dependencies=[Depends(require_permission(Perm.PADRON_GESTIONAR_ALUMNO))],
)
async def listar_padron(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista el padrón activo del dictado.

    Gated with `padron:gestionar-alumno` (permiso que el PROFESOR tiene).
    No usar `padron:ver` que el PROFESOR NO tiene.
    """
    service = ProfesorService.create(db, current_user.tenant_id)
    entradas = await service.obtener_padron_activo(dictado_id)
    return [
        {
            "id": ep.id,
            "nombre": ep.nombre,
            "apellidos": ep.apellidos,
            "email": ep.email,
            "comision": ep.comision,
        }
        for ep in entradas
    ]


@router.get(
    "/dictados/{dictado_id}/alumnos-disponibles",
    dependencies=[Depends(require_permission(Perm.PADRON_GESTIONAR_ALUMNO))],
)
async def alumnos_disponibles(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Alumnos del tenant (rol ALUMNO) que NO están en el padrón activo del dictado.

    Devuelve [{usuario_id, nombre, apellidos, email}] para el picker de alta.
    """
    service = ProfesorService.create(db, current_user.tenant_id)
    return await service.get_alumnos_disponibles(dictado_id)


class AltaAlumnoRequest(BaseModel):
    """Alta individual o masiva de alumnos en el padrón.

    Flujo bulk: proporcionar `usuario_ids` (lista de UUIDs).
    Flujo single: proporcionar `usuario_id` de un alumno existente del tenant.
    Flujo de fallback (legacy): proporcionar nombre + apellidos para crear entrada libre.
    """
    model_config = ConfigDict(extra="forbid")
    # Bulk path — list of usuario_ids
    usuario_ids: list[UUID] | None = None
    # Primary single path — pick existing alumno
    usuario_id: UUID | None = None
    # Fallback — free-text entry
    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    apellidos: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = None
    comision: str | None = None


@router.post(
    "/dictados/{dictado_id}/padron/alumnos",
    status_code=201,
    dependencies=[Depends(require_permission(Perm.PADRON_GESTIONAR_ALUMNO))],
)
async def alta_alumno(
    dictado_id: UUID,
    body: AltaAlumnoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Alta de alumno/s en el padrón activo del dictado.

    - Si `usuario_ids` presente → bulk add (lista de UUIDs).
    - Si `usuario_id` presente → single add.
    - Si nombre+apellidos → free-text entry (fallback).
    """
    from fastapi import HTTPException

    service = ProfesorService.create(db, current_user.tenant_id)

    # Bulk path
    if body.usuario_ids is not None:
        entradas = await service.alta_alumnos_dictado_bulk(
            dictado_id=dictado_id,
            usuario_ids=body.usuario_ids,
            current_user=current_user,
        )
        await db.commit()
        return [
            {
                "id": e.id,
                "nombre": e.nombre,
                "apellidos": e.apellidos,
                "email": e.email,
                "comision": e.comision,
            }
            for e in entradas
        ]

    # Single path
    if body.usuario_id is None and (not body.nombre or not body.apellidos):
        raise HTTPException(
            status_code=422,
            detail="Debe proveer usuario_ids OR usuario_id OR (nombre + apellidos)",
        )

    entrada = await service.alta_alumno_dictado(
        dictado_id=dictado_id,
        alumno_data=body.model_dump(),
        current_user=current_user,
    )
    await db.commit()
    await db.refresh(entrada)
    return {
        "id": entrada.id,
        "nombre": entrada.nombre,
        "apellidos": entrada.apellidos,
        "email": entrada.email,
        "comision": entrada.comision,
    }


class BulkBajaRequest(BaseModel):
    """Baja masiva de alumnos del padrón."""
    model_config = ConfigDict(extra="forbid")
    entrada_padron_ids: list[UUID]


@router.post(
    "/dictados/{dictado_id}/padron/alumnos/bulk-baja",
    status_code=204,
    dependencies=[Depends(require_permission(Perm.PADRON_GESTIONAR_ALUMNO))],
)
async def bulk_baja_alumnos(
    dictado_id: UUID,
    body: BulkBajaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Baja masiva (soft-delete) de alumnos del padrón activo.

    Calificaciones existentes PERSISTEN después de la baja.
    Gate: padron:gestionar-alumno.
    """
    service = ProfesorService.create(db, current_user.tenant_id)
    await service.baja_alumnos_bulk(
        entrada_padron_ids=body.entrada_padron_ids,
        dictado_id=dictado_id,
        current_user=current_user,
    )
    await db.commit()


@router.delete(
    "/dictados/{dictado_id}/padron/alumnos/{entrada_padron_id}",
    status_code=204,
    dependencies=[Depends(require_permission(Perm.PADRON_GESTIONAR_ALUMNO))],
)
async def baja_alumno(
    dictado_id: UUID,
    entrada_padron_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete de un alumno del padrón (baja individual)."""
    service = ProfesorService.create(db, current_user.tenant_id)
    await service.baja_alumno_dictado(
        entrada_padron_id=entrada_padron_id,
        dictado_id=dictado_id,
        current_user=current_user,
    )
    await db.commit()


@router.get(
    "/dictados/{dictado_id}/padron/export-csv",
)
async def exportar_padron_csv(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exporta el padrón activo del dictado como CSV (read-only)."""
    from app.repositories.entrada_padron_repository import EntradaPadronRepository
    from app.repositories.version_padron_repository import VersionPadronRepository

    tenant_id = current_user.tenant_id
    vp_repo = VersionPadronRepository(session=db, tenant_id=tenant_id)
    ep_repo = EntradaPadronRepository(session=db, tenant_id=tenant_id)

    active_vp = await vp_repo.find_active_by_dictado(dictado_id)
    entradas = []
    if active_vp:
        entradas = await ep_repo.find_by_version(active_vp.id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["alumno_id", "nombre", "apellido", "nota", "aprobado", "actividad"])
    for ep in entradas:
        writer.writerow([str(ep.id), ep.nombre, ep.apellidos, "", "", ""])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=padron_{dictado_id}.csv"},
    )


# ── §7b Atrasados cross-materia (global panel) ────────────────────────────────


@router.get(
    "/atrasados",
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_atrasados_cross_materia(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Alumnos con ≥1 actividad sin entrega en todos los dictados del profesor.

    Retorna: entrada_padron_id, nombre, apellido, dictado_id, materia_nombre,
    actividades_sin_entrega [].
    Gate: atrasados:ver (PROFESOR tiene es_propio=True).
    """
    service = ProfesorService.create(db, current_user.tenant_id)
    return await service.get_atrasados_cross_materia(current_user)


# ── §7 Atrasados clasificados ─────────────────────────────────────────────────


@router.get(
    "/dictados/{dictado_id}/atrasados",
    dependencies=[Depends(require_permission(Perm.ATRASADOS_VER))],
)
async def get_atrasados_clasificados(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Alumnos clasificados por estado (aprobado/atrasado/atrasado_null)."""
    service = ProfesorService.create(db, current_user.tenant_id)
    return await service.get_alumnos_clasificados(dictado_id)


# ── §8 Comunicado a atrasado_null ─────────────────────────────────────────────


class ComunicadoAtrasadoNullRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actividad_id: UUID
    asunto_template: str = Field(..., min_length=1)
    cuerpo_template: str = Field(..., min_length=1)


@router.post(
    "/dictados/{dictado_id}/comunicado-atrasado-null",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_ENVIAR))],
)
async def comunicado_atrasado_null(
    dictado_id: UUID,
    body: ComunicadoAtrasadoNullRequest,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Envía comunicado a alumnos con atrasado-null para una actividad específica."""
    service = ProfesorService.create(db, current_user.tenant_id)
    result = await service.prepare_comunicado_atrasado_null(
        dictado_id=dictado_id,
        actividad_id=body.actividad_id,
        asunto_template=body.asunto_template,
        cuerpo_template=body.cuerpo_template,
        current_user=current_user,
        request=request,
    )
    await db.commit()
    return result


# ── §8b Comunicado a desaprobados ────────────────────────────────────────────


class ComunicadoAtrasadosRequest(BaseModel):
    """Comunicado a alumnos atrasados por subtipo ('desaprobado' | 'atrasado_null')."""
    model_config = ConfigDict(extra="forbid")
    actividad_id: UUID
    subtipo: str = Field(..., pattern="^(desaprobado|atrasado_null)$")
    asunto_template: str = Field(..., min_length=1)
    cuerpo_template: str = Field(..., min_length=1)


@router.post(
    "/dictados/{dictado_id}/comunicado-atrasados",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_ENVIAR))],
)
async def comunicado_atrasados(
    dictado_id: UUID,
    body: ComunicadoAtrasadosRequest,
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Envía comunicado a alumnos con `subtipo` indicado para una actividad.

    `subtipo` puede ser 'desaprobado' o 'atrasado_null'.
    Reutiliza el pipeline de comunicaciones (enqueue_masivo → aprobación).
    """
    service = ProfesorService.create(db, current_user.tenant_id)
    result = await service.prepare_comunicado_atrasados(
        dictado_id=dictado_id,
        actividad_id=body.actividad_id,
        subtipo=body.subtipo,
        asunto_template=body.asunto_template,
        cuerpo_template=body.cuerpo_template,
        current_user=current_user,
        request=request,
    )
    await db.commit()
    return result


# ── §10 Comunicado flexible (actividad opcional, destinatarios explícitos) ─────


class ComunicadoDestinatarioItem(BaseModel):
    """Un destinatario del comunicado flexible: selector de entrada + dictado."""
    model_config = ConfigDict(extra="forbid")
    entrada_padron_id: UUID
    dictado_id: UUID


class ComunicadoFlexibleRequest(BaseModel):
    """Request del comunicado flexible (actividad_id opcional, destinatarios explícitos).

    Governance CRÍTICO: este endpoint siempre pasa por `enqueue_masivo` — NUNCA
    saltea el gate de aprobación del tenant.
    """
    model_config = ConfigDict(extra="forbid")
    actividad_id: UUID | None = None
    asunto_template: str = Field(..., min_length=1)
    cuerpo_template: str = Field(..., min_length=1)
    destinatarios: list[ComunicadoDestinatarioItem] = Field(..., min_length=1)


@router.post(
    "/comunicado-atrasados-flexible",
    dependencies=[Depends(require_permission(Perm.COMUNICACION_ENVIAR))],
)
async def comunicado_atrasados_flexible(
    body: ComunicadoFlexibleRequest,
    current_user=Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Envía comunicado a destinatarios explícitos con actividad opcional.

    Modo individual: lista de un elemento.
    Modo general: lista con todos los desaprobados/atrasados de la vista.

    Siempre reutiliza `enqueue_masivo` → respeta `tenant.aprobacion_comunicaciones`.
    Identity: JWT session (current_user). Tenant-scoped. Audited.
    """
    service = ProfesorService.create(db, current_user.tenant_id)
    result = await service.prepare_comunicado_flexible(
        actividad_id=body.actividad_id,
        asunto_template=body.asunto_template,
        cuerpo_template=body.cuerpo_template,
        destinatarios=[
            {"entrada_padron_id": d.entrada_padron_id, "dictado_id": d.dictado_id}
            for d in body.destinatarios
        ],
        current_user=current_user,
        request=request,
    )
    await db.commit()
    return result


# ── §9 Equipo docente ─────────────────────────────────────────────────────────


@router.get("/dictados/{dictado_id}/equipo")
async def get_equipo_dictado(
    dictado_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Equipo docente del dictado (PROFESOR/TUTOR), excluyendo al usuario actual."""
    service = ProfesorService.create(db, current_user.tenant_id)
    return await service.get_equipo_dictado(dictado_id, current_user)


# ── §9 Filtros "mios" en routers existentes ───────────────────────────────────
# These are helper endpoints on the profesor router that wrap existing services


@router.get("/avisos/mios")
async def mis_avisos(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Avisos del tenant para el usuario actual (todos los activos y no eliminados)."""
    from sqlalchemy import select

    from app.services.avisos_service import AvisoService

    service = AvisoService.create(db, current_user.tenant_id)
    return await service.get_visible(current_user)


@router.get("/coloquios/mios")
async def mis_coloquios(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Coloquios (evaluaciones) creados por el usuario actual (created_by_id)."""
    from sqlalchemy import select

    from app.models.evaluacion import Evaluacion

    stmt = select(Evaluacion).where(
        Evaluacion.tenant_id == current_user.tenant_id,
        Evaluacion.created_by_id == current_user.user_id,
    )
    r = await db.execute(stmt)
    coloquios = list(r.unique().scalars().all())
    return [
        {
            "id": c.id,
            "instancia": c.instancia,
            "estado": c.estado,
            "tipo": c.tipo,
            "dictado_id": c.dictado_id,
        }
        for c in coloquios
    ]
