"""Router tests for `/api/equipos` (C-08 task groups 4-5).

`mis-equipos` (F4.2) is session-only -- no `equipos:asignar` guard, scoped
EXCLUSIVAMENTE a `current_user` (D3 [SEC], regla dura #8). Coordination
endpoints (F4.3-F4.7) require `equipos:asignar`, fail-closed (D3 [SEC]).
Block operations (masiva, clonado, vigencia) are transactional -- a single
`await db.commit()` -- and emit exactly ONE `ASIGNACION_MODIFICAR` (D6/D7).
Read operations (mis-equipos, listado, export) do NOT audit.
"""

import datetime
import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.models.asignacion import Asignacion
from app.models.cohorte import Cohorte
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.base import BaseRepository
from tests.helpers import cleanup_permission_cache
from tests.test_equipos.conftest import make_token, make_usuario_perfil

_HOY = datetime.date.today()


async def _make_asignacion(
    db_session, tenant_id, usuario_id, rol, *, materia_id=None, carrera_id=None,
    cohorte_id=None, desde, hasta=None, responsable_id=None, comisiones=None,
):
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    data = {
        "usuario_id": usuario_id,
        "rol": rol,
        "materia_id": materia_id,
        "carrera_id": carrera_id,
        "cohorte_id": cohorte_id,
        "desde": desde,
        "hasta": hasta,
        "responsable_id": responsable_id,
    }
    if comisiones is not None:
        data["comisiones"] = comisiones
    return await repo.create(data)


async def _make_academic_context(db_session, tenant_id, suffix):
    from app.models.carrera import Carrera
    from app.models.materia import Materia

    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)

    materia = await materia_repo.create({"codigo": f"MAT-{suffix}", "nombre": f"Materia {suffix}"})
    carrera = await carrera_repo.create({"codigo": f"CAR-{suffix}", "nombre": f"Carrera {suffix}"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": f"2026-{suffix}"})
    return materia, carrera, cohorte


# ── 4.1/4.2: GET /api/equipos/mis-equipos ────────────────────────────────


async def test_mis_equipos_with_valid_session_returns_only_own_asignaciones(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, plain_user, admin_user
):
    cleanup_permission_cache()
    usuario_propio = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Propio", "User")
    usuario_otro = await make_usuario_perfil(db_session, seeded_tenant.id, admin_user.id, "Otro", "User")

    await _make_asignacion(
        db_session, seeded_tenant.id, usuario_propio.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario_otro.id, "TUTOR",
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()

    token = make_token(plain_user)
    response = await client.get(
        "/api/equipos/mis-equipos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["usuario_id"] == str(usuario_propio.id)
    assert body[0]["rol"] == "PROFESOR"
    assert body[0]["estado_vigencia"] == "Vigente"


async def test_mis_equipos_without_session_returns_401(client: AsyncClient):
    response = await client.get("/api/equipos/mis-equipos")
    assert response.status_code == 401


async def test_mis_equipos_filters_by_materia_id_query_param(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Filt", "Filt")
    materia_a, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "MEFA")
    materia_b, _, _ = await _make_academic_context(db_session, seeded_tenant.id, "MEFB")

    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia_a.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "TUTOR",
        materia_id=materia_b.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()

    token = make_token(plain_user)
    response = await client.get(
        "/api/equipos/mis-equipos",
        params={"materia_id": str(materia_a.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["materia_id"] == str(materia_a.id)
    assert body[0]["rol"] == "PROFESOR"


# ── 4.3 RED+GREEN: coordination endpoints require equipos:asignar ───────


async def test_listar_equipos_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.get(
        "/api/equipos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_listar_equipos_with_permission_returns_tenant_scoped(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Lista", "Test")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "LSTR")

    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.get(
        "/api/equipos",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["usuario_id"] == str(usuario.id)


async def test_buscar_docentes_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.get(
        "/api/equipos/docentes",
        params={"q": "Ana"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_buscar_docentes_with_permission_returns_matches(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Ana", "Perez")
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.get(
        "/api/equipos/docentes",
        params={"q": "Ana"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert any(d["nombre"] == "Ana" for d in body)


async def test_asignacion_masiva_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "M", "M")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "MAS403")
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.post(
        "/api/equipos/asignacion-masiva",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_ids": [str(usuario.id)],
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "rol": "PROFESOR",
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 403


async def test_asignacion_masiva_with_permission_executes_scoped_to_tenant(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "M2", "M2")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "MAS200")
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.post(
        "/api/equipos/asignacion-masiva",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_ids": [str(usuario.id)],
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "rol": "PROFESOR",
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["creadas"] == [str(usuario.id)]
    assert body["filas_afectadas"] == 1

    rows = await AsignacionRepositoryFor(db_session, seeded_tenant.id).find_equipo(
        seeded_tenant.id, materia.id, carrera.id, cohorte.id
    )
    assert len(rows) == 1
    assert rows[0].usuario_id == usuario.id


async def test_clonar_equipo_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, seeded_tenant.id, "CLO403")
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=seeded_tenant.id)
    cohorte_destino = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "CLO403-DEST"})
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.post(
        "/api/equipos/clonar",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_origen_id": str(cohorte_origen.id),
            "cohorte_destino_id": str(cohorte_destino.id),
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 403


async def test_clonar_equipo_with_permission_clones_vigentes(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "CL", "CL")
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, seeded_tenant.id, "CLO200")
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=seeded_tenant.id)
    cohorte_destino = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "CLO200-DEST"})

    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.post(
        "/api/equipos/clonar",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_origen_id": str(cohorte_origen.id),
            "cohorte_destino_id": str(cohorte_destino.id),
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filas_afectadas"] == 1

    rows = await AsignacionRepositoryFor(db_session, seeded_tenant.id).find_equipo(
        seeded_tenant.id, materia.id, carrera.id, cohorte_destino.id
    )
    assert len(rows) == 1


async def test_modificar_vigencia_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "VIG403")
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.patch(
        "/api/equipos/vigencia",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "hasta": str(_HOY + datetime.timedelta(days=365)),
        },
    )
    assert response.status_code == 403


async def test_modificar_vigencia_with_permission_updates_equipo(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "VG", "VG")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "VIG200")

    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=100),
    )
    await db_session.commit()
    token = make_token(admin_user)

    nueva_hasta = _HOY + datetime.timedelta(days=365)
    response = await client.patch(
        "/api/equipos/vigencia",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "hasta": str(nueva_hasta),
        },
    )
    assert response.status_code == 200
    assert response.json()["filas_afectadas"] == 1

    rows = await AsignacionRepositoryFor(db_session, seeded_tenant.id).find_equipo(
        seeded_tenant.id, materia.id, carrera.id, cohorte.id
    )
    assert rows[0].hasta == nueva_hasta


