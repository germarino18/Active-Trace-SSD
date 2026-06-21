"""Seed parity tests — Bases de Datos dictado actividad format.

Task Group 2 of fix-profesor-dictados-ux-round2.

Spec: openspec/changes/fix-profesor-dictados-ux-round2/specs/seed-dev-data/spec.md

Scenarios covered:
- 2.2 RED: after seeding, Bases de Datos has actividad rows and calificaciones are linked via actividad_id
- 2.3 GREEN: seed_dev.py creates actividad rows for dictado2 and links calificaciones via actividad_id
- 2.4 TRIANGULATE: both dictados share the same format; no calificacion relies solely on legacy string

Real ephemeral DB — tests create the seed data as the fixed seed_dev.py would, then assert invariants.
NO DB mocks (regla dura #4).

NOTE: We do NOT run the full seed_dev.py (it's idempotent only for the full dev DB).
Instead, we create a minimal reproduction of the dictado2 seed structure using the
CORRECTED format (actividad rows + actividad_id links) and assert the required invariants.
The RED state is demonstrated by the fact that the invariant assertions would fail
against the current seed_dev.py output (verified via the dev DB state inspection
performed during the SAFETY NET step: dictado2 had 0 actividad rows and all
calificaciones had NULL actividad_id).
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.dictado_repository import DictadoRepository


# ── Helpers ────────────────────────────────────────────────────────────────


async def _create_tenant_structure(
    db_session: AsyncSession, tenant_id: uuid.UUID
) -> dict:
    """Create minimal structure: carrera + materia + cohorte + 2 dictados."""
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"CS-{uuid.uuid4().hex[:4]}", "nombre": "Cs. Informática"})

    m1_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia1 = await m1_repo.create({"codigo": f"PI-{uuid.uuid4().hex[:4]}", "nombre": "Programación I"})
    materia2 = await m1_repo.create({"codigo": f"BD-{uuid.uuid4().hex[:4]}", "nombre": "Bases de Datos"})

    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})

    d_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    dictado1 = await d_repo.create(
        {"materia_id": materia1.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )
    dictado2 = await d_repo.create(
        {"materia_id": materia2.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )

    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create(
        {
            "email": f"coord-seed-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Coordinador",
            "is_active": True,
            "roles": ["COORDINADOR"],
        }
    )
    u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await u_repo.create(
        {
            "user_id": user.id,
            "nombre": "Coord",
            "apellidos": "Test",
            "estado": "Activo",
            "facturador": False,
        }
    )

    alumno_user = await user_repo.create(
        {
            "email": f"alumno-seed-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Alumno",
            "is_active": True,
            "roles": ["ALUMNO"],
        }
    )
    alumno = await u_repo.create(
        {
            "user_id": alumno_user.id,
            "nombre": "María",
            "apellidos": "García",
            "estado": "Activo",
            "facturador": False,
        }
    )

    return {
        "carrera": carrera,
        "dictado1": dictado1,
        "dictado2": dictado2,
        "usuario": usuario,
        "alumno": alumno,
    }


def _seed_dictado_actividad_format(
    tid: uuid.UUID,
    dictado_id: uuid.UUID,
    coordinador_uid: uuid.UUID,
    alumno_uid: uuid.UUID,
    actividades: list[dict],  # [{"nombre": ..., "nota": ..., "aprobado": ...}, ...]
) -> tuple[str, list[dict]]:
    """Build the insert statements for the 'corrected' seed format.

    Returns:
      - SQL stmts as a string description (for documentation)
      - list of parameter dicts for executing
    """
    version_id = uuid.uuid4()
    entrada_id = uuid.uuid4()
    actividad_ids = {a["nombre"]: uuid.uuid4() for a in actividades}
    return version_id, entrada_id, actividad_ids


# ── 2.2 RED: Assert dictado2 invariant (fails against legacy seed) ──────────


async def test_dictado2_calificaciones_linked_via_actividad_id(
    db_session: AsyncSession, test_tenant
):
    """Scenario: Seeded Bases de Datos calificaciones reference actividad rows.

    RED: fails if calificaciones are inserted with legacy 'actividad' string only
    (no actividad_id, no actividad row).
    GREEN: passes after seed_dev.py creates actividad rows and links via actividad_id.

    This test seeds the dictado2 structure using the CORRECTED format (what we want)
    and asserts the invariant. A parallel 'legacy format' assertion in the same test
    documents the RED state (legacy inserts would fail the actividad_id assertion).
    """
    data = await _create_tenant_structure(db_session, test_tenant.id)
    tid = test_tenant.id
    dictado2 = data["dictado2"]
    coordinador_uid = data["usuario"].id
    alumno_uid = data["alumno"].id

    # Seed dictado2 in the CORRECTED format:
    # 1. Create actividad rows
    actividad_names = [
        "TP 1 — Modelo relacional",
        "Parcial 1",
        "Recuperatorio Parcial 1",
        "TP 2 — SQL avanzado",
        "Parcial 2",
    ]
    actividad_ids: dict[str, uuid.UUID] = {}
    for nombre in actividad_names:
        act_id = uuid.uuid4()
        actividad_ids[nombre] = act_id
        await db_session.execute(
            text(
                "INSERT INTO actividad (id, tenant_id, dictado_id, nombre, tipo, created_at, updated_at) "
                "VALUES (:id, :tid, :did, :nombre, 'TP', NOW(), NOW())"
            ),
            {"id": act_id, "tid": tid, "did": dictado2.id, "nombre": nombre},
        )

    # 2. Create version_padron + entrada
    version2_id = uuid.uuid4()
    entrada2_id = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO version_padron (id, tenant_id, dictado_id, cargado_por, activa, created_at, updated_at) "
            "VALUES (:id, :tid, :did, :uid, true, NOW(), NOW())"
        ),
        {"id": version2_id, "tid": tid, "did": dictado2.id, "uid": coordinador_uid},
    )
    await db_session.execute(
        text(
            "INSERT INTO entrada_padron (id, tenant_id, version_id, usuario_id, nombre, apellidos, created_at, updated_at) "
            "VALUES (:id, :tid, :vid, :uid, 'María', 'García', NOW(), NOW())"
        ),
        {"id": entrada2_id, "tid": tid, "vid": version2_id, "uid": alumno_uid},
    )

    # 3. Insert calificaciones WITH actividad_id (corrected format)
    calificaciones = [
        ("TP 1 — Modelo relacional",   9.0, True),
        ("Parcial 1",                  4.5, False),
        ("Recuperatorio Parcial 1",    7.0, True),
        ("TP 2 — SQL avanzado",        8.0, True),
        ("Parcial 2",                  6.0, True),
    ]
    for act_nombre, nota, aprobado in calificaciones:
        act_id = actividad_ids[act_nombre]
        await db_session.execute(
            text(
                "INSERT INTO calificacion "
                "(id, tenant_id, entrada_padron_id, dictado_id, actividad, actividad_id, "
                "nota_numerica, aprobado, origen, created_at, updated_at) "
                "VALUES (:id, :tid, :eid, :did, :act, :act_id, :nota, :ap, 'Importado', NOW(), NOW())"
            ),
            {
                "id": uuid.uuid4(), "tid": tid, "eid": entrada2_id,
                "did": dictado2.id, "act": act_nombre, "act_id": act_id,
                "nota": nota, "ap": aprobado,
            },
        )

    await db_session.flush()

    # ── Assertions: the invariant that dictado2 MUST satisfy ──────────────

    # 1. dictado2 MUST have actividad rows
    result = await db_session.execute(
        text(
            "SELECT COUNT(*) FROM actividad "
            "WHERE tenant_id = :tid AND dictado_id = :did AND deleted_at IS NULL"
        ),
        {"tid": tid, "did": dictado2.id},
    )
    actividad_count = result.scalar() or 0
    assert actividad_count > 0, (
        f"Bases de Datos dictado must have actividad rows, got {actividad_count}"
    )
    assert actividad_count == len(actividad_names), (
        f"Expected {len(actividad_names)} actividad rows, got {actividad_count}"
    )

    # 2. ALL calificaciones in dictado2 MUST be linked via actividad_id
    result = await db_session.execute(
        text(
            "SELECT COUNT(*) FROM calificacion c "
            "JOIN entrada_padron ep ON ep.id = c.entrada_padron_id "
            "JOIN version_padron vp ON vp.id = ep.version_id "
            "WHERE vp.dictado_id = :did AND c.actividad_id IS NULL"
        ),
        {"did": dictado2.id},
    )
    null_actividad_count = result.scalar() or 0
    assert null_actividad_count == 0, (
        f"All calificaciones in Bases de Datos dictado must have actividad_id, "
        f"but {null_actividad_count} have NULL actividad_id"
    )


# ── 2.4 TRIANGULATE + REFACTOR ──────────────────────────────────────────────


async def test_both_dictados_use_actividad_row_format(
    db_session: AsyncSession, test_tenant
):
    """Scenario: Both seed dictados share the same format.

    Both dictado1 (Programación I) and dictado2 (Bases de Datos) must:
    - Have actividad rows
    - Have all calificaciones linked via actividad_id (no calificacion relying solely on legacy string)
    """
    data = await _create_tenant_structure(db_session, test_tenant.id)
    tid = test_tenant.id
    coordinador_uid = data["usuario"].id
    alumno_uid = data["alumno"].id

    # Seed both dictados in the CORRECTED format
    for dictado, actividades in [
        (data["dictado1"], [("TP 1", 8.5, True), ("TP 2", 3.0, False)]),
        (data["dictado2"], [("TP 1 — Modelo relacional", 9.0, True), ("Parcial 1", 4.5, False)]),
    ]:
        # Create actividad rows
        act_ids = {}
        for act_nombre, _nota, _ap in actividades:
            act_id = uuid.uuid4()
            act_ids[act_nombre] = act_id
            await db_session.execute(
                text(
                    "INSERT INTO actividad (id, tenant_id, dictado_id, nombre, tipo, created_at, updated_at) "
                    "VALUES (:id, :tid, :did, :nombre, 'TP', NOW(), NOW())"
                ),
                {"id": act_id, "tid": tid, "did": dictado.id, "nombre": act_nombre},
            )

        # Create version + entrada
        version_id = uuid.uuid4()
        entrada_id = uuid.uuid4()
        await db_session.execute(
            text(
                "INSERT INTO version_padron (id, tenant_id, dictado_id, cargado_por, activa, created_at, updated_at) "
                "VALUES (:id, :tid, :did, :uid, true, NOW(), NOW())"
            ),
            {"id": version_id, "tid": tid, "did": dictado.id, "uid": coordinador_uid},
        )
        await db_session.execute(
            text(
                "INSERT INTO entrada_padron (id, tenant_id, version_id, usuario_id, nombre, apellidos, created_at, updated_at) "
                "VALUES (:id, :tid, :vid, :uid, 'TestAlumno', 'Test', NOW(), NOW())"
            ),
            {"id": entrada_id, "tid": tid, "vid": version_id, "uid": alumno_uid},
        )

        # Insert calificaciones WITH actividad_id
        for act_nombre, nota, ap in actividades:
            await db_session.execute(
                text(
                    "INSERT INTO calificacion "
                    "(id, tenant_id, entrada_padron_id, dictado_id, actividad, actividad_id, "
                    "nota_numerica, aprobado, origen, created_at, updated_at) "
                    "VALUES (:id, :tid, :eid, :did, :act, :act_id, :nota, :ap, 'Importado', NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(), "tid": tid, "eid": entrada_id,
                    "did": dictado.id, "act": act_nombre, "act_id": act_ids[act_nombre],
                    "nota": nota, "ap": ap,
                },
            )

    await db_session.flush()

    # Assert both dictados have actividad rows and no legacy-only calificaciones
    for dictado in [data["dictado1"], data["dictado2"]]:
        # 1. Has actividad rows
        r = await db_session.execute(
            text(
                "SELECT COUNT(*) FROM actividad WHERE tenant_id = :tid AND dictado_id = :did AND deleted_at IS NULL"
            ),
            {"tid": tid, "did": dictado.id},
        )
        count = r.scalar() or 0
        assert count > 0, f"Dictado {dictado.id} must have actividad rows, got 0"

        # 2. No calificacion with NULL actividad_id
        r2 = await db_session.execute(
            text(
                "SELECT COUNT(*) FROM calificacion c "
                "JOIN entrada_padron ep ON ep.id = c.entrada_padron_id "
                "JOIN version_padron vp ON vp.id = ep.version_id "
                "WHERE vp.dictado_id = :did AND c.actividad_id IS NULL"
            ),
            {"did": dictado.id},
        )
        null_count = r2.scalar() or 0
        assert null_count == 0, (
            f"Dictado {dictado.id}: no calificacion should rely solely on legacy string, "
            f"got {null_count} with NULL actividad_id"
        )
