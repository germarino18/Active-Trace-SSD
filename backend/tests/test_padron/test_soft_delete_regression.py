"""Regression integration tests — padrón soft-delete read fix.

Task Group 1 of fix-profesor-dictados-ux-round2.

Spec: openspec/changes/fix-profesor-dictados-ux-round2/specs/padron-soft-delete-read/spec.md

Scenarios covered:
- 1.2 RED / 1.3 GREEN: find_by_version excludes soft-deleted entries
- 1.4 TRIANGULATE: count_by_version excludes soft-deleted; tenant isolation
- 1.5 TRIANGULATE: soft-deleted alumno absent from get_atrasados_cross_materia and get_alumnos_clasificados
- 1.6 REFACTOR: active entries unaffected; full suite stays green

Real ephemeral DB — NO DB mocks (regla dura #4).
"""

import datetime as dt
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.actividad import Actividad
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.schemas.auth import CurrentUser
from app.services.profesor_service import ProfesorService


# ── Helpers ────────────────────────────────────────────────────────────────


async def _create_user_and_profile(
    db_session: AsyncSession, tenant_id: uuid.UUID
) -> tuple[User, Usuario]:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create(
        {
            "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Test User",
            "is_active": True,
            "roles": [],
        }
    )
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await usuario_repo.create(
        {
            "user_id": user.id,
            "nombre": "Test",
            "apellidos": "User",
            "estado": "Activo",
        }
    )
    return user, usuario


async def _create_dictado(db_session: AsyncSession, tenant_id: uuid.UUID):
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"C-{uuid.uuid4().hex[:4]}", "nombre": "Ingeniería"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": f"M-{uuid.uuid4().hex[:4]}", "nombre": "Materia Test"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    return await repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )


async def _create_version_with_entries(
    db_session: AsyncSession,
    tenant_id: uuid.UUID,
    dictado_id: uuid.UUID,
    usuario_id: uuid.UUID,
    names: list[str],
):
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create(
        {"dictado_id": dictado_id, "cargado_por": usuario_id, "activa": True}
    )
    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    entries = await ep_repo.bulk_create(
        [
            {
                "version_id": version.id,
                "nombre": name,
                "apellidos": f"Apellido-{name}",
                "email": f"{name.lower()}@test.com",
            }
            for name in names
        ]
    )
    return version, entries


# ── 1.2 / 1.3  find_by_version soft-delete regression ─────────────────────


async def test_find_by_version_excludes_soft_deleted_entry(
    db_session: AsyncSession, test_tenant
):
    """Scenario: Soft-deleted alumno disappears from the padrón list.

    RED: fails before _apply_soft_delete_filter is added.
    GREEN: passes after the one-line fix in find_by_version().
    """
    _user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version, entries = await _create_version_with_entries(
        db_session, test_tenant.id, dictado.id, usuario.id, ["Juan", "Ana"]
    )

    # Soft-delete 'Ana' directly on the ORM instance (mimics baja_alumno_dictado)
    ana_entry = next(e for e in entries if e.nombre == "Ana")
    ana_entry.deleted_at = datetime.now(UTC)
    await db_session.flush()

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    result = await ep_repo.find_by_version(version.id)

    nombres = [e.nombre for e in result]
    assert "Ana" not in nombres, (
        f"Soft-deleted 'Ana' must not appear in find_by_version but got: {nombres}"
    )
    assert "Juan" in nombres, "Active 'Juan' must still appear in find_by_version"
    assert len(result) == 1, f"Expected 1 active entry, got {len(result)}"


# ── 1.4  TRIANGULATE: count_by_version + tenant isolation ─────────────────


async def test_count_by_version_excludes_soft_deleted_entry(
    db_session: AsyncSession, test_tenant
):
    """Scenario: Count reflects the removal.

    count_by_version must NOT count soft-deleted entries.
    """
    _user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version, entries = await _create_version_with_entries(
        db_session, test_tenant.id, dictado.id, usuario.id, ["Alice", "Bob", "Carlos"]
    )

    # Soft-delete 'Bob'
    bob = next(e for e in entries if e.nombre == "Bob")
    bob.deleted_at = datetime.now(UTC)
    await db_session.flush()

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    count = await ep_repo.count_by_version(version.id)

    assert count == 2, f"Expected count 2 (Alice + Carlos), got {count}"


