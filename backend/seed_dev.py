"""Seed desarrollo: usuarios + asignaciones + roles/permisos."""
import asyncio
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.auth.password_service import PasswordService

# Debe mantenerse en sync con alembic/versions/003_create_rol_permiso_tables.py
_ROLES = [
    ("ALUMNO", "Alumno", "Estudiante cursando una carrera"),
    ("TUTOR", "Tutor", "Tutor de alumnos"),
    ("PROFESOR", "Profesor", "Docente a cargo de comisiones"),
    ("COORDINADOR", "Coordinador", "Coordinador académico"),
    ("NEXO", "Nexo", "Enlace institucional"),
    ("ADMIN", "Admin", "Administrador del tenant"),
    ("FINANZAS", "Finanzas", "Gestión financiera y liquidaciones"),
]

_PERMISOS = [
    ("estado-academico:ver", "estado-academico"),
    ("evaluacion:reservar", "evaluacion"),
    ("avisos:confirmar", "avisos"),
    ("calificaciones:importar", "calificaciones"),
    ("atrasados:ver", "atrasados"),
    ("entregas:sin-corregir", "entregas"),
    ("comunicacion:enviar", "comunicacion"),
    ("comunicacion:aprobar", "comunicacion"),
    ("encuentros:gestionar", "encuentros"),
    ("guardias:registrar", "guardias"),
    ("tareas:gestionar", "tareas"),
    ("avisos:publicar", "avisos"),
    ("equipos:gestionar", "equipos"),
    ("estructura:gestionar", "estructura"),
    ("usuarios:gestionar", "usuarios"),
    ("auditoria:ver", "auditoria"),
    ("grilla:operar", "grilla"),
    ("liquidaciones:cerrar", "liquidaciones"),
    ("facturas:gestionar", "facturas"),
    ("configurar:tenant", "configurar"),
]

_MATRIX = [
    ("ALUMNO", "estado-academico:ver", False),
    ("ALUMNO", "evaluacion:reservar", False),
    ("ALUMNO", "avisos:confirmar", False),
    ("TUTOR", "avisos:confirmar", False),
    ("TUTOR", "atrasados:ver", False),
    ("TUTOR", "entregas:sin-corregir", False),
    ("TUTOR", "encuentros:gestionar", False),
    ("TUTOR", "guardias:registrar", True),
    ("PROFESOR", "avisos:confirmar", False),
    ("PROFESOR", "calificaciones:importar", True),
    ("PROFESOR", "atrasados:ver", True),
    ("PROFESOR", "entregas:sin-corregir", True),
    ("PROFESOR", "comunicacion:enviar", True),
    ("PROFESOR", "encuentros:gestionar", True),
    ("PROFESOR", "guardias:registrar", True),
    ("PROFESOR", "tareas:gestionar", True),
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
    ("FINANZAS", "avisos:confirmar", False),
    ("FINANZAS", "auditoria:ver", False),
    ("FINANZAS", "grilla:operar", False),
    ("FINANZAS", "liquidaciones:cerrar", False),
    ("FINANZAS", "facturas:gestionar", False),
]


