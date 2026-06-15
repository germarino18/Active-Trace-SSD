"""Tests for PadronService (TASK GROUP 5).

Real ephemeral test DB (no DB mocks, regla dura #4). Tests cover:
- preview_archivo: parsing, column validation, token generation
- confirmar_importacion: version+entries creation, deactivation, audit
- obtener_padron_activo: active version resolution
- listar_versiones: version history
- vaciar_dictado: scope-isolated deletion (coordinador vs profesor)
- Tenant isolation

NOTE: audit_log.actor_id FK references users.id, while
version_padron.cargado_por FK references usuario.id. The service
resolves usuario.id from the current_user_id (User.id) internally.
"""

import csv
import io
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.dictado import Dictado
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.services.padron.padron_service import PadronService


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_csv_bytes(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _make_service(
    db_session: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID
) -> PadronService:
    return PadronService(
        db_session=db_session,
        tenant_id=tenant_id,
        current_user_id=current_user_id,
    )


async def _create_user_and_profile(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> tuple[User, Usuario]:
    """Create a User (auth identity) + Usuario (business profile).
    Returns (user, usuario). user.id is for audit_log.actor_id (FK to users),
    usuario.id is for version_padron.cargado_por (FK to usuario).
    """
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create({
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
        "is_active": True,
        "roles": [],
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
        "estado": "Activo",
    })
    return user, usuario


async def _create_dictado(db_session: AsyncSession, tenant_id: uuid.UUID) -> Dictado:
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    return await repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )


async def _seed_active_version(
    db_session: AsyncSession, tenant_id: uuid.UUID, dictado_id: uuid.UUID, usuario_id: uuid.UUID
) -> VersionPadron:
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create({
        "dictado_id": dictado_id,
        "cargado_por": usuario_id,
        "activa": True,
    })
    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    await ep_repo.bulk_create([
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        {"version_id": version.id, "nombre": "Ana", "apellidos": "López", "email": "ana@test.com"},
    ])
    return version


# ── 5.1 preview_archivo ──────────────────────────────────────────────────


async def test_preview_archivo_parses_csv_and_returns_preview(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    csv_content = _make_csv_bytes([
        {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "comision": "A"},
        {"nombre": "María", "apellidos": "García", "email": "maria@test.com"},
    ])

    result = await service.preview_archivo(csv_content, "alumnos.csv", dictado.id)

    assert "columnas_encontradas" in result
    assert "nombre" in result["columnas_encontradas"]
    assert "apellidos" in result["columnas_encontradas"]
    assert "email" in result["columnas_encontradas"]
    assert "comision" in result["columnas_encontradas"]
    assert result["total_filas"] == 2
    assert len(result["filas"]) == 2
    assert result["filas"][0]["nombre"] == "Juan"
    assert "preview_token" in result
    assert isinstance(result["preview_token"], str)


async def test_preview_archivo_rejects_missing_required_columns(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    csv_content = _make_csv_bytes([
        {"nombre": "Juan", "apellidos": "Pérez"},  # missing email
    ])

    with pytest.raises(ValidationException, match="email"):
        await service.preview_archivo(csv_content, "bad.csv", dictado.id)


async def test_preview_archivo_handles_extra_columns(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    csv_content = _make_csv_bytes([
        {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "telefono": "123456"},
    ])

    result = await service.preview_archivo(csv_content, "extra.csv", dictado.id)

    assert "telefono" in result["columnas_encontradas"]
    assert result["total_filas"] == 1


async def test_preview_archivo_rejects_unsupported_format(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    with pytest.raises(ValidationException, match="(?i)formato"):
        await service.preview_archivo(b"not a file", "data.pdf", dictado.id)


# ── 5.2 confirmar_importacion ────────────────────────────────────────────


async def test_confirmar_importacion_creates_version_and_entries(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    csv_content = _make_csv_bytes([
        {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
        {"nombre": "Ana", "apellidos": "López", "email": "ana@test.com"},
    ])
    preview = await service.preview_archivo(csv_content, "data.csv", dictado.id)

    result = await service.confirmar_importacion(dictado.id, preview["preview_token"])

    assert "version_id" in result
    assert result["total_importados"] == 2
    assert result["mensaje"] is not None

    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.find_by_id(result["version_id"])
    assert version is not None
    assert version.activa is True
    assert version.cargado_por == usuario.id

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    entries = await ep_repo.find_by_version(result["version_id"])
    assert len(entries) == 2


async def test_confirmar_importacion_deactivates_previous_active_version(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    old_version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)

    service = _make_service(db_session, test_tenant.id, user.id)
    csv_content = _make_csv_bytes([
        {"nombre": "Nuevo", "apellidos": "Alumno", "email": "nuevo@test.com"},
    ])
    preview = await service.preview_archivo(csv_content, "data.csv", dictado.id)
    result = await service.confirmar_importacion(dictado.id, preview["preview_token"])

    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    old = await vp_repo.find_by_id(old_version.id)
    assert old.activa is False

    new = await vp_repo.find_by_id(result["version_id"])
    assert new.activa is True


async def test_confirmar_importacion_audits_padron_cargar(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    csv_content = _make_csv_bytes([
        {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
    ])
    preview = await service.preview_archivo(csv_content, "data.csv", dictado.id)
    await service.confirmar_importacion(dictado.id, preview["preview_token"])

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.PADRON_CARGAR)
    assert len(logs) == 1
    assert logs[0].actor_id == user.id


async def test_confirmar_importacion_invalid_token_raises_error(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    with pytest.raises(ValidationException, match="(?i)token"):
        await service.confirmar_importacion(dictado.id, "invalid-token")


async def test_confirmar_importacion_wrong_dictado_raises_error(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    service = _make_service(db_session, test_tenant.id, user.id)

    csv_content = _make_csv_bytes([
        {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com"},
    ])
    preview = await service.preview_archivo(csv_content, "data.csv", dictado.id)

    other_dictado_id = uuid.uuid4()
    with pytest.raises(ValidationException, match="token"):
        await service.confirmar_importacion(other_dictado_id, preview["preview_token"])


# ── 5.3 obtener_padron_activo ────────────────────────────────────────────


async def test_obtener_padron_activo_returns_active_version_entries(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)

    service = _make_service(db_session, test_tenant.id, user.id)
    entries = await service.obtener_padron_activo(dictado.id)

    assert len(entries) == 2


async def test_obtener_padron_activo_returns_empty_when_no_active_version(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)

    service = _make_service(db_session, test_tenant.id, user.id)
    entries = await service.obtener_padron_activo(dictado.id)

    assert entries == []


# ── 5.4 listar_versiones ────────────────────────────────────────────────


async def test_listar_versiones_returns_all_versions_ordered(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    v1 = await vp_repo.create({
        "dictado_id": dictado.id, "cargado_por": usuario.id, "activa": True,
    })
    v2 = await vp_repo.create({
        "dictado_id": dictado.id, "cargado_por": usuario.id, "activa": False,
    })

    service = _make_service(db_session, test_tenant.id, user.id)
    versions = await service.listar_versiones(dictado.id)

    assert len(versions) == 2
    version_ids = {v.id for v in versions}
    assert v1.id in version_ids
    assert v2.id in version_ids


async def test_listar_versiones_returns_empty_when_no_versions(
    db_session: AsyncSession, test_tenant
):
    user, _ = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)

    service = _make_service(db_session, test_tenant.id, user.id)
    versions = await service.listar_versiones(dictado.id)

    assert versions == []


# ── 5.5 vaciar_dictado ───────────────────────────────────────────────────


async def test_vaciar_dictado_coordinador_deletes_all_entries(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)

    service = _make_service(db_session, test_tenant.id, user.id)
    result = await service.vaciar_dictado(dictado.id, user.id, es_coordinador=True)

    assert result["entradas_eliminadas"] > 0
    assert result["dictado_id"] == dictado.id

    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    remaining = await vp_repo.find_by_dictado(dictado.id)
    assert len(remaining) == 0


async def test_vaciar_dictado_profesor_deletes_only_own_versions(
    db_session: AsyncSession, test_tenant
):
    user_a, usuario_a = await _create_user_and_profile(db_session, test_tenant.id)
    user_b, usuario_b = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    await vp_repo.create({
        "dictado_id": dictado.id, "cargado_por": usuario_a.id, "activa": True,
    })
    await vp_repo.create({
        "dictado_id": dictado.id, "cargado_por": usuario_b.id, "activa": False,
    })

    service = _make_service(db_session, test_tenant.id, user_a.id)
    result = await service.vaciar_dictado(dictado.id, user_a.id, es_coordinador=False)

    assert result["entradas_eliminadas"] > 0

    remaining = await vp_repo.find_by_dictado(dictado.id)
    assert len(remaining) == 1
    assert remaining[0].cargado_por == usuario_b.id


async def test_vaciar_dictado_audits_padron_vaciar(
    db_session: AsyncSession, test_tenant
):
    user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)

    service = _make_service(db_session, test_tenant.id, user.id)
    await service.vaciar_dictado(dictado.id, user.id, es_coordinador=True)

    audit_repo = AuditLogRepository(session=db_session, tenant_id=test_tenant.id)
    logs = await audit_repo.find_by(accion=AccionAuditoria.PADRON_VACIAR)
    assert len(logs) == 1
    assert logs[0].actor_id == user.id


# ── 5.6 Tenant isolation ─────────────────────────────────────────────────


async def test_tenant_isolation_prevents_cross_tenant_access(
    db_session: AsyncSession, test_tenant, another_tenant
):
    user_a, usuario_a = await _create_user_and_profile(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    await _seed_active_version(db_session, test_tenant.id, dictado_a.id, usuario_a.id)

    # User from another tenant trying to access tenant A's dictado
    user_b, _ = await _create_user_and_profile(db_session, another_tenant.id)
    service_b = _make_service(db_session, another_tenant.id, user_b.id)

    entries = await service_b.obtener_padron_activo(dictado_a.id)
    assert entries == []
