"""Test helper utilities for the permission system."""

import datetime
import uuid

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.usuario import Usuario
from app.models.user import User
from app.repositories.base import BaseRepository


async def seed_permissions_for_tenant(
    db_session: AsyncSession,
    tenant_id: uuid.UUID,
):
    """Seed default roles, permissions, and their assignments for a tenant.

    Uses codigo-based lookups so each tenant gets independent UUIDs.
    """

    # ── Role definitions ───────────────────────────────────────────────
    roles = [
        ("ALUMNO", "Alumno", "Estudiante cursando una carrera"),
        ("TUTOR", "Tutor", "Tutor de alumnos"),
        ("PROFESOR", "Profesor", "Docente a cargo de comisiones"),
        ("COORDINADOR", "Coordinador", "Coordinador académico"),
        ("NEXO", "Nexo", "Enlace institucional (pendiente PA-25)"),
        ("ADMIN", "Admin", "Administrador del tenant"),
        ("FINANZAS", "Finanzas", "Gestión financiera y liquidaciones"),
    ]

    # ── Permission definitions ─────────────────────────────────────────
    permisos = [
        ("estado-academico:ver", "Ver estado académico propio", "estado-academico"),
        ("evaluacion:reservar", "Reservar instancia de evaluación", "evaluacion"),
        ("avisos:confirmar", "Confirmar avisos (ack)", "avisos"),
        ("calificaciones:importar", "Importar calificaciones", "calificaciones"),
        ("atrasados:ver", "Ver alumnos atrasados", "atrasados"),
        ("entregas:sin-corregir", "Detectar entregas sin corregir", "entregas"),
        ("comunicacion:enviar", "Enviar comunicaciones a alumnos", "comunicacion"),
        ("comunicacion:aprobar", "Aprobar comunicaciones masivas", "comunicacion"),
        ("encuentros:gestionar", "Gestionar encuentros", "encuentros"),
        ("guardias:registrar", "Registrar guardias", "guardias"),
        ("tareas:gestionar", "Gestionar tareas internas", "tareas"),
        ("avisos:publicar", "Publicar avisos", "avisos"),
        ("equipos:gestionar", "Gestionar equipos docentes", "equipos"),
        ("equipos:asignar", "Asignar roles y contexto a usuarios", "equipos"),
        ("estructura:gestionar", "Gestionar estructura académica", "estructura"),
        ("usuarios:gestionar", "Gestionar usuarios del tenant", "usuarios"),
        ("auditoria:ver", "Ver auditoría", "auditoria"),
        ("grilla:operar", "Operar grilla salarial", "grilla"),
        ("liquidaciones:ver", "Ver liquidaciones del período", "liquidaciones"),
        ("liquidaciones:calcular", "Calcular liquidaciones del período", "liquidaciones"),
        ("liquidaciones:configurar-salarios", "Configurar grilla salarial", "liquidaciones"),
        ("liquidaciones:cerrar", "Calcular/cerrar liquidaciones", "liquidaciones"),
        ("facturas:gestionar", "Gestionar facturas", "facturas"),
        ("configurar:tenant", "Configurar el tenant", "configurar"),
        ("padron:importar", "Importar padrón de alumnos", "padron"),
        ("padron:vaciar", "Vaciar datos de dictado", "padron"),
        ("padron:ver", "Ver padrón de alumnos", "padron"),
        ("coloquios:gestionar", "Gestionar convocatorias de coloquio", "coloquios"),
        ("coloquios:reservar", "Reservar turno de coloquio", "coloquios"),
        ("coloquios:ver", "Ver coloquios y resultados", "coloquios"),
        ("inbox:acceder", "Acceder a la bandeja de mensajes interna", "inbox"),
        # C-25 profesor dashboard
        ("actividades:gestionar", "Gestionar actividades del dictado", "actividades"),
        ("calificaciones:editar", "Editar calificación individual", "calificaciones"),
        ("padron:gestionar-alumno", "Alta/baja individual de alumno", "padron"),
    ]

    # ── Role-permission matrix ─────────────────────────────────────────
    # Each entry: (role_codigo, permiso_codigo, es_propio)
    matrix = [
        # ALUMNO
        ("ALUMNO", "estado-academico:ver", False),
        ("ALUMNO", "evaluacion:reservar", False),
        ("ALUMNO", "avisos:confirmar", False),
        ("ALUMNO", "inbox:acceder", False),
        # TUTOR
        ("TUTOR", "avisos:confirmar", False),
        ("TUTOR", "atrasados:ver", False),
        ("TUTOR", "entregas:sin-corregir", False),
        ("TUTOR", "encuentros:gestionar", False),
        ("TUTOR", "guardias:registrar", True),
        ("TUTOR", "inbox:acceder", False),
        # PROFESOR
        ("PROFESOR", "avisos:confirmar", False),
        ("PROFESOR", "avisos:publicar", True),  # C-26: propio (solo sus dictados)
        ("PROFESOR", "calificaciones:importar", True),
        ("PROFESOR", "atrasados:ver", True),
        ("PROFESOR", "entregas:sin-corregir", True),
        ("PROFESOR", "comunicacion:enviar", True),
        ("PROFESOR", "encuentros:gestionar", True),
        ("PROFESOR", "guardias:registrar", True),
        ("PROFESOR", "tareas:gestionar", True),
        ("PROFESOR", "inbox:acceder", False),
        # COORDINADOR
        ("COORDINADOR", "avisos:confirmar", False),
        ("COORDINADOR", "calificaciones:importar", False),
        ("COORDINADOR", "atrasados:ver", False),
        ("COORDINADOR", "entregas:sin-corregir", False),
        ("COORDINADOR", "comunicacion:enviar", False),
        ("COORDINADOR", "comunicacion:aprobar", False),
        ("COORDINADOR", "encuentros:gestionar", False),
        ("COORDINADOR", "guardias:registrar", False),
        ("COORDINADOR", "tareas:gestionar", False),
        ("COORDINADOR", "avisos:publicar", False),
        ("COORDINADOR", "equipos:gestionar", False),
        ("COORDINADOR", "equipos:asignar", False),
        ("COORDINADOR", "auditoria:ver", True),
        ("COORDINADOR", "inbox:acceder", False),
        # NEXO
        ("NEXO", "inbox:acceder", False),
        # ADMIN
        ("ADMIN", "avisos:confirmar", False),
        ("ADMIN", "calificaciones:importar", False),
        ("ADMIN", "atrasados:ver", False),
        ("ADMIN", "entregas:sin-corregir", False),
        ("ADMIN", "comunicacion:enviar", False),
        ("ADMIN", "comunicacion:aprobar", False),
        ("ADMIN", "encuentros:gestionar", False),
        ("ADMIN", "guardias:registrar", False),
        ("ADMIN", "tareas:gestionar", False),
        ("ADMIN", "avisos:publicar", False),
        ("ADMIN", "equipos:gestionar", False),
        ("ADMIN", "equipos:asignar", False),
        ("ADMIN", "estructura:gestionar", False),
        ("ADMIN", "usuarios:gestionar", False),
        ("ADMIN", "auditoria:ver", False),
        ("ADMIN", "configurar:tenant", False),
        ("ADMIN", "padron:importar", False),
        ("ADMIN", "padron:vaciar", False),
        ("ADMIN", "padron:ver", False),
        ("ADMIN", "inbox:acceder", False),
        # COORDINADOR — coloquios
        ("COORDINADOR", "coloquios:gestionar", False),
        ("COORDINADOR", "coloquios:ver", False),
        # ALUMNO — coloquios
        ("ALUMNO", "coloquios:reservar", False),
        # PROFESOR — coloquios (propio)
        ("PROFESOR", "coloquios:ver", True),
        # ADMIN — coloquios
        ("ADMIN", "coloquios:gestionar", False),
        ("ADMIN", "coloquios:ver", False),
        # PROFESOR — C-25 nuevos permisos (es_propio=True: sólo sus propios dictados)
        ("PROFESOR", "actividades:gestionar", True),
        ("PROFESOR", "calificaciones:editar", True),
        ("PROFESOR", "padron:gestionar-alumno", True),
        # COORDINADOR — C-25
        ("COORDINADOR", "actividades:gestionar", False),
        ("COORDINADOR", "calificaciones:editar", False),
        ("COORDINADOR", "padron:gestionar-alumno", False),
        # ADMIN — C-25
        ("ADMIN", "actividades:gestionar", False),
        ("ADMIN", "calificaciones:editar", False),
        ("ADMIN", "padron:gestionar-alumno", False),
        # FINANZAS
        ("FINANZAS", "avisos:confirmar", False),
        ("FINANZAS", "auditoria:ver", False),
        ("FINANZAS", "grilla:operar", False),
        ("FINANZAS", "liquidaciones:ver", False),
        ("FINANZAS", "liquidaciones:calcular", False),
        ("FINANZAS", "liquidaciones:configurar-salarios", False),
        ("FINANZAS", "liquidaciones:cerrar", False),
        ("FINANZAS", "facturas:gestionar", False),
        ("FINANZAS", "inbox:acceder", False),
    ]

    # 1. Insert roles (with generated UUIDs, skip if already exist per tenant)
    for codigo, nombre, descripcion in roles:
        await db_session.execute(
            sql_text("""
                INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :descripcion, now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
            """),
            {
                "tenant_id": tenant_id,
                "codigo": codigo,
                "nombre": nombre,
                "descripcion": descripcion,
            },
        )

    # 2. Insert permissions (with generated UUIDs)
    for codigo, nombre, modulo in permisos:
        await db_session.execute(
            sql_text("""
                INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :descripcion, :modulo, now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
            """),
            {
                "tenant_id": tenant_id,
                "codigo": codigo,
                "nombre": nombre,
                "descripcion": None,
                "modulo": modulo,
            },
        )

    await db_session.flush()

    # 3. Look up IDs and insert rol_permiso
    for role_codigo, permiso_codigo, es_propio in matrix:
        await db_session.execute(
            sql_text("""
                INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at)
                SELECT gen_random_uuid(), :tenant_id, r.id, p.id, :es_propio, now(), now()
                FROM rol r, permiso p
                WHERE r.tenant_id = :tenant_id AND r.codigo = :role_codigo AND r.deleted_at IS NULL
                  AND p.tenant_id = :tenant_id AND p.codigo = :permiso_codigo AND p.deleted_at IS NULL
                ON CONFLICT (tenant_id, rol_id, permiso_id) DO NOTHING
            """),
            {
                "tenant_id": tenant_id,
                "role_codigo": role_codigo,
                "permiso_codigo": permiso_codigo,
                "es_propio": es_propio,
            },
        )

    await db_session.flush()


