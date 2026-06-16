"""Seed script para entorno de desarrollo.

Crea un tenant + usuario ADMIN con contraseña hasheada (Argon2id).
Ejecutar desde la raíz del proyecto:

    docker compose up -d postgres             # si no está levantado
    docker compose exec api alembic upgrade head   # migraciones al día
    pip install -e backend                     # si no instalaste el paquete
    python scripts/seed_dev.py                 # este script

O directamente contra el contenedor:

    docker compose exec -T postgres psql -U postgres -d activia_trace < scripts/seed_dev.sql

Pero el .sql necesita un hash Argon2id pre-generado (corré python -c primero).
"""

import asyncio
import os
import sys

# Asegura que podemos importar del backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.services.auth.password_service import PasswordService

# ── Config (prioriza DATABASE_URL env var, fallback al .env) ────────────────
settings = Settings()
DATABASE_URL = os.environ.get("DATABASE_URL", settings.database_url)

PASSWORD = "admin123"  # 🚀 password para todos los usuarios de prueba
TENANT_DATA = {
    "name": "Universidad Tecnológica Nacional",
    "slug": "utn",
}

USERS = [
    {
        "email": "admin@utn.edu.ar",
        "display_name": "Admin UTN",
        "roles": ["ADMIN"],
    },
    {
        "email": "coordinador@utn.edu.ar",
        "display_name": "Coordinador UTN",
        "roles": ["COORDINADOR"],
    },
    {
        "email": "profesor@utn.edu.ar",
        "display_name": "Profesor UTN",
        "roles": ["PROFESOR"],
    },
]

# ── Seed ────────────────────────────────────────────────────────────────────


