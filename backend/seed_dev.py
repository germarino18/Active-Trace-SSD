"""Seed desarrollo completo: tenant + usuarios + estructura académica + roles/permisos."""
import asyncio
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.auth.password_service import PasswordService

# ── Matriz de roles/permisos ───────────────────────────────────────────────────
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
        r = await session.execute(text("SELECT COUNT(*) FROM tenant"))
        if (r.scalar() or 0) > 0:
            print("Ya hay datos — omitiendo seed.")
            await engine.dispose()
            return

        tenant_id = uuid.uuid4()

        # ── 1. Tenant ────────────────────────────────────────────────────────
        await session.execute(
            text(
                "INSERT INTO tenant (id, tenant_id, name, slug, is_active, created_at, updated_at) "
                "VALUES (:tid, :tid, :name, :slug, true, NOW(), NOW())"
            ),
            {"tid": tenant_id, "name": "Universidad Demo", "slug": "demo"},
        )

        # ── 2. Usuarios ──────────────────────────────────────────────────────
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
            {
                "email": "tutor@demo.com",
                "pw": "Tutor123!",
                "name": "Tutor",
                "apellidos": "Demo",
                "roles": ["TUTOR"],
            },
            {
                "email": "alumno@demo.com",
                "pw": "Alumno123!",
                "name": "María",
                "apellidos": "García",
                "roles": ["ALUMNO"],
            },
        ]

        usuario_ids: dict[str, uuid.UUID] = {}

        for u in users_data:
            user_id = uuid.uuid4()
            usuario_id = uuid.uuid4()
            usuario_ids[u["email"]] = usuario_id

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

            for role in u["roles"]:
                await session.execute(
                    text(
                        "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, desde, hasta, created_at, updated_at) "
                        "VALUES (:aid, :tid, :usid, :rol, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
                    ),
                    {
                        "aid": uuid.uuid4(),
                        "tid": tenant_id,
                        "usid": usuario_id,
                        "rol": role,
                    },
                )

        # ── 3. Estructura académica ───────────────────────────────────────────
        carrera_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        materia1_id = uuid.uuid4()  # Programación I
        materia2_id = uuid.uuid4()  # Bases de Datos
        dictado1_id = uuid.uuid4()  # PROG1 / ING-SIS / 2024
        dictado2_id = uuid.uuid4()  # BDATOS / ING-SIS / 2024

        await session.execute(
            text(
                "INSERT INTO carrera (id, tenant_id, codigo, nombre, estado, created_at, updated_at) "
                "VALUES (:id, :tid, :codigo, :nombre, 'Activa', NOW(), NOW())"
            ),
            {"id": carrera_id, "tid": tenant_id, "codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"},
        )

        await session.execute(
            text(
                "INSERT INTO cohorte (id, tenant_id, carrera_id, nombre, anio, estado, created_at, updated_at) "
                "VALUES (:id, :tid, :cid, :nombre, :anio, 'Activa', NOW(), NOW())"
            ),
            {"id": cohorte_id, "tid": tenant_id, "cid": carrera_id, "nombre": "2024", "anio": 2024},
        )

        for mid, codigo, nombre in [
            (materia1_id, "PROG1", "Programación I"),
            (materia2_id, "BDATOS", "Bases de Datos"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO materia (id, tenant_id, codigo, nombre, estado, created_at, updated_at) "
                    "VALUES (:id, :tid, :codigo, :nombre, 'Activa', NOW(), NOW())"
                ),
                {"id": mid, "tid": tenant_id, "codigo": codigo, "nombre": nombre},
            )

        for did, mid in [(dictado1_id, materia1_id), (dictado2_id, materia2_id)]:
            await session.execute(
                text(
                    "INSERT INTO dictado (id, tenant_id, materia_id, carrera_id, cohorte_id, estado, created_at, updated_at) "
                    "VALUES (:id, :tid, :mid, :crid, :coid, 'Activo', NOW(), NOW())"
                ),
                {"id": did, "tid": tenant_id, "mid": mid, "crid": carrera_id, "coid": cohorte_id},
            )

        # Asignaciones con contexto: profesor y tutor a sus dictados
        coordinador_uid = usuario_ids["coordinador@demo.com"]
        profesor_uid = usuario_ids["profesor@demo.com"]
        tutor_uid = usuario_ids["tutor@demo.com"]
        alumno_uid = usuario_ids["alumno@demo.com"]

        profesor_asi1_id = uuid.uuid4()
        profesor_asi2_id = uuid.uuid4()

        for asi_id, did in [(profesor_asi1_id, dictado1_id), (profesor_asi2_id, dictado2_id)]:
            await session.execute(
                text(
                    "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, dictado_id, desde, hasta, created_at, updated_at) "
                    "VALUES (:aid, :tid, :usid, 'PROFESOR', :did, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
                ),
                {"aid": asi_id, "tid": tenant_id, "usid": profesor_uid, "did": did},
            )

        for did in [dictado1_id, dictado2_id]:
            await session.execute(
                text(
                    "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, dictado_id, desde, hasta, created_at, updated_at) "
                    "VALUES (:aid, :tid, :usid, 'TUTOR', :did, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
                ),
                {"aid": uuid.uuid4(), "tid": tenant_id, "usid": tutor_uid, "did": did},
            )

        await session.execute(
            text(
                "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, carrera_id, desde, hasta, created_at, updated_at) "
                "VALUES (:aid, :tid, :usid, 'COORDINADOR', :crid, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
            ),
            {"aid": uuid.uuid4(), "tid": tenant_id, "usid": coordinador_uid, "crid": carrera_id},
        )

        # ── 4. Padrón y calificaciones ────────────────────────────────────────
        for did, version_id, entrada_id, califs in [
            (
                dictado1_id,
                uuid.uuid4(),
                uuid.uuid4(),
                [
                    ("TP 1 — Fundamentos", 8.5, True),
                    ("TP 2 — Estructuras de control", 7.0, True),
                    ("Parcial 1", 6.5, True),
                    ("TP 3 — Funciones", 9.0, True),
                    ("Parcial 2", 5.5, True),
                ],
            ),
            (
                dictado2_id,
                uuid.uuid4(),
                uuid.uuid4(),
                [
                    ("TP 1 — Modelo relacional", 9.0, True),
                    ("Parcial 1", 4.5, False),
                    ("Recuperatorio Parcial 1", 7.0, True),
                    ("TP 2 — SQL avanzado", 8.0, True),
                    ("Parcial 2", 6.0, True),
                ],
            ),
        ]:
            await session.execute(
                text(
                    "INSERT INTO version_padron (id, tenant_id, dictado_id, cargado_por, activa, created_at, updated_at) "
                    "VALUES (:id, :tid, :did, :uid, true, NOW(), NOW())"
                ),
                {"id": version_id, "tid": tenant_id, "did": did, "uid": coordinador_uid},
            )

            await session.execute(
                text(
                    "INSERT INTO entrada_padron (id, tenant_id, version_id, usuario_id, nombre, apellidos, comision, created_at, updated_at) "
                    "VALUES (:id, :tid, :vid, :uid, 'María', 'García', 'A', NOW(), NOW())"
                ),
                {"id": entrada_id, "tid": tenant_id, "vid": version_id, "uid": alumno_uid},
            )

            for actividad, nota, aprobado in califs:
                await session.execute(
                    text(
                        "INSERT INTO calificacion (id, tenant_id, entrada_padron_id, dictado_id, actividad, nota_numerica, aprobado, origen, created_at, updated_at) "
                        "VALUES (:id, :tid, :eid, :did, :act, :nota, :aprobado, 'Importado', NOW(), NOW())"
                    ),
                    {
                        "id": uuid.uuid4(),
                        "tid": tenant_id,
                        "eid": entrada_id,
                        "did": did,
                        "act": actividad,
                        "nota": nota,
                        "aprobado": aprobado,
                    },
                )

        # ── 5. Umbrales y fechas académicas ──────────────────────────────────
        for asi_id, did in [(profesor_asi1_id, dictado1_id), (profesor_asi2_id, dictado2_id)]:
            await session.execute(
                text(
                    "INSERT INTO umbral_materia (id, tenant_id, asignacion_id, dictado_id, umbral_pct, created_at, updated_at) "
                    "VALUES (:id, :tid, :aid, :did, 60, NOW(), NOW())"
                ),
                {"id": uuid.uuid4(), "tid": tenant_id, "aid": asi_id, "did": did},
            )

        fechas = [
            # (dictado_id, tipo, numero, periodo, fecha, titulo)
            (dictado1_id, "TP",    1, "2026-1", "2026-03-25 10:00:00+00", "TP 1 — Fundamentos"),
            (dictado1_id, "TP",    2, "2026-1", "2026-04-22 10:00:00+00", "TP 2 — Estructuras de control"),
            (dictado1_id, "Parcial", 1, "2026-1", "2026-04-15 09:00:00+00", "Primer Parcial"),
            (dictado1_id, "TP",    3, "2026-1", "2026-05-20 10:00:00+00", "TP 3 — Funciones"),
            (dictado1_id, "Parcial", 2, "2026-1", "2026-06-03 09:00:00+00", "Segundo Parcial"),
            (dictado1_id, "Coloquio", 1, "2026-1", "2026-06-24 09:00:00+00", "Coloquio Final"),
            (dictado2_id, "TP",    1, "2026-1", "2026-03-30 10:00:00+00", "TP 1 — Modelo relacional"),
            (dictado2_id, "Parcial", 1, "2026-1", "2026-04-20 09:00:00+00", "Primer Parcial"),
            (dictado2_id, "Recuperatorio", 1, "2026-1", "2026-05-06 09:00:00+00", "Recuperatorio Parcial 1"),
            (dictado2_id, "TP",    2, "2026-1", "2026-05-27 10:00:00+00", "TP 2 — SQL avanzado"),
            (dictado2_id, "Parcial", 2, "2026-1", "2026-06-10 09:00:00+00", "Segundo Parcial"),
            (dictado2_id, "Coloquio", 1, "2026-1", "2026-06-27 09:00:00+00", "Coloquio Final"),
        ]

        for did, tipo, numero, periodo, fecha, titulo in fechas:
            await session.execute(
                text(
                    "INSERT INTO fecha_academica (id, tenant_id, dictado_id, tipo, numero, periodo, fecha, titulo, created_at, updated_at) "
                    "VALUES (:id, :tid, :did, :tipo, :num, :periodo, :fecha, :titulo, NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tenant_id,
                    "did": did,
                    "tipo": tipo,
                    "num": numero,
                    "periodo": periodo,
                    "fecha": fecha,
                    "titulo": titulo,
                },
            )

        # ── 6. Roles / permisos / rol_permiso ────────────────────────────────
        for codigo, nombre, descripcion in _ROLES:
            await session.execute(
                text(
                    "INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :tid, :codigo, :nombre, :desc, NOW(), NOW()) "
                    "ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING"
                ),
                {"tid": tenant_id, "codigo": codigo, "nombre": nombre, "desc": descripcion},
            )
        for codigo, modulo in _PERMISOS:
            await session.execute(
                text(
                    "INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :tid, :codigo, :codigo, NULL, :modulo, NOW(), NOW()) "
                    "ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING"
                ),
                {"tid": tenant_id, "codigo": codigo, "modulo": modulo},
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
                {"tid": tenant_id, "rc": role_codigo, "pc": permiso_codigo, "es_propio": es_propio},
            )

        await session.commit()
        print("\n✅ Seed completado exitosamente!\n")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║               CREDENCIALES DE DESARROLLO                   ║")
        print("╠═══════════════╦═════════════════════════╦═══════════════════╣")
        print("║  ROL          ║ EMAIL                   ║ PASSWORD          ║")
        print("╠═══════════════╬═════════════════════════╬═══════════════════╣")
        print("║  ADMIN        ║ admin@demo.com          ║ Admin123!         ║")
        print("║  COORDINADOR  ║ coordinador@demo.com    ║ Coord123!         ║")
        print("║  PROFESOR     ║ profesor@demo.com       ║ Demo123!          ║")
        print("║  FINANZAS     ║ finanzas@demo.com       ║ Fin123!           ║")
        print("║  NEXO         ║ nexo@demo.com           ║ Nexo123!          ║")
        print("║  TUTOR        ║ tutor@demo.com          ║ Tutor123!         ║")
        print("║  ALUMNO       ║ alumno@demo.com         ║ Alumno123!        ║")
        print("╠═══════════════╩═════════════════════════╩═══════════════════╣")
        print("║  Tenant slug: demo                                          ║")
        print("║  Carrera: Ingeniería en Sistemas (ING-SIS)                  ║")
        print("║  Cohorte: 2024  |  Materias: PROG1, BDATOS                  ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