def cleanup_permission_cache():
    """Clear the per-request permission cache between tests."""
    from app.services.permission_service import PermissionResolver
    PermissionResolver.clear_cache()


async def seed_asignaciones_for_user(
    db_session: AsyncSession,
    user: User,
    roles: list[str] | None,
) -> Usuario | None:
    """Mirror migration 007's backfill for a single test user (C-07 Grupo 6).

    The test schema is built via `Base.metadata.create_all`, so migration
    007's backfill never runs against the test DB. Without this helper,
    `AsignacionRepository.find_roles_vigentes` would return an empty set for
    every test user, breaking the auth/RBAC safety net once
    `TokenService.create_access_token` derives the `roles` claim from
    `Asignacion` instead of `users.roles`.

    For each role in `roles`, ensures:
    - a `Usuario` row exists for `(tenant_id, user.id)` (created if absent,
      same shell defaults as the migration: empty `nombre`/`apellidos`,
      `facturador=False`, `estado="Activo"`)
    - an `Asignacion` row with that `rol`, NULL academic context (tenant-global),
      `desde=today()`, `hasta=None` — matching the migration's backfill shape.

    Returns the `Usuario` row, or `None` if `roles` is empty/None (no
    Usuario/Asignacion rows are created for a roleless user, matching the
    migration's `if not roles: continue`).
    """
    if not roles:
        return None

    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=user.tenant_id)
    existing = await usuario_repo.find_by(user_id=user.id)
    usuario = existing[0] if existing else None
    if usuario is None:
        usuario = await usuario_repo.create(
            {
                "user_id": user.id,
                "nombre": "",
                "apellidos": "",
                "facturador": False,
                "estado": "Activo",
            }
        )

    asignacion_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=user.tenant_id)
    hoy = datetime.date.today()
    for rol in roles:
        existing_asignacion = await asignacion_repo.find_by(usuario_id=usuario.id, rol=rol)
        already_global = any(
            a.dictado_id is None
            and a.materia_id is None
            and a.carrera_id is None
            and a.cohorte_id is None
            for a in existing_asignacion
        )
        if already_global:
            continue
        await asignacion_repo.create(
            {
                "usuario_id": usuario.id,
                "rol": rol,
                "desde": hoy,
                "hasta": None,
            }
        )

    return usuario