async def seed():
    """Corre el seed: tenant → users → backfill automático."""
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        # ── Tenant ─────────────────────────────────────────────────────
        tenant_row = await conn.execute(
            text("""
                INSERT INTO tenant (id, name, slug, settings, is_active, created_at, updated_at)
                VALUES (gen_random_uuid(), :name, :slug, '{}'::jsonb, true, now(), now())
                ON CONFLICT (slug) WHERE deleted_at IS NULL
                DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """),
            TENANT_DATA,
        )
        tenant_id = tenant_row.scalar()
        print(f"[OK] Tenant: {TENANT_DATA['name']} ({tenant_id})")

        # ── Users ──────────────────────────────────────────────────────
        password_hash = PasswordService.hash_password(PASSWORD)
        for u in USERS:
            user_row = await conn.execute(
                text("""
                    INSERT INTO users (id, tenant_id, email, password_hash, display_name,
                                       is_active, roles, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :email, :password_hash, :display_name,
                             true, string_to_array(:roles_text, ','), now(), now())
                    ON CONFLICT (tenant_id, email) WHERE deleted_at IS NULL
                    DO UPDATE SET display_name = EXCLUDED.display_name,
                                  password_hash = EXCLUDED.password_hash
                    RETURNING id
                """),
                {
                    "tenant_id": tenant_id,
                    "email": u["email"],
                    "password_hash": password_hash,
                    "display_name": u["display_name"],
                    "roles_text": ",".join(u["roles"]),
                },
            )
            user_id = user_row.scalar()
            print(f"  User: {u['email']} -- roles={u['roles']} ({user_id})")

        # ── Seed: roles + permisos + matriz (como en migration 003) ────
        ROLES = [
            ("ALUMNO", "Alumno", "Estudiante cursando una carrera"),
            ("TUTOR", "Tutor", "Tutor de alumnos"),
            ("PROFESOR", "Profesor", "Docente a cargo de comisiones"),
            ("COORDINADOR", "Coordinador", "Coordinador academico"),
            ("NEXO", "Nexo", "Enlace institucional"),
            ("ADMIN", "Admin", "Administrador del tenant"),
            ("FINANZAS", "Finanzas", "Gestion financiera y liquidaciones"),
        ]
        for codigo, nombre, descripcion in ROLES:
            await conn.execute(
                text("""
                    INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :descripcion, now(), now())
                    ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
                """),
                {"tenant_id": tenant_id, "codigo": codigo, "nombre": nombre, "descripcion": descripcion},
            )

        PERMISOS = [
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
            ("equipos:asignar", "equipos"),
            ("estructura:gestionar", "estructura"),
            ("usuarios:gestionar", "usuarios"),
            ("auditoria:ver", "auditoria"),
            ("grilla:operar", "grilla"),
            ("liquidaciones:cerrar", "liquidaciones"),
            ("facturas:gestionar", "facturas"),
            ("configurar:tenant", "configurar"),
            ("padron:importar", "padron"),
            ("padron:vaciar", "padron"),
            ("padron:ver", "padron"),
            ("impersonacion:usar", "impersonacion"),
        ]
        for codigo, modulo in PERMISOS:
            await conn.execute(
                text("""
                    INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :codigo, :codigo, NULL, :modulo, now(), now())
                    ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
                """),
                {"tenant_id": tenant_id, "codigo": codigo, "modulo": modulo},
            )

        MATRIX = [
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
        for role_codigo, permiso_codigo, es_propio in MATRIX:
            await conn.execute(
                text("""
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
        print(f"[OK] Roles/permisos/matriz seedeados para el tenant")

        # ── Backfill: usuario + asignacion (como en migration 007) ─────
        users = await conn.execute(
            text("""
                SELECT id, roles, created_at FROM users
                WHERE tenant_id = :tenant_id AND deleted_at IS NULL
            """),
            {"tenant_id": tenant_id},
        )

        for user_id, roles, created_at in users:
            if not roles:
                continue

            await conn.execute(
                text("""
                    INSERT INTO usuario (id, tenant_id, user_id, nombre, apellidos,
                                         facturador, estado, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :user_id, '', '', false, 'Activo', now(), now())
                    ON CONFLICT (tenant_id, user_id) WHERE deleted_at IS NULL DO NOTHING
                """),
                {"tenant_id": tenant_id, "user_id": user_id},
            )

            usuario_id = await conn.execute(
                text("""
                    SELECT id FROM usuario
                    WHERE tenant_id = :tenant_id AND user_id = :user_id AND deleted_at IS NULL
                """),
                {"tenant_id": tenant_id, "user_id": user_id},
            )
            usuario_id = usuario_id.scalar()

            for rol in roles:
                rol_str = rol.strip() if isinstance(rol, str) else rol
                desde = created_at.date() if hasattr(created_at, 'date') else created_at
                await conn.execute(
                    text("""
                        INSERT INTO asignacion (id, tenant_id, usuario_id, rol, comisiones, desde, created_at, updated_at)
                        SELECT gen_random_uuid(), :tenant_id, :usuario_id, :rol, '{}'::varchar[], :desde, now(), now()
                        WHERE NOT EXISTS (
                            SELECT 1 FROM asignacion
                            WHERE tenant_id = :tenant_id2
                              AND usuario_id = :usuario_id2
                              AND rol = :rol2
                              AND dictado_id IS NULL AND materia_id IS NULL
                              AND carrera_id IS NULL AND cohorte_id IS NULL
                              AND deleted_at IS NULL
                        )
                    """),
                    {
                        "tenant_id": tenant_id,
                        "usuario_id": usuario_id,
                        "rol": rol_str,
                        "desde": desde,
                        "tenant_id2": tenant_id,
                        "usuario_id2": usuario_id,
                        "rol2": rol_str,
                    },
                )

    await engine.dispose()


# ── Estructura Académica + Calificaciones ─────────────────────────────────────


async def seed_estructura():
    """Crea carrera, materias, cohorte, dictados, padron y calificaciones de prueba."""
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        # Re-obtener tenant_id
        tenant_row = await conn.execute(
            text("""SELECT id FROM tenant WHERE slug = :slug AND deleted_at IS NULL"""),
            {"slug": TENANT_DATA["slug"]},
        )
        tenant_id = tenant_row.scalar()
        if not tenant_id:
            print("[ERROR] No existe el tenant  -  ejecutá primero seed()")
            return

        # ── 1. Carrera ──────────────────────────────────────────────────
        carrera_row = await conn.execute(
            text("""
                INSERT INTO carrera (id, tenant_id, codigo, nombre, estado, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, 'Activa', now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL
                DO UPDATE SET nombre = EXCLUDED.nombre
                RETURNING id
            """),
            {"tenant_id": tenant_id, "codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"},
        )
        carrera_id = carrera_row.scalar()
        print(f"[OK] Carrera: ING-SIS - Ingenieria en Sistemas ({carrera_id})")

        # ── 2. Materias ─────────────────────────────────────────────────
        materias = [
            {"codigo": "MAT-101", "nombre": "Matemática I"},
            {"codigo": "PROG-101", "nombre": "Programación I"},
        ]
        materia_ids = {}
        for m in materias:
            row = await conn.execute(
                text("""
                    INSERT INTO materia (id, tenant_id, codigo, nombre, estado, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, 'Activa', now(), now())
                    ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL
                    DO UPDATE SET nombre = EXCLUDED.nombre
                    RETURNING id
                """),
                {"tenant_id": tenant_id, "codigo": m["codigo"], "nombre": m["nombre"]},
            )
            materia_ids[m["codigo"]] = row.scalar()
            print(f"[OK] Materia: {m['codigo']}  -  {m['nombre']} ({materia_ids[m['codigo']]})")

        # ── 3. Cohorte ──────────────────────────────────────────────────
        cohorte_row = await conn.execute(
            text("""
                INSERT INTO cohorte (id, tenant_id, carrera_id, nombre, anio, estado, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :carrera_id, :nombre, :anio, 'Activa', now(), now())
                ON CONFLICT (tenant_id, carrera_id, nombre) WHERE deleted_at IS NULL
                DO UPDATE SET anio = EXCLUDED.anio
                RETURNING id
            """),
            {"tenant_id": tenant_id, "carrera_id": carrera_id,
             "nombre": "2025", "anio": 2025},
        )
        cohorte_id = cohorte_row.scalar()
        print(f"[OK] Cohorte: 2025 ({cohorte_id})")

        # ── 4. Dictados ─────────────────────────────────────────────────
        dictado_ids = {}
        for m in materias:
            row = await conn.execute(
                text("""
                    INSERT INTO dictado (id, tenant_id, materia_id, carrera_id, cohorte_id, estado, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :materia_id, :carrera_id, :cohorte_id, 'Activo', now(), now())
                    ON CONFLICT (tenant_id, materia_id, carrera_id, cohorte_id) WHERE deleted_at IS NULL
                    DO UPDATE SET estado = EXCLUDED.estado
                    RETURNING id
                """),
                {
                    "tenant_id": tenant_id,
                    "materia_id": materia_ids[m["codigo"]],
                    "carrera_id": carrera_id,
                    "cohorte_id": cohorte_id,
                },
            )
            dictado_ids[m["codigo"]] = row.scalar()
            print(f"[OK] Dictado: {m['codigo']}  -  {m['nombre']} ({dictado_ids[m['codigo']]})")

        # ── 5. Asignar PROFESOR al dictado MAT-101 ──────────────────────
        prof_user_row = await conn.execute(
            text("""
                SELECT u.id FROM usuario u
                JOIN users us ON us.id = u.user_id
                WHERE us.email = 'profesor@utn.edu.ar'
                  AND u.tenant_id = :tenant_id AND u.deleted_at IS NULL
            """),
            {"tenant_id": tenant_id},
        )
        prof_usuario_id = prof_user_row.scalar()

        if prof_usuario_id:
            # Eliminar asignación previa al dictado para reinserción limpia
            await conn.execute(
                text("""
                    DELETE FROM asignacion
                    WHERE tenant_id = :tenant_id AND usuario_id = :usuario_id
                      AND dictado_id = :dictado_id AND rol = 'PROFESOR'
                """),
                {
                    "tenant_id": tenant_id,
                    "usuario_id": prof_usuario_id,
                    "dictado_id": dictado_ids["MAT-101"],
                },
            )
            await conn.execute(
                text("""
                    INSERT INTO asignacion (id, tenant_id, usuario_id, rol, dictado_id, comisiones, desde, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :usuario_id, 'PROFESOR', :dictado_id, '{"A","B"}'::varchar[], '2025-03-01'::date, now(), now())
                """),
                {
                    "tenant_id": tenant_id,
                    "usuario_id": prof_usuario_id,
                    "dictado_id": dictado_ids["MAT-101"],
                },
            )
            print(f"[OK] Asignacion: PROFESOR -> MAT-101")

        # ── 6. VersionPadron activa para MAT-101 ───────────────────────
        admin_user_row = await conn.execute(
            text("""
                SELECT u.id FROM usuario u
                JOIN users us ON us.id = u.user_id
                WHERE us.email = 'admin@utn.edu.ar'
                  AND u.tenant_id = :tenant_id AND u.deleted_at IS NULL
            """),
            {"tenant_id": tenant_id},
        )
        admin_usuario_id = admin_user_row.scalar()

        # Eliminar version activa previa si existe (para re-ejecución idempotente)
        await conn.execute(
            text("""
                DELETE FROM version_padron
                WHERE tenant_id = :tenant_id AND dictado_id = :dictado_id AND activa = true
            """),
            {"tenant_id": tenant_id, "dictado_id": dictado_ids["MAT-101"]},
        )

        vp_row = await conn.execute(
            text("""
                INSERT INTO version_padron (id, tenant_id, dictado_id, cargado_por, activa, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :dictado_id, :cargado_por, true, now(), now())
                RETURNING id
            """),
            {
                "tenant_id": tenant_id,
                "dictado_id": dictado_ids["MAT-101"],
                "cargado_por": admin_usuario_id,
            },
        )
        vp_id = vp_row.scalar()
        print(f"[OK] VersionPadron activa para MAT-101 ({vp_id})")

        # ── 7. Entradas de padrón (5 alumnos) ───────────────────────────
        # Limpiar entradas viejas para idempotencia (cascadea calificaciones)
        await conn.execute(
            text("""
                DELETE FROM entrada_padron
                WHERE tenant_id = :tenant_id AND version_id = :version_id
            """),
            {"tenant_id": tenant_id, "version_id": vp_id},
        )

        alumnos = [
            # (nombre, apellido, comision, email)
            ("Juan", "Pérez", "A", "juan.perez@example.com"),
            ("María", "García", "A", "maria.garcia@example.com"),
            ("Carlos", "López", "B", "carlos.lopez@example.com"),
            ("Ana", "Martínez", "A", "ana.martinez@example.com"),
            ("Pedro", "Rodríguez", "B", "pedro.rodriguez@example.com"),
        ]
        entrada_ids = {}
        for nombre, apellidos, comision, email in alumnos:
            # email va cifrado con EncryptedString  -  en SQL raw insertamos el string plano
            # porque el cifrado ocurre a nivel ORM. Para seed raw, ponemos NULL.
            row = await conn.execute(
                text("""
                    INSERT INTO entrada_padron (id, tenant_id, version_id, nombre, apellidos, comision, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :version_id, :nombre, :apellidos, :comision, now(), now())
                    RETURNING id
                """),
                {
                    "tenant_id": tenant_id,
                    "version_id": vp_id,
                    "nombre": nombre,
                    "apellidos": apellidos,
                    "comision": comision,
                },
            )
            ep_id = row.scalar()
            entrada_ids[f"{nombre}_{apellidos}"] = ep_id

        print(f"[OK] 5 entradas de padrón creadas para MAT-101")

        # ── 8. Calificaciones ───────────────────────────────────────────
        # Escenarios (umbral default pct=60):
        #
        #   Juan Pérez    → Promocionado (RN-07): TP1=85✅, TP2=90✅  → no atrasado
        #   María García  → Regular (RN-08):    TP1=65✅, TP2=80✅  → no atrasado
        #   Carlos López  → Desaprobado (RN-09): TP1=30❌, TP2=55❌ → atrasado (ambas < 60)
        #   Ana Martínez  → Faltante (RN-06):    TP1=75✅, TP2 sin calif → atrasado (faltante)
        #   Pedro Rodríguez → Textual no aprob:  TP1=85✅, TP2="Regular"❌ → atrasado
        #
        calificaciones = [
            # Juan Pérez: promocionado
            ("Juan_Pérez", "TP1", 85.0, None, True),
            ("Juan_Pérez", "TP2", 90.0, None, True),
            # María García: regular
            ("María_García", "TP1", 65.0, None, True),
            ("María_García", "TP2", 80.0, None, True),
            # Carlos López: desaprobado
            ("Carlos_López", "TP1", 30.0, None, False),
            ("Carlos_López", "TP2", 55.0, None, False),
            # Ana Martínez: faltante (solo TP1)
            ("Ana_Martínez", "TP1", 75.0, None, True),
            # Pedro Rodríguez: textual no aprobatorio
            ("Pedro_Rodríguez", "TP1", 85.0, None, True),
            ("Pedro_Rodríguez", "TP2", None, "Regular", False),
        ]

        for key, actividad, nota_num, nota_txt, aprobado in calificaciones:
            ep_id = entrada_ids[key]
            await conn.execute(
                text("""
                    INSERT INTO calificacion (id, tenant_id, entrada_padron_id, dictado_id,
                                              actividad, nota_numerica, nota_textual, aprobado, origen, importado_at,
                                              created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :ep_id, :dictado_id,
                            :actividad, :nota_num, :nota_txt, :aprobado, 'Importado', now(),
                            now(), now())
                """),
                {
                    "tenant_id": tenant_id,
                    "ep_id": ep_id,
                    "dictado_id": dictado_ids["MAT-101"],
                    "actividad": actividad,
                    "nota_num": nota_num,
                    "nota_txt": nota_txt,
                    "aprobado": aprobado,
                },
            )

        print(f"[OK] {len(calificaciones)} calificaciones insertadas para MAT-101")

        # ── 9. UmbralMateria opcional para MAT-101 ──────────────────────
        # Usamos la asignacion tenant-global del PROFESOR
        prof_asig_row = await conn.execute(
            text("""
                SELECT a.id FROM asignacion a
                JOIN usuario u ON u.id = a.usuario_id
                JOIN users us ON us.id = u.user_id
                WHERE us.email = 'profesor@utn.edu.ar'
                  AND a.rol = 'PROFESOR' AND a.dictado_id = :dictado_id
                  AND a.deleted_at IS NULL
                LIMIT 1
            """),
            {"dictado_id": dictado_ids["MAT-101"]},
        )
        prof_asig_id = prof_asig_row.scalar()

        if prof_asig_id:
            await conn.execute(
                text("""
                    INSERT INTO umbral_materia (id, tenant_id, asignacion_id, dictado_id,
                                                umbral_pct, valores_aprobatorios, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tenant_id, :asignacion_id, :dictado_id,
                            60, '["Satisfactorio", "Supera lo esperado"]'::jsonb, now(), now())
                    ON CONFLICT (tenant_id, asignacion_id, dictado_id) DO NOTHING
                """),
                {
                    "tenant_id": tenant_id,
                    "asignacion_id": prof_asig_id,
                    "dictado_id": dictado_ids["MAT-101"],
                },
            )
            print(f"[OK] UmbralMateria para MAT-101 (pct=60)")

    await engine.dispose()

    print(f"\n=== Estructura académica completada ===")
    print(f"   Carrera:  ING-SIS  -  Ingeniería en Sistemas")
    print(f"   Materias: MAT-101, PROG-101")
    print(f"   Cohorte:  2025")
    print(f"   Dictados: MAT-101 (con alumnos+califs), PROG-101 (vacío)")
    print()
    print(f"Escenarios en MAT-101 (umbral 60%):")
    print(f"   Juan Perez      -> TP1=85, TP2=90   -> Promocionado")
    print(f"   Maria Garcia    -> TP1=65, TP2=80   -> Regular")
    print(f"   Carlos Lopez    -> TP1=30, TP2=55   -> Desaprobado (atrasado)")
    print(f"   Ana Martinez    -> TP1=75, sin TP2  -> Faltante (atrasado)")
    print(f"   Pedro Rodriguez -> TP1=85, TP2=Regular -> Textual no aprob (atrasado)")


async def full_seed():
    """Ejecuta seed completo: tenant + usuarios + estructura + calificaciones."""
    await seed()
    print("\n" + "=" * 60)
    await seed_estructura()


if __name__ == "__main__":
    asyncio.run(full_seed())
