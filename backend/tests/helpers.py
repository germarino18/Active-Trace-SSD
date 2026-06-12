"""Test helper utilities for the permission system."""

import uuid

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession


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
        ("estructura:gestionar", "Gestionar estructura académica", "estructura"),
        ("usuarios:gestionar", "Gestionar usuarios del tenant", "usuarios"),
        ("auditoria:ver", "Ver auditoría", "auditoria"),
        ("grilla:operar", "Operar grilla salarial", "grilla"),
        ("liquidaciones:cerrar", "Calcular/cerrar liquidaciones", "liquidaciones"),
        ("facturas:gestionar", "Gestionar facturas", "facturas"),
        ("configurar:tenant", "Configurar el tenant", "configurar"),
    ]

    # ── Role-permission matrix ─────────────────────────────────────────
    # Each entry: (role_codigo, permiso_codigo, es_propio)
    matrix = [
        # ALUMNO
        ("ALUMNO", "estado-academico:ver", False),
        ("ALUMNO", "evaluacion:reservar", False),
        ("ALUMNO", "avisos:confirmar", False),
        # TUTOR
        ("TUTOR", "avisos:confirmar", False),
        ("TUTOR", "atrasados:ver", False),
        ("TUTOR", "entregas:sin-corregir", False),
        ("TUTOR", "encuentros:gestionar", False),
        ("TUTOR", "guardias:registrar", True),
        # PROFESOR
        ("PROFESOR", "avisos:confirmar", False),
        ("PROFESOR", "calificaciones:importar", True),
        ("PROFESOR", "atrasados:ver", True),
        ("PROFESOR", "entregas:sin-corregir", True),
        ("PROFESOR", "comunicacion:enviar", True),
        ("PROFESOR", "encuentros:gestionar", True),
        ("PROFESOR", "guardias:registrar", True),
        ("PROFESOR", "tareas:gestionar", True),
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
        ("COORDINADOR", "auditoria:ver", True),
        # NEXO — zero permissions
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
        ("ADMIN", "estructura:gestionar", False),
        ("ADMIN", "usuarios:gestionar", False),
        ("ADMIN", "auditoria:ver", False),
        ("ADMIN", "configurar:tenant", False),
        # FINANZAS
        ("FINANZAS", "avisos:confirmar", False),
        ("FINANZAS", "auditoria:ver", False),
        ("FINANZAS", "grilla:operar", False),
        ("FINANZAS", "liquidaciones:cerrar", False),
        ("FINANZAS", "facturas:gestionar", False),
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