async def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Check if already seeded
        r = await session.execute(text("SELECT COUNT(*) FROM tenant"))
        if (r.scalar() or 0) > 0:
            print("Ya hay datos — omitiendo seed.")
            await engine.dispose()
            return

        tenant_id = uuid.uuid4()

        # 1. Create tenant
        await session.execute(
            text(
                "INSERT INTO tenant (id, tenant_id, name, slug, is_active, created_at, updated_at) "
                "VALUES (:tid, :tid, :name, :slug, true, NOW(), NOW())"
            ),
            {"tid": tenant_id, "name": "Universidad Demo", "slug": "demo"},
        )

        users_data = [
            {
                "email": "admin@demo.com",
                "pw": "Admin123!",
                "name": "Admin",
                "apellidos": "Demo",
                "roles": ["ADMIN", "COORDINADOR"],
            },
            {
                "email": "coordinador@demo.com",
                "pw": "Coord123!",
                "name": "Coordinador",
                "apellidos": "Demo",
                "roles": ["COORDINADOR"],
            },
            {
                "email": "profesor@demo.com",
                "pw": "Demo123!",
                "name": "Profesor",
                "apellidos": "Demo",
                "roles": ["PROFESOR"],
            },
            {
                "email": "finanzas@demo.com",
                "pw": "Fin123!",
                "name": "Finanzas",
                "apellidos": "Demo",
                "roles": ["FINANZAS"],
            },
            {
                "email": "nexo@demo.com",
                "pw": "Nexo123!",
                "name": "Nexo",
                "apellidos": "Demo",
                "roles": ["NEXO"],
            },
        ]

        for u in users_data:
            user_id = uuid.uuid4()
            usuario_id = uuid.uuid4()

            # users table
            await session.execute(
                text(
                    "INSERT INTO users (id, tenant_id, email, password_hash, display_name, is_active, roles, created_at, updated_at) "
                    "VALUES (:uid, :tid, :email, :pw, :name, true, :roles, NOW(), NOW())"
                ),
                {
                    "uid": user_id,
                    "tid": tenant_id,
                    "email": u["email"],
                    "pw": PasswordService.hash_password(u["pw"]),
                    "name": f"{u['name']} {u['apellidos']}",
                    "roles": u["roles"],
                },
            )

            # usuario table (business profile)
            await session.execute(
                text(
                    "INSERT INTO usuario (id, tenant_id, user_id, nombre, apellidos, legajo, facturador, estado, created_at, updated_at) "
                    "VALUES (:usid, :tid, :uid, :nom, :ape, :leg, false, 'Activo', NOW(), NOW())"
                ),
                {
                    "usid": usuario_id,
                    "tid": tenant_id,
                    "uid": user_id,
                    "nom": u["name"],
                    "ape": u["apellidos"],
                    "leg": u["email"].split("@")[0],
                },
            )

            # asignacion for each role
            for role in u["roles"]:
                asi_id = uuid.uuid4()
                await session.execute(
                    text(
                        "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, desde, hasta, created_at, updated_at) "
                        "VALUES (:aid, :tid, :usid, :rol, NOW(), '2099-12-31', NOW(), NOW())"
                    ),
                    {
                        "aid": asi_id,
                        "tid": tenant_id,
                        "usid": usuario_id,
                        "rol": role,
                    },
                )

        # 2. Seed rol / permiso / rol_permiso for the new tenant
        tid_str = str(tenant_id)
        for codigo, nombre, descripcion in _ROLES:
            await session.execute(
                text(
                    "INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :tid, :codigo, :nombre, :desc, NOW(), NOW()) "
                    "ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING"
                ),
                {"tid": tid_str, "codigo": codigo, "nombre": nombre, "desc": descripcion},
            )
        for codigo, modulo in _PERMISOS:
            await session.execute(
                text(
                    "INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :tid, :codigo, :codigo, NULL, :modulo, NOW(), NOW()) "
                    "ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING"
                ),
                {"tid": tid_str, "codigo": codigo, "modulo": modulo},
            )
        for role_codigo, permiso_codigo, es_propio in _MATRIX:
            await session.execute(
                text(
                    "INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at) "
                    "SELECT gen_random_uuid(), :tid, r.id, p.id, :es_propio, NOW(), NOW() "
                    "FROM rol r, permiso p "
                    "WHERE r.tenant_id = :tid AND r.codigo = :rc AND r.deleted_at IS NULL "
                    "  AND p.tenant_id = :tid AND p.codigo = :pc AND p.deleted_at IS NULL "
                    "ON CONFLICT (tenant_id, rol_id, permiso_id) DO NOTHING"
                ),
                {"tid": tid_str, "rc": role_codigo, "pc": permiso_codigo, "es_propio": es_propio},
            )

        await session.commit()
        print("\n✅ Seed completado exitosamente!\n")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║              CREDENCIALES DE DESARROLLO                 ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║  ROL          │ EMAIL                   │ PASSWORD     ║")
        print("║───────────────┼────────────────────────┼───────────────║")
        print("║  ADMIN        │ admin@demo.com          │ Admin123!    ║")
        print("║  COORDINADOR  │ coordinador@demo.com    │ Coord123!    ║")
        print("║  PROFESOR     │ profesor@demo.com       │ Demo123!     ║")
        print("║  FINANZAS     │ finanzas@demo.com       │ Fin123!      ║")
        print("║  NEXO         │ nexo@demo.com           │ Nexo123!     ║")
        print("╚══════════════════════════════════════════════════════════╝\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