async def test_find_by_version_with_mixed_active_and_deleted(
    db_session: AsyncSession, test_tenant
):
    """Scenario: Non-deleted entries are unaffected.

    When the padrón contains both active and soft-deleted entries,
    find_by_version returns ONLY the active ones.
    """
    _user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version, entries = await _create_version_with_entries(
        db_session, test_tenant.id, dictado.id, usuario.id,
        ["Active1", "Deleted1", "Active2", "Deleted2"]
    )

    # Soft-delete the 'Deleted*' entries
    for entry in entries:
        if entry.nombre.startswith("Deleted"):
            entry.deleted_at = datetime.now(UTC)
    await db_session.flush()

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    result = await ep_repo.find_by_version(version.id)
    nombres = sorted(e.nombre for e in result)

    assert nombres == ["Active1", "Active2"], f"Expected only active entries, got {nombres}"


async def test_other_tenant_entries_never_returned(
    db_session: AsyncSession, test_tenant, another_tenant
):
    """Scenario: Entries belonging to another tenant SHALL never be returned.

    Tenant isolation: repo scoped to test_tenant must not see another_tenant entries.
    """
    _user_a, usuario_a = await _create_user_and_profile(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    version_a, _ = await _create_version_with_entries(
        db_session, test_tenant.id, dictado_a.id, usuario_a.id, ["TenantA-Student"]
    )

    _user_b, usuario_b = await _create_user_and_profile(db_session, another_tenant.id)
    dictado_b = await _create_dictado(db_session, another_tenant.id)
    version_b, _ = await _create_version_with_entries(
        db_session, another_tenant.id, dictado_b.id, usuario_b.id, ["TenantB-Student"]
    )

    # Repo scoped to test_tenant must not return another_tenant entries
    ep_repo_a = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    result = await ep_repo_a.find_by_version(version_b.id)

    assert result == [], (
        f"Tenant A repo must not return Tenant B entries, got {[e.nombre for e in result]}"
    )


async def test_count_by_version_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant
):
    """count_by_version must be scoped to the current tenant."""
    _user_a, usuario_a = await _create_user_and_profile(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    version_a, _ = await _create_version_with_entries(
        db_session, test_tenant.id, dictado_a.id, usuario_a.id,
        ["StudentA1", "StudentA2"]
    )

    _user_b, usuario_b = await _create_user_and_profile(db_session, another_tenant.id)
    dictado_b = await _create_dictado(db_session, another_tenant.id)
    version_b, _ = await _create_version_with_entries(
        db_session, another_tenant.id, dictado_b.id, usuario_b.id,
        ["StudentB1", "StudentB2", "StudentB3"]
    )

    # count_by_version for version_b scoped to test_tenant must return 0
    ep_repo_a = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    count = await ep_repo_a.count_by_version(version_b.id)

    assert count == 0, (
        f"Tenant A repo counting Tenant B version must return 0, got {count}"
    )


# ── 1.5  TRIANGULATE: service-level views exclude soft-deleted alumnos ─────


async def _setup_profesor_with_dictado_and_atrasado(
    db_session: AsyncSession, tenant_id: uuid.UUID
):
    """Set up a full estructura with a PROFESOR assigned to a dictado with one atrasado alumno."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create(
        {
            "email": f"prof-sd-{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "hash",
            "display_name": "Prof SoftDelete",
            "is_active": True,
            "roles": ["PROFESOR"],
        }
    )
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await usuario_repo.create(
        {
            "user_id": user.id,
            "nombre": "Prof",
            "apellidos": "Test",
            "estado": "Activo",
            "facturador": False,
        }
    )

    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"C-{uuid.uuid4().hex[:4]}", "nombre": "Ingeniería"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": f"M-{uuid.uuid4().hex[:4]}", "nombre": "Materia SD"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    dictado_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    dictado = await dictado_repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )

    # Assign usuario as PROFESOR
    asig_repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    await asig_repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "PROFESOR",
            "dictado_id": dictado.id,
            "desde": dt.date.today(),
            "hasta": None,
        }
    )

    # Padrón version with 2 alumnos
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create(
        {"dictado_id": dictado.id, "cargado_por": usuario.id, "activa": True}
    )
    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    active_ep = await ep_repo.bulk_create(
        [
            {"version_id": version.id, "nombre": "Active", "apellidos": "Alumno", "email": "active@test.com"},
            {"version_id": version.id, "nombre": "Baja", "apellidos": "Alumno", "email": "baja@test.com"},
        ]
    )

    # Actividad with past fecha_limite
    act_repo = BaseRepository(model=Actividad, session=db_session, tenant_id=tenant_id)
    actividad = await act_repo.create(
        {
            "dictado_id": dictado.id,
            "nombre": "TP Regresion",
            "tipo": "TP",
            "fecha_limite": dt.date(2025, 1, 1),  # past date → generates atraso
        }
    )

    current_user = CurrentUser(user_id=user.id, tenant_id=tenant_id, roles=["PROFESOR"])
    return {
        "current_user": current_user,
        "dictado": dictado,
        "entradas": active_ep,  # [active_ep, baja_ep]
        "actividad": actividad,
        "ep_repo": ep_repo,
    }


async def test_soft_deleted_alumno_absent_from_atrasados_cross_materia(
    db_session: AsyncSession, test_tenant
):
    """Task 1.5 TRIANGULATE: soft-deleted alumno must not appear in get_atrasados_cross_materia.

    This confirms the single fix (find_by_version filter) covers the atrasados read path.
    """
    data = await _setup_profesor_with_dictado_and_atrasado(db_session, test_tenant.id)
    ep_repo = data["ep_repo"]
    current_user = data["current_user"]
    entradas = data["entradas"]

    # Soft-delete the 'Baja' alumno
    baja_ep = next(e for e in entradas if e.nombre == "Baja")
    baja_ep.deleted_at = datetime.now(UTC)
    await db_session.flush()

    service = ProfesorService(db_session=db_session, tenant_id=test_tenant.id)
    atrasados = await service.get_atrasados_cross_materia(current_user)

    baja_ids = {str(r["entrada_padron_id"]) for r in atrasados}
    assert str(baja_ep.id) not in baja_ids, (
        "Soft-deleted 'Baja' alumno must not appear in get_atrasados_cross_materia"
    )

    # The active alumno must still appear (they have no entrega for the past-due actividad)
    active_ep = next(e for e in entradas if e.nombre == "Active")
    active_ids = {str(r["entrada_padron_id"]) for r in atrasados}
    assert str(active_ep.id) in active_ids, (
        "Active alumno must still appear in get_atrasados_cross_materia"
    )


async def test_soft_deleted_alumno_absent_from_get_alumnos_clasificados(
    db_session: AsyncSession, test_tenant
):
    """Task 1.5 TRIANGULATE: soft-deleted alumno must not appear in get_alumnos_clasificados.

    This confirms the single fix covers the actividades read path.
    """
    data = await _setup_profesor_with_dictado_and_atrasado(db_session, test_tenant.id)
    current_user = data["current_user"]
    dictado = data["dictado"]
    entradas = data["entradas"]

    # Soft-delete the 'Baja' alumno
    baja_ep = next(e for e in entradas if e.nombre == "Baja")
    baja_ep.deleted_at = datetime.now(UTC)
    await db_session.flush()

    service = ProfesorService(db_session=db_session, tenant_id=test_tenant.id)
    clasificados = await service.get_alumnos_clasificados(dictado.id)

    # get_alumnos_clasificados returns dicts with key "alumno_id" (= entrada.id)
    baja_ids = {str(r["alumno_id"]) for r in clasificados}
    assert str(baja_ep.id) not in baja_ids, (
        "Soft-deleted 'Baja' alumno must not appear in get_alumnos_clasificados"
    )

    # The active alumno must appear
    active_ep = next(e for e in entradas if e.nombre == "Active")
    active_ids = {str(r["alumno_id"]) for r in clasificados}
    assert str(active_ep.id) in active_ids, (
        "Active alumno must still appear in get_alumnos_clasificados"
    )