# ── 4.4 RED+GREEN: validation failure leaves no partial commit ──────────


async def test_asignacion_masiva_validation_failure_leaves_no_partial_commit(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant, admin_user, plain_user, another_tenant_admin
):
    cleanup_permission_cache()
    usuario_propio = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "OK", "OK")
    usuario_ajeno = await make_usuario_perfil(db_session, another_tenant.id, another_tenant_admin.id, "X", "X")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "PARCIAL")
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.post(
        "/api/equipos/asignacion-masiva",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_ids": [str(usuario_propio.id), str(usuario_ajeno.id)],
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "rol": "PROFESOR",
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 404

    # Nothing committed: usuario_propio has no asignacion in this context.
    rows = await AsignacionRepositoryFor(db_session, seeded_tenant.id).find_equipo(
        seeded_tenant.id, materia.id, carrera.id, cohorte.id
    )
    assert rows == []

    audit_repo = AuditLogRepository(session=db_session, tenant_id=seeded_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert logs == []


# ── 4.5 GREEN: export returns text/csv with attachment ──────────────────


async def test_export_equipo_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "EXP403")
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.get(
        "/api/equipos/export",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_export_equipo_returns_csv_with_attachment_and_one_row_per_asignacion(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario_a = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Ana", "Perez")
    usuario_b = await make_usuario_perfil(db_session, seeded_tenant.id, admin_user.id, "Beto", "Gomez")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "EXP200")

    await _make_asignacion(
        db_session, seeded_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario_b.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()
    token = make_token(admin_user)

    response = await client.get(
        "/api/equipos/export",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]

    lines = response.text.strip().splitlines()
    # Header + one row per asignacion.
    assert len(lines) == 1 + 2


# ── 5.1 RED+GREEN: tenant isolation ──────────────────────────────────────


async def test_listar_equipos_other_tenant_does_not_leak_rows(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant,
    admin_user, another_tenant_admin, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Iso", "Iso")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "ISO1")
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()

    # Coordinator from another tenant.
    token_b = make_token(another_tenant_admin)

    response = await client.get(
        "/api/equipos",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_export_equipo_from_other_tenant_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant,
    admin_user, another_tenant_admin, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Iso2", "Iso2")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "ISO2")
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()

    token_b = make_token(another_tenant_admin)

    response = await client.get(
        "/api/equipos/export",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404


async def test_asignacion_masiva_to_other_tenant_context_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant,
    admin_user, another_tenant_admin, plain_user
):
    cleanup_permission_cache()
    usuario_a = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "IsoA", "IsoA")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "ISO3")
    await db_session.commit()

    token_b = make_token(another_tenant_admin)

    response = await client.post(
        "/api/equipos/asignacion-masiva",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "usuario_ids": [str(usuario_a.id)],
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "rol": "PROFESOR",
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 404


async def test_clonar_equipo_to_other_tenant_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant,
    admin_user, another_tenant_admin, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "IsoB", "IsoB")
    materia, carrera, cohorte_origen = await _make_academic_context(db_session, seeded_tenant.id, "ISO4")
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_origen.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()

    token_b = make_token(another_tenant_admin)
    cohorte_repo_b = BaseRepository(model=Cohorte, session=db_session, tenant_id=another_tenant.id)
    cohorte_destino_b = await cohorte_repo_b.create({"carrera_id": carrera.id, "nombre": "ISO4-DEST-B"})
    await db_session.commit()

    response = await client.post(
        "/api/equipos/clonar",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_origen_id": str(cohorte_origen.id),
            "cohorte_destino_id": str(cohorte_destino_b.id),
            "desde": str(_HOY),
        },
    )
    assert response.status_code == 404


async def test_mis_equipos_never_crosses_tenants(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant,
    plain_user, another_tenant_admin
):
    """A docente with the same `usuario.id` linked across both tenants only
    sees their own-tenant asignaciones via mis-equipos (D3/D4 [SEC])."""
    cleanup_permission_cache()
    usuario_a = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Cross", "A")
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario_a.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    # Same auth user id, but a Usuario perfil + asignacion in another tenant.
    usuario_b = await make_usuario_perfil(db_session, another_tenant.id, another_tenant_admin.id, "Cross", "B")
    await _make_asignacion(
        db_session, another_tenant.id, usuario_b.id, "TUTOR",
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()

    token = make_token(plain_user)
    response = await client.get(
        "/api/equipos/mis-equipos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["rol"] == "PROFESOR"


# ── 5.2 RED+GREEN: audit counts ──────────────────────────────────────────


async def test_block_operations_each_emit_exactly_one_audit_event(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario_a = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Aud", "A")
    usuario_b = await make_usuario_perfil(db_session, admin_user.tenant_id, admin_user.id, "Aud", "B")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "AUDIT1")
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=seeded_tenant.id)
    cohorte_destino = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "AUDIT1-DEST"})
    await db_session.commit()
    token = make_token(admin_user)

    # 1) Asignacion masiva -> ASIGNACION_MODIFICAR x1
    masiva_resp = await client.post(
        "/api/equipos/asignacion-masiva",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_ids": [str(usuario_a.id)],
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "rol": "PROFESOR",
            "desde": str(_HOY),
        },
    )
    assert masiva_resp.status_code == 200

    # 2) Clonado -> ASIGNACION_MODIFICAR x1 (total 2)
    clonar_resp = await client.post(
        "/api/equipos/clonar",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_origen_id": str(cohorte.id),
            "cohorte_destino_id": str(cohorte_destino.id),
            "desde": str(_HOY),
        },
    )
    assert clonar_resp.status_code == 200

    # 3) Vigencia en bloque -> ASIGNACION_MODIFICAR x1 (total 3)
    vigencia_resp = await client.patch(
        "/api/equipos/vigencia",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "materia_id": str(materia.id),
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "hasta": str(_HOY + datetime.timedelta(days=365)),
        },
    )
    assert vigencia_resp.status_code == 200

    audit_repo = AuditLogRepository(session=db_session, tenant_id=seeded_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert len(logs) == 3
    for log in logs:
        assert log.filas_afectadas == 1


async def test_read_operations_do_not_emit_audit_events(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id, "Lect", "Lect")
    materia, carrera, cohorte = await _make_academic_context(db_session, seeded_tenant.id, "AUDIT2")
    await _make_asignacion(
        db_session, seeded_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await db_session.commit()
    token = make_token(admin_user)
    plain_token = make_token(plain_user)

    # mis-equipos (session-only).
    r1 = await client.get("/api/equipos/mis-equipos", headers={"Authorization": f"Bearer {plain_token}"})
    assert r1.status_code == 200

    # listado del tenant.
    r2 = await client.get(
        "/api/equipos",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200

    # export.
    r3 = await client.get(
        "/api/equipos/export",
        params={"materia_id": str(materia.id), "carrera_id": str(carrera.id), "cohorte_id": str(cohorte.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r3.status_code == 200

    audit_repo = AuditLogRepository(session=db_session, tenant_id=seeded_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.ASIGNACION_MODIFICAR)
    assert logs == []


# ── Helper ────────────────────────────────────────────────────────────


def AsignacionRepositoryFor(db_session, tenant_id):
    from app.repositories.asignacion_repository import AsignacionRepository
    return AsignacionRepository(session=db_session, tenant_id=tenant_id)
