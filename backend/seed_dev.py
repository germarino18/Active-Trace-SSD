"""Seed desarrollo completo: tenant + usuarios + estructura académica + roles/permisos."""

import asyncio
import hashlib
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.security import encrypt_value, get_encryption_key
from app.core.security import encrypt_value, get_encryption_key
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
    (
        "liquidaciones:configurar-salarios",
        "Configurar grilla salarial",
        "liquidaciones",
    ),
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
    (
        "actividades:gestionar",
        "Gestionar actividades",
        "actividades",
    ),
    ("calificaciones:editar", "Editar calificaciones", "calificaciones"),
    ("padron:gestionar-alumno", "Gestionar padron", "padron"),
]

_MATRIX = [
    # ALUMNO
    ("ALUMNO", "estado-academico:ver", False),
    ("ALUMNO", "evaluacion:reservar", False),
    ("ALUMNO", "avisos:confirmar", False),
    ("ALUMNO", "inbox:acceder", False),
    ("ALUMNO", "coloquios:reservar", False),
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
    ("PROFESOR", "coloquios:ver", True),
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
    ("COORDINADOR", "coloquios:gestionar", False),
    ("COORDINADOR", "coloquios:ver", False),
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
    ("ADMIN", "coloquios:gestionar", False),
    ("ADMIN", "coloquios:ver", False),
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
    # C-25 profesor dashboard
    ("PROFESOR", "actividades:gestionar", True),
    ("PROFESOR", "calificaciones:editar", True),
    ("PROFESOR", "padron:gestionar-alumno", True),
    ("COORDINADOR", "actividades:gestionar", False),
    ("COORDINADOR", "calificaciones:editar", False),
    ("COORDINADOR", "padron:gestionar-alumno", False),
    ("ADMIN", "actividades:gestionar", False),
    ("ADMIN", "calificaciones:editar", False),
    ("ADMIN", "padron:gestionar-alumno", False),
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
        tid = tenant_id  # alias para legibilidad

        # ── 1. Tenant ────────────────────────────────────────────────────────
        await session.execute(
            text(
                "INSERT INTO tenant (id, tenant_id, name, slug, is_active, created_at, updated_at) "
                "VALUES (:tid, :tid, :name, :slug, true, NOW(), NOW())"
            ),
            {"tid": tid, "name": "Universidad Demo", "slug": "demo"},
        )

        # ── 2. Usuarios ──────────────────────────────────────────────────────
        users_data = [
            {
                "email": "admin@demo.com",
                "pw": "Admin123!",
                "name": "Admin",
                "apellidos": "Demo",
                "roles": ["ADMIN", "COORDINADOR"],
                "facturador": False,
            },
            {
                "email": "coordinador@demo.com",
                "pw": "Coord123!",
                "name": "Coordinador",
                "apellidos": "Demo",
                "roles": ["COORDINADOR"],
                "facturador": False,
            },
            {
                "email": "profesor@demo.com",
                "pw": "Demo123!",
                "name": "Carlos",
                "apellidos": "López",
                "roles": ["PROFESOR"],
                "facturador": True,
            },
            {
                "email": "finanzas@demo.com",
                "pw": "Fin123!",
                "name": "Finanzas",
                "apellidos": "Demo",
                "roles": ["FINANZAS"],
                "facturador": False,
            },
            {
                "email": "nexo@demo.com",
                "pw": "Nexo123!",
                "name": "Nexo",
                "apellidos": "Demo",
                "roles": ["NEXO"],
                "facturador": False,
            },
            {
                "email": "tutor@demo.com",
                "pw": "Tutor123!",
                "name": "Ana",
                "apellidos": "Martínez",
                "roles": ["TUTOR"],
                "facturador": False,
            },
            {
                "email": "alumno@demo.com",
                "pw": "Alumno123!",
                "name": "María",
                "apellidos": "García",
                "roles": ["ALUMNO"],
                "facturador": False,
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
                    "tid": tid,
                    "email": u["email"],
                    "pw": PasswordService.hash_password(u["pw"]),
                    "name": f"{u['name']} {u['apellidos']}",
                    "roles": u["roles"],
                },
            )
            await session.execute(
                text(
                    # WARNING: usuario.dni/cuil/cbu/alias_cbu are EncryptedString columns
                    # DO NOT add them as raw values here — always encrypt via encrypt_value()
                    "INSERT INTO usuario (id, tenant_id, user_id, nombre, apellidos, legajo, facturador, estado, created_at, updated_at) "
                    "VALUES (:usid, :tid, :uid, :nom, :ape, :leg, :fac, 'Activo', NOW(), NOW())"
                ),
                {
                    "usid": usuario_id,
                    "tid": tid,
                    "uid": user_id,
                    "nom": u["name"],
                    "ape": u["apellidos"],
                    "leg": u["email"].split("@")[0],
                    "fac": u["facturador"],
                },
            )
            for role in u["roles"]:
                await session.execute(
                    text(
                        "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, desde, hasta, created_at, updated_at) "
                        "VALUES (:aid, :tid, :usid, :rol, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
                    ),
                    {"aid": uuid.uuid4(), "tid": tid, "usid": usuario_id, "rol": role},
                )

        coordinador_uid = usuario_ids["coordinador@demo.com"]
        profesor_uid = usuario_ids["profesor@demo.com"]
        tutor_uid = usuario_ids["tutor@demo.com"]
        alumno_uid = usuario_ids["alumno@demo.com"]

        # ── 2b. Alumnos extra (para picker alumnos-disponibles) ───────────────
        extra_alumnos = [
            {"email": "pedro.gomez@demo.com", "name": "Pedro", "apellidos": "Gómez"},
            {"email": "laura.diaz@demo.com", "name": "Laura", "apellidos": "Díaz"},
            {"email": "jorge.silva@demo.com", "name": "Jorge", "apellidos": "Silva"},
            {"email": "ana.torres@demo.com", "name": "Ana", "apellidos": "Torres"},
            {"email": "martin.ruiz@demo.com", "name": "Martín", "apellidos": "Ruiz"},
        ]
        for eu in extra_alumnos:
            extra_user_id = uuid.uuid4()
            extra_usuario_id = uuid.uuid4()
            await session.execute(
                text(
                    "INSERT INTO users (id, tenant_id, email, password_hash, display_name, is_active, roles, created_at, updated_at) "
                    "VALUES (:uid, :tid, :email, :pw, :name, true, :roles, NOW(), NOW())"
                ),
                {
                    "uid": extra_user_id,
                    "tid": tid,
                    "email": eu["email"],
                    "pw": PasswordService.hash_password("Alumno123!"),
                    "name": f"{eu['name']} {eu['apellidos']}",
                    "roles": ["ALUMNO"],
                },
            )
            await session.execute(
                text(
                    "INSERT INTO usuario (id, tenant_id, user_id, nombre, apellidos, legajo, facturador, estado, created_at, updated_at) "
                    "VALUES (:usid, :tid, :uid, :nom, :ape, :leg, false, 'Activo', NOW(), NOW())"
                ),
                {
                    "usid": extra_usuario_id,
                    "tid": tid,
                    "uid": extra_user_id,
                    "nom": eu["name"],
                    "ape": eu["apellidos"],
                    "leg": eu["email"].split("@")[0],
                },
            )
            # Global ALUMNO asignacion (vigente)
            await session.execute(
                text(
                    "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, desde, hasta, created_at, updated_at) "
                    "VALUES (:aid, :tid, :usid, 'ALUMNO', CURRENT_DATE, '2099-12-31', NOW(), NOW())"
                ),
                {"aid": uuid.uuid4(), "tid": tid, "usid": extra_usuario_id},
            )

        # ── 3. Estructura académica ───────────────────────────────────────────
        carrera_id = uuid.uuid4()
        cohorte_id = uuid.uuid4()
        materia1_id = uuid.uuid4()  # PROG1
        materia2_id = uuid.uuid4()  # BDATOS
        dictado1_id = uuid.uuid4()  # PROG1 / ING-SIS / 2024
        dictado2_id = uuid.uuid4()  # BDATOS / ING-SIS / 2024

        await session.execute(
            text(
                "INSERT INTO carrera (id, tenant_id, codigo, nombre, estado, created_at, updated_at) VALUES (:id, :tid, :cod, :nom, 'Activa', NOW(), NOW())"
            ),
            {
                "id": carrera_id,
                "tid": tid,
                "cod": "ING-SIS",
                "nom": "Ingeniería en Sistemas",
            },
        )
        await session.execute(
            text(
                "INSERT INTO cohorte (id, tenant_id, carrera_id, nombre, anio, estado, created_at, updated_at) VALUES (:id, :tid, :cid, :nom, :anio, 'Activa', NOW(), NOW())"
            ),
            {
                "id": cohorte_id,
                "tid": tid,
                "cid": carrera_id,
                "nom": "2024",
                "anio": 2024,
            },
        )
        # Vincular alumno al cohorte via su asignacion (creada en el loop de usuarios, línea 203)
        await session.execute(
            text(
                "UPDATE asignacion SET cohorte_id = :coid WHERE usuario_id = :uid AND rol = 'ALUMNO'"
            ),
            {"coid": cohorte_id, "uid": alumno_uid},
        )
        for mid, cod, nom in [
            (materia1_id, "PROG1", "Programación I"),
            (materia2_id, "BDATOS", "Bases de Datos"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO materia (id, tenant_id, codigo, nombre, estado, created_at, updated_at) VALUES (:id, :tid, :cod, :nom, 'Activa', NOW(), NOW())"
                ),
                {"id": mid, "tid": tid, "cod": cod, "nom": nom},
            )
        for did, mid in [(dictado1_id, materia1_id), (dictado2_id, materia2_id)]:
            await session.execute(
                text(
                    "INSERT INTO dictado (id, tenant_id, materia_id, carrera_id, cohorte_id, estado, created_at, updated_at) VALUES (:id, :tid, :mid, :crid, :coid, 'Activo', NOW(), NOW())"
                ),
                {
                    "id": did,
                    "tid": tid,
                    "mid": mid,
                    "crid": carrera_id,
                    "coid": cohorte_id,
                },
            )

        # Asignaciones contextuales
        profesor_asi1_id = uuid.uuid4()
        profesor_asi2_id = uuid.uuid4()
        tutor_asi1_id = uuid.uuid4()
        tutor_asi2_id = uuid.uuid4()

        for asi_id, uid, rol, did in [
            (profesor_asi1_id, profesor_uid, "PROFESOR", dictado1_id),
            (profesor_asi2_id, profesor_uid, "PROFESOR", dictado2_id),
            (tutor_asi1_id, tutor_uid, "TUTOR", dictado1_id),
            (tutor_asi2_id, tutor_uid, "TUTOR", dictado2_id),
        ]:
            await session.execute(
                text(
                    "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, dictado_id, desde, hasta, created_at, updated_at) VALUES (:aid, :tid, :uid, :rol, :did, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
                ),
                {"aid": asi_id, "tid": tid, "uid": uid, "rol": rol, "did": did},
            )
        await session.execute(
            text(
                "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, carrera_id, desde, hasta, created_at, updated_at) VALUES (:aid, :tid, :uid, 'COORDINADOR', :crid, CURRENT_DATE, '2099-12-31', NOW(), NOW())"
            ),
            {
                "aid": uuid.uuid4(),
                "tid": tid,
                "uid": coordinador_uid,
                "crid": carrera_id,
            },
        )

        # ── 4. Actividades evaluables para dictado1 ──────────────────────────────
        # TP 1 y TP 2 con fecha_limite en el pasado → missing = atrasado_null
        actividad1_id = uuid.uuid4()
        actividad2_id = uuid.uuid4()
        for act_id, act_nombre in [(actividad1_id, "TP 1"), (actividad2_id, "TP 2")]:
            await session.execute(
                text(
                    "INSERT INTO actividad (id, tenant_id, dictado_id, nombre, tipo, fecha_limite, created_at, updated_at) "
                    "VALUES (:id, :tid, :did, :nombre, 'TP', '2025-06-01', NOW(), NOW())"
                ),
                {"id": act_id, "tid": tid, "did": dictado1_id, "nombre": act_nombre},
            )

        # ── 4. Padrón y calificaciones ────────────────────────────────────────
        # dictado1: María García (original) + Pedro Gómez + Laura Díaz enrolled
        # Jorge Silva, Ana Torres, Martín Ruiz left unenrolled (for picker)
        version1_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO version_padron (id, tenant_id, dictado_id, cargado_por, activa, created_at, updated_at) VALUES (:id, :tid, :did, :uid, true, NOW(), NOW())"
            ),
            {"id": version1_id, "tid": tid, "did": dictado1_id, "uid": coordinador_uid},
        )

        # Entrada de María García (alumno original)
        entrada_maria_id = uuid.uuid4()
        _seed_enc_key = get_encryption_key()
        # WARNING: EncryptedString column — raw SQL bypasses TypeDecorator, encrypt manually
        email_maria = encrypt_value("alumno@demo.com", _seed_enc_key)
        await session.execute(
            text(
                "INSERT INTO entrada_padron (id, tenant_id, version_id, usuario_id, nombre, apellidos, comision, email, created_at, updated_at) VALUES (:id, :tid, :vid, :uid, 'María', 'García', 'A', :email, NOW(), NOW())"
            ),
            {
                "id": entrada_maria_id,
                "tid": tid,
                "vid": version1_id,
                "uid": alumno_uid,
                "email": email_maria,
            },
        )

        # Resolver usuario_ids de Pedro Gómez y Laura Díaz
        pedro_uid_row = await session.execute(
            text(
                "SELECT u.id FROM usuario u JOIN users us ON us.id = u.user_id WHERE us.email = 'pedro.gomez@demo.com' AND u.tenant_id = :tid"
            ),
            {"tid": tid},
        )
        pedro_uid = pedro_uid_row.scalar_one()

        laura_uid_row = await session.execute(
            text(
                "SELECT u.id FROM usuario u JOIN users us ON us.id = u.user_id WHERE us.email = 'laura.diaz@demo.com' AND u.tenant_id = :tid"
            ),
            {"tid": tid},
        )
        laura_uid = laura_uid_row.scalar_one()

        entrada_pedro_id = uuid.uuid4()
        entrada_laura_id = uuid.uuid4()
        for eid, uid, nom, ape in [
            (entrada_pedro_id, pedro_uid, "Pedro", "Gómez"),
            (entrada_laura_id, laura_uid, "Laura", "Díaz"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO entrada_padron (id, tenant_id, version_id, usuario_id, nombre, apellidos, comision, created_at, updated_at) VALUES (:id, :tid, :vid, :uid, :nom, :ape, 'A', NOW(), NOW())"
                ),
                {
                    "id": eid,
                    "tid": tid,
                    "vid": version1_id,
                    "uid": uid,
                    "nom": nom,
                    "ape": ape,
                },
            )

        # Calificaciones para dictado1:
        # María García: APROBADO TP 1, DESAPROBADO TP 2 → atrasada (desaprobado)
        # Pedro Gómez: APROBADO TP 1, sin calificacion TP 2 → atrasado (atrasado_null)
        # Laura Díaz: sin calificaciones → atrasada (atrasado_null en TP 1 y TP 2)
        for eid, act_id, act_nombre, nota, aprobado in [
            (entrada_maria_id, actividad1_id, "TP 1", 8.5, True),
            (entrada_maria_id, actividad2_id, "TP 2", 3.0, False),
            (entrada_pedro_id, actividad1_id, "TP 1", 9.0, True),
            # Pedro no tiene calificacion para TP 2 → atrasado_null
        ]:
            await session.execute(
                text(
                    "INSERT INTO calificacion (id, tenant_id, entrada_padron_id, dictado_id, "
                    "actividad, actividad_id, nota_numerica, aprobado, origen, created_at, updated_at) "
                    "VALUES (:id, :tid, :eid, :did, :act, :act_id, :nota, :ap, 'Importado', NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "eid": eid,
                    "did": dictado1_id,
                    "act": act_nombre,
                    "act_id": act_id,
                    "nota": nota,
                    "ap": aprobado,
                },
            )

        # ── 4b. Actividades evaluables para dictado2 (Bases de Datos) ────────────
        # Mirrors dictado1's format: actividad rows + actividad_id on calificaciones.
        bd_actividades = [
            ("TP 1 — Modelo relacional", "TP"),
            ("Parcial 1", "Parcial"),
            ("Recuperatorio Parcial 1", "Recuperatorio"),
            ("TP 2 — SQL avanzado", "TP"),
            ("Parcial 2", "Parcial"),
        ]
        bd_actividad_ids: dict[str, uuid.UUID] = {}
        for act_nombre, act_tipo in bd_actividades:
            act_id = uuid.uuid4()
            bd_actividad_ids[act_nombre] = act_id
            await session.execute(
                text(
                    "INSERT INTO actividad (id, tenant_id, dictado_id, nombre, tipo, created_at, updated_at) "
                    "VALUES (:id, :tid, :did, :nombre, :tipo, NOW(), NOW())"
                ),
                {
                    "id": act_id,
                    "tid": tid,
                    "did": dictado2_id,
                    "nombre": act_nombre,
                    "tipo": act_tipo,
                },
            )

        # dictado2: solo María García, calificaciones vinculadas via actividad_id (formato correcto)
        version2_id = uuid.uuid4()
        entrada2_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO version_padron (id, tenant_id, dictado_id, cargado_por, activa, created_at, updated_at) VALUES (:id, :tid, :did, :uid, true, NOW(), NOW())"
            ),
            {"id": version2_id, "tid": tid, "did": dictado2_id, "uid": coordinador_uid},
        )
        # WARNING: EncryptedString column — raw SQL bypasses TypeDecorator, encrypt manually
        email_maria2 = encrypt_value("alumno@demo.com", _seed_enc_key)
        await session.execute(
            text(
                "INSERT INTO entrada_padron (id, tenant_id, version_id, usuario_id, nombre, apellidos, comision, email, created_at, updated_at) VALUES (:id, :tid, :vid, :uid, 'María', 'García', 'A', :email, NOW(), NOW())"
            ),
            {
                "id": entrada2_id,
                "tid": tid,
                "vid": version2_id,
                "uid": alumno_uid,
                "email": email_maria2,
            },
        )
        for act_nombre, nota, aprobado in [
            ("TP 1 — Modelo relacional", 9.0, True),
            ("Parcial 1", 4.5, False),
            ("Recuperatorio Parcial 1", 7.0, True),
            ("TP 2 — SQL avanzado", 8.0, True),
            ("Parcial 2", 6.0, True),
        ]:
            await session.execute(
                text(
                    "INSERT INTO calificacion "
                    "(id, tenant_id, entrada_padron_id, dictado_id, actividad, actividad_id, "
                    "nota_numerica, aprobado, origen, created_at, updated_at) "
                    "VALUES (:id, :tid, :eid, :did, :act, :act_id, :nota, :ap, 'Importado', NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "eid": entrada2_id,
                    "did": dictado2_id,
                    "act": act_nombre,
                    "act_id": bd_actividad_ids[act_nombre],
                    "nota": nota,
                    "ap": aprobado,
                },
            )

        # ── 5. Umbrales y fechas académicas ──────────────────────────────────
        for asi_id, did in [
            (profesor_asi1_id, dictado1_id),
            (profesor_asi2_id, dictado2_id),
        ]:
            await session.execute(
                text(
                    "INSERT INTO umbral_materia (id, tenant_id, asignacion_id, dictado_id, umbral_pct, created_at, updated_at) VALUES (:id, :tid, :aid, :did, 60, NOW(), NOW())"
                ),
                {"id": uuid.uuid4(), "tid": tid, "aid": asi_id, "did": did},
            )
        for did, tipo, num, periodo, fecha, titulo in [
            (
                dictado1_id,
                "TP",
                1,
                "2026-1",
                "2026-03-25 10:00:00+00",
                "TP 1 — Fundamentos",
            ),
            (
                dictado1_id,
                "TP",
                2,
                "2026-1",
                "2026-04-22 10:00:00+00",
                "TP 2 — Estructuras de control",
            ),
            (
                dictado1_id,
                "Parcial",
                1,
                "2026-1",
                "2026-04-15 09:00:00+00",
                "Primer Parcial",
            ),
            (
                dictado1_id,
                "TP",
                3,
                "2026-1",
                "2026-05-20 10:00:00+00",
                "TP 3 — Funciones",
            ),
            (
                dictado1_id,
                "Parcial",
                2,
                "2026-1",
                "2026-06-03 09:00:00+00",
                "Segundo Parcial",
            ),
            (
                dictado1_id,
                "Coloquio",
                1,
                "2026-1",
                "2026-06-24 09:00:00+00",
                "Coloquio Final",
            ),
            (
                dictado2_id,
                "TP",
                1,
                "2026-1",
                "2026-03-30 10:00:00+00",
                "TP 1 — Modelo relacional",
            ),
            (
                dictado2_id,
                "Parcial",
                1,
                "2026-1",
                "2026-04-20 09:00:00+00",
                "Primer Parcial",
            ),
            (
                dictado2_id,
                "Recuperatorio",
                1,
                "2026-1",
                "2026-05-06 09:00:00+00",
                "Recuperatorio Parcial 1",
            ),
            (
                dictado2_id,
                "TP",
                2,
                "2026-1",
                "2026-05-27 10:00:00+00",
                "TP 2 — SQL avanzado",
            ),
            (
                dictado2_id,
                "Parcial",
                2,
                "2026-1",
                "2026-06-10 09:00:00+00",
                "Segundo Parcial",
            ),
            (
                dictado2_id,
                "Coloquio",
                1,
                "2026-1",
                "2026-06-27 09:00:00+00",
                "Coloquio Final",
            ),
        ]:
            await session.execute(
                text(
                    f"INSERT INTO fecha_academica (id, tenant_id, dictado_id, tipo, numero, periodo, fecha, titulo, created_at, updated_at) VALUES (:id, :tid, :did, :tipo, :num, :per, '{fecha}', :titulo, NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "did": did,
                    "tipo": tipo,
                    "num": num,
                    "per": periodo,
                    "titulo": titulo,
                },
            )

        # ── 6. Programas de materia ───────────────────────────────────────────
        for did, titulo, ref in [
            (
                dictado1_id,
                "Programa Programación I — 2024",
                "programas/ING-SIS/2024/PROG1.pdf",
            ),
            (
                dictado2_id,
                "Programa Bases de Datos — 2024",
                "programas/ING-SIS/2024/BDATOS.pdf",
            ),
        ]:
            await session.execute(
                text(
                    "INSERT INTO programa_materia (id, tenant_id, dictado_id, titulo, referencia_archivo, created_at, updated_at) VALUES (:id, :tid, :did, :titulo, :ref, NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "did": did,
                    "titulo": titulo,
                    "ref": ref,
                },
            )

        # ── 7. Slots de encuentro e instancias ────────────────────────────────
        slot1_id = uuid.uuid4()
        slot2_id = uuid.uuid4()
        for slot_id, asi_id, did, titulo, hora, dia, fecha_inicio in [
            (
                slot1_id,
                tutor_asi1_id,
                dictado1_id,
                "Tutoría Programación I",
                "18:00:00",
                "Martes",
                "2026-03-04",
            ),
            (
                slot2_id,
                tutor_asi2_id,
                dictado2_id,
                "Tutoría Bases de Datos",
                "19:00:00",
                "Jueves",
                "2026-03-06",
            ),
        ]:
            await session.execute(
                text(
                    f"INSERT INTO slot_encuentro (id, tenant_id, dictado_id, asignacion_id, titulo, hora, dia_semana, fecha_inicio, cant_semanas, vig_desde, created_at, updated_at) "
                    f"VALUES (:id, :tid, :did, :aid, :titulo, '{hora}', :dia, '{fecha_inicio}', 16, '{fecha_inicio}', NOW(), NOW())"
                ),
                {
                    "id": slot_id,
                    "tid": tid,
                    "did": did,
                    "aid": asi_id,
                    "titulo": titulo,
                    "dia": dia,
                },
            )
        for slot_id, asi_id, did, fechas in [
            (
                slot1_id,
                tutor_asi1_id,
                dictado1_id,
                [
                    ("2026-03-11", "Realizado"),
                    ("2026-03-18", "Realizado"),
                    ("2026-04-01", "Realizado"),
                    ("2026-06-17", "Programado"),
                ],
            ),
            (
                slot2_id,
                tutor_asi2_id,
                dictado2_id,
                [
                    ("2026-03-13", "Realizado"),
                    ("2026-03-20", "Realizado"),
                    ("2026-06-19", "Programado"),
                ],
            ),
        ]:
            for fecha, estado in fechas:
                hora = "18:00:00" if did == dictado1_id else "19:00:00"
                titulo_inst = (
                    "Tutoría Programación I"
                    if did == dictado1_id
                    else "Tutoría Bases de Datos"
                )
                await session.execute(
                    text(
                        f"INSERT INTO instancia_encuentro (id, tenant_id, slot_id, dictado_id, asignacion_id, fecha, hora, titulo, estado, created_at, updated_at) "
                        f"VALUES (:id, :tid, :sid, :did, :aid, '{fecha}', '{hora}', :titulo, :estado, NOW(), NOW())"
                    ),
                    {
                        "id": uuid.uuid4(),
                        "tid": tid,
                        "sid": slot_id,
                        "did": did,
                        "aid": asi_id,
                        "titulo": titulo_inst,
                        "estado": estado,
                    },
                )

        # ── 8. Guardias de consulta ───────────────────────────────────────────
        for asi_id, did, dia, horario in [
            (tutor_asi1_id, dictado1_id, "Lunes", "10:00 - 12:00"),
            (tutor_asi1_id, dictado1_id, "Viernes", "14:00 - 16:00"),
            (tutor_asi2_id, dictado2_id, "Miércoles", "15:00 - 17:00"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO guardia (id, tenant_id, asignacion_id, dictado_id, dia, horario, estado, creada_at, created_at, updated_at) "
                    "VALUES (:id, :tid, :aid, :did, :dia, :horario, 'Pendiente', NOW(), NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "aid": asi_id,
                    "did": did,
                    "dia": dia,
                    "horario": horario,
                },
            )

        # ── 9. Evaluaciones / coloquios ───────────────────────────────────────
        # NOTE: created_by_id is set to the profesor's user_id so
        # GET /profesor/coloquios/mios (filtered by created_by_id) returns results.
        eval1_id = uuid.uuid4()
        eval2_id = uuid.uuid4()
        eval3_id = uuid.uuid4()  # extra closed coloquio for PROG1
        # Resolve the profesor's users.id (not usuario.id) for created_by_id
        prof_user_id_row = await session.execute(
            text(
                "SELECT id FROM users WHERE email = 'profesor@demo.com' AND tenant_id = :tid"
            ),
            {"tid": tid},
        )
        prof_user_id = prof_user_id_row.scalar_one()
        for eval_id, did, instancia, estado in [
            (eval1_id, dictado1_id, "Coloquio Final — Programación I", "Activa"),
            (eval2_id, dictado2_id, "Coloquio Final — Bases de Datos", "Activa"),
            (eval3_id, dictado1_id, "Recuperatorio — Programación I", "Cerrada"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO evaluacion (id, tenant_id, dictado_id, tipo, instancia, cupo_maximo, estado, "
                    "created_by_id, created_at, updated_at) "
                    "VALUES (:id, :tid, :did, 'Coloquio', :inst, 20, :estado, :cbid, NOW(), NOW())"
                ),
                {
                    "id": eval_id,
                    "tid": tid,
                    "did": did,
                    "inst": instancia,
                    "estado": estado,
                    "cbid": prof_user_id,
                },
            )
            await session.execute(
                text(
                    "INSERT INTO alumno_convocado (id, tenant_id, evaluacion_id, alumno_id, created_at, updated_at) VALUES (:id, :tid, :eid, :uid, NOW(), NOW())"
                ),
                {"id": uuid.uuid4(), "tid": tid, "eid": eval_id, "uid": alumno_uid},
            )

        # Alumno reserva el coloquio de Programación I
        await session.execute(
            text(
                "INSERT INTO reserva_evaluacion (id, tenant_id, evaluacion_id, alumno_id, fecha_hora, estado, created_at, updated_at) "
                "VALUES (:id, :tid, :eid, :uid, '2026-06-24 09:00:00+00', 'Activa', NOW(), NOW())"
            ),
            {"id": uuid.uuid4(), "tid": tid, "eid": eval1_id, "uid": alumno_uid},
        )
        # Coloquio de Bases de Datos ya tiene resultado
        await session.execute(
            text(
                "INSERT INTO resultado_evaluacion (id, tenant_id, evaluacion_id, alumno_id, nota_final, created_at, updated_at) VALUES (:id, :tid, :eid, :uid, 'Aprobado - 7', NOW(), NOW())"
            ),
            {"id": uuid.uuid4(), "tid": tid, "eid": eval2_id, "uid": alumno_uid},
        )

        # ── 10. Avisos ────────────────────────────────────────────────────────
        aviso1_id = uuid.uuid4()
        aviso2_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO aviso (id, tenant_id, alcance, severidad, titulo, cuerpo, inicio_en, fin_en, requiere_ack, activo, created_at, updated_at) "
                "VALUES (:id, :tid, 'GLOBAL', 'INFO', :titulo, :cuerpo, '2026-03-01 00:00:00+00', '2026-04-01 00:00:00+00', false, true, NOW(), NOW())"
            ),
            {
                "id": aviso1_id,
                "tid": tid,
                "titulo": "Inicio de cursada 2026 — Primer cuatrimestre",
                "cuerpo": "Les comunicamos que la cursada del primer cuatrimestre 2026 comenzará el 3 de marzo. Revisá tu plan de estudios y el calendario académico.",
            },
        )
        await session.execute(
            text(
                "INSERT INTO aviso (id, tenant_id, alcance, cohorte_id, severidad, titulo, cuerpo, inicio_en, fin_en, requiere_ack, activo, created_at, updated_at) "
                "VALUES (:id, :tid, 'POR_COHORTE', :coid, 'ADVERTENCIA', :titulo, :cuerpo, '2026-05-01 00:00:00+00', '2026-06-30 00:00:00+00', true, true, NOW(), NOW())"
            ),
            {
                "id": aviso2_id,
                "tid": tid,
                "coid": cohorte_id,
                "titulo": "Requisitos para rendir coloquio — cohorte 2024",
                "cuerpo": "Recordamos que para acceder al coloquio final es necesario tener aprobados todos los TPs y ambos parciales (o recuperatorio). Verificá tu situación académica.",
            },
        )
        # Alumno confirma el aviso con ack
        await session.execute(
            text(
                "INSERT INTO acknowledgment_aviso (id, tenant_id, aviso_id, usuario_id, created_at, updated_at) VALUES (:id, :tid, :aid, :uid, NOW(), NOW())"
            ),
            {"id": uuid.uuid4(), "tid": tid, "aid": aviso2_id, "uid": alumno_uid},
        )

        # ── 11. Tareas ────────────────────────────────────────────────────────
        for descripcion, estado, asignado_a, materia_id in [
            (
                "Cargar calificaciones del TP 3 — Programación I antes del 25/05",
                "PENDIENTE",
                profesor_uid,
                materia1_id,
            ),
            (
                "Actualizar programa de Bases de Datos para el próximo cuatrimestre",
                "EN_PROGRESO",
                profesor_uid,
                materia2_id,
            ),
            (
                "Revisar y aprobar el listado de alumnos habilitados para coloquio",
                "RESUELTA",
                coordinador_uid,
                None,
            ),
        ]:
            await session.execute(
                text(
                    "INSERT INTO tarea (id, tenant_id, materia_id, asignado_a, asignado_por, descripcion, estado, created_at, updated_at) "
                    "VALUES (:id, :tid, :mid, :aa, :ap, :desc, :estado, NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "mid": materia_id,
                    "aa": asignado_a,
                    "ap": coordinador_uid,
                    "desc": descripcion,
                    "estado": estado,
                },
            )

        # ── 12. Mensajería interna ────────────────────────────────────────────
        # Hilo 1: Coordinador ↔ Profesor (existente)
        hilo_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO hilo_conversacion (id, tenant_id, asunto, created_at, updated_at) VALUES (:id, :tid, :asunto, NOW(), NOW())"
            ),
            {"id": hilo_id, "tid": tid, "asunto": "Novedades TP 3 — Programación I"},
        )
        for uid in [coordinador_uid, profesor_uid]:
            await session.execute(
                text(
                    "INSERT INTO hilo_participante (hilo_id, usuario_id) VALUES (:hid, :uid)"
                ),
                {"hid": hilo_id, "uid": uid},
            )
        for remitente_id, contenido in [
            (
                coordinador_uid,
                "Hola Carlos, ¿cómo van las notas del TP 3? Necesito el informe antes del viernes para cerrar el período.",
            ),
            (
                profesor_uid,
                "Hola, estoy terminando de cargarlas. Tengo 2 alumnos que entregaron tarde, ¿los incluyo igual o los marco como ausentes?",
            ),
        ]:
            await session.execute(
                text(
                    "INSERT INTO mensaje (id, tenant_id, hilo_id, remitente_id, contenido, created_at, updated_at) VALUES (:id, :tid, :hid, :rem, :cont, NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "hid": hilo_id,
                    "rem": remitente_id,
                    "cont": contenido,
                },
            )
        # Hilo 2: Coordinador ↔ Tutor ↔ Alumno (consulta académica)
        hilo2_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO hilo_conversacion (id, tenant_id, asunto, created_at, updated_at) VALUES (:id, :tid, :asunto, NOW(), NOW())"
            ),
            {
                "id": hilo2_id,
                "tid": tid,
                "asunto": "Consulta sobre correlativas — Programación I",
            },
        )
        for uid in [coordinador_uid, tutor_uid, alumno_uid]:
            await session.execute(
                text(
                    "INSERT INTO hilo_participante (hilo_id, usuario_id) VALUES (:hid, :uid)"
                ),
                {"hid": hilo2_id, "uid": uid},
            )
        for remitente_id, contenido in [
            (
                alumno_uid,
                "Buenos días, quería saber si con la regularidad de Programación I puedo cursar Bases de Datos este cuatrimestre o necesito tenerla aprobada.",
            ),
            (
                tutor_uid,
                "Hola María, con la regularidad es suficiente. La correlativa pide 'regularizada' para cursar, no aprobada.",
            ),
            (alumno_uid, "Perfecto, ¡muchas gracias!"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO mensaje (id, tenant_id, hilo_id, remitente_id, contenido, created_at, updated_at) VALUES (:id, :tid, :hid, :rem, :cont, NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "hid": hilo2_id,
                    "rem": remitente_id,
                    "cont": contenido,
                },
            )

        # ── 13. Grilla salarial ───────────────────────────────────────────────
        # salario_base por rol (vigente desde 2025-01-01)
        for rol, monto in [
            ("PROFESOR", 650000),
            ("TUTOR", 420000),
            ("COORDINADOR", 820000),
        ]:
            await session.execute(
                text(
                    "INSERT INTO salario_base (id, tenant_id, rol, monto, desde, created_at, updated_at) VALUES (:id, :tid, :rol, :monto, '2025-01-01', NOW(), NOW())"
                ),
                {"id": uuid.uuid4(), "tid": tid, "rol": rol, "monto": monto},
            )

        # salario_plus — adicionales por grupo y rol
        for grupo, rol, desc, monto in [
            ("Antigüedad", "PROFESOR", "Plus por antigüedad (más de 5 años)", 75000),
            ("Antigüedad", "TUTOR", "Plus por antigüedad (más de 5 años)", 48000),
            ("Título", "PROFESOR", "Plus por título universitario de posgrado", 55000),
            (
                "Título",
                "COORDINADOR",
                "Plus por título universitario de posgrado",
                80000,
            ),
            ("Zona", "PROFESOR", "Plus por zona geográfica", 30000),
            ("Zona", "TUTOR", "Plus por zona geográfica", 25000),
        ]:
            await session.execute(
                text(
                    "INSERT INTO salario_plus (id, tenant_id, grupo, rol, descripcion, monto, desde, created_at, updated_at) VALUES (:id, :tid, :grupo, :rol, :desc, :monto, '2025-01-01', NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "grupo": grupo,
                    "rol": rol,
                    "desc": desc,
                    "monto": monto,
                },
            )

        # clave_plus — categorías especiales por materia
        cplus1_id = uuid.uuid4()
        cplus2_id = uuid.uuid4()
        for cp_id, codigo, desc in [
            (cplus1_id, "CPROG", "Programación (plus curricular especial)"),
            (cplus2_id, "CBDATOS", "Bases de Datos (plus curricular especial)"),
        ]:
            await session.execute(
                text(
                    "INSERT INTO clave_plus (id, tenant_id, codigo, descripcion, desde, created_at, updated_at) VALUES (:id, :tid, :cod, :desc, '2025-01-01', NOW(), NOW())"
                ),
                {"id": cp_id, "tid": tid, "cod": codigo, "desc": desc},
            )

        # materia_clave_plus — asignación de clave a materia
        for mid, cp_id in [(materia1_id, cplus1_id), (materia2_id, cplus2_id)]:
            await session.execute(
                text(
                    "INSERT INTO materia_clave_plus (id, tenant_id, materia_id, clave_plus_id, desde, created_at, updated_at) VALUES (:id, :tid, :mid, :cpid, '2025-01-01', NOW(), NOW())"
                ),
                {"id": uuid.uuid4(), "tid": tid, "mid": mid, "cpid": cp_id},
            )

        # ── 14. Liquidaciones y facturas ─────────────────────────────────────
        # Profesor: base $650k + antigüedad $75k + título $55k = $780k
        # Tutor:    base $420k + antigüedad $48k = $468k
        liq1_id = uuid.uuid4()
        liq2_id = uuid.uuid4()
        for liq_id, uid, rol, base, plus, total in [
            (liq1_id, profesor_uid, "PROFESOR", 650000, 130000, 780000),
            (liq2_id, tutor_uid, "TUTOR", 420000, 48000, 468000),
        ]:
            await session.execute(
                text(
                    "INSERT INTO liquidacion (id, tenant_id, cohorte_id, periodo, usuario_id, rol, comisiones, monto_base, monto_plus, total, estado, created_at, updated_at) "
                    "VALUES (:id, :tid, :coid, '2026-06', :uid, :rol, 'A', :base, :plus, :total, 'Abierta', NOW(), NOW())"
                ),
                {
                    "id": liq_id,
                    "tid": tid,
                    "coid": cohorte_id,
                    "uid": uid,
                    "rol": rol,
                    "base": base,
                    "plus": plus,
                    "total": total,
                },
            )

        # Factura del profesor (facturador=True)
        await session.execute(
            text(
                "INSERT INTO factura (id, tenant_id, usuario_id, periodo, detalle, estado, created_at, updated_at) "
                "VALUES (:id, :tid, :uid, '2026-06', :det, 'Pendiente', NOW(), NOW())"
            ),
            {
                "id": uuid.uuid4(),
                "tid": tid,
                "uid": profesor_uid,
                "det": "Honorarios junio 2026 — Programación I y Bases de Datos (ING-SIS cohorte 2024)",
            },
        )

        # ── 15. Roles / permisos / rol_permiso ───────────────────────────────
        for codigo, nombre, descripcion in _ROLES:
            await session.execute(
                text(
                    "INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at) VALUES (gen_random_uuid(), :tid, :cod, :nom, :desc, NOW(), NOW()) ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING"
                ),
                {"tid": tid, "cod": codigo, "nom": nombre, "desc": descripcion},
            )
        for codigo, nombre_desc, modulo in _PERMISOS:
            await session.execute(
                text(
                    "INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at) VALUES (gen_random_uuid(), :tid, :cod, :nom, :desc, :mod, NOW(), NOW()) ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING"
                ),
                {
                    "tid": tid,
                    "cod": codigo,
                    "nom": nombre_desc,
                    "desc": nombre_desc,
                    "mod": modulo,
                },
            )
        for rc, pc, es_propio in _MATRIX:
            await session.execute(
                text(
                    "INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at) "
                    "SELECT gen_random_uuid(), :tid, r.id, p.id, :ep, NOW(), NOW() "
                    "FROM rol r, permiso p "
                    "WHERE r.tenant_id = :tid AND r.codigo = :rc AND r.deleted_at IS NULL "
                    "  AND p.tenant_id = :tid AND p.codigo = :pc AND p.deleted_at IS NULL "
                    "ON CONFLICT (tenant_id, rol_id, permiso_id) DO NOTHING"
                ),
                {"tid": tid, "rc": rc, "pc": pc, "ep": es_propio},
            )

        # ── 16. Comunicaciones (registro de mensajería externa) ──────────────
        encryption_key = get_encryption_key()
        alumno_email_enc = encrypt_value("alumno@demo.com", encryption_key)
        alumno_hash = hashlib.sha256(b"alumno@demo.com").hexdigest()
        for com_asunto, com_cuerpo in [
            (
                "Bienvenida al cuatrimestre 2026 — Primer cuatrimestre",
                "Te damos la bienvenida al primer cuatrimestre de 2026. Recordá revisar el calendario académico y las fechas de parciales en tu dashboard.",
            ),
            (
                "Recordatorio: Inscripción a coloquios",
                "Las inscripciones para los coloquios de Programación I y Bases de Datos cierran el 30 de junio. "
                "Si estás en condiciones, no olvides reservar tu turno desde la sección de Coloquios.",
            ),
        ]:
            lote_id = uuid.uuid4()
            await session.execute(
                text(
                    "INSERT INTO comunicacion (id, tenant_id, enviado_por, materia_id, asunto, cuerpo, "
                    "lote_id, destinatario_hash, destinatario, estado, created_at, updated_at) "
                    "VALUES (:id, :tid, :eid, :mid, :asunto, :cuerpo, :lid, :dhash, :denc, 'Enviado', NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "tid": tid,
                    "lid": lote_id,
                    "eid": coordinador_uid,
                    "mid": materia1_id,
                    "asunto": com_asunto,
                    "cuerpo": com_cuerpo,
                    "dhash": alumno_hash,
                    "denc": alumno_email_enc,
                },
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
        print("║  Carrera: Ingeniería en Sistemas (ING-SIS) — Cohorte 2024  ║")
        print("║  Materias: PROG1 · BDATOS  |  Alumno: María García         ║")
        print("║  Grilla: PROFESOR $780k · TUTOR $468k (base + plus)        ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
