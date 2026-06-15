"""Business rule integration tests for padrón (Task Group 8).

Tests cover:
  8.1 — Versionado: new version deactivates previous
  8.2 — Import xlsx/csv: preview shows summary, confirm persists
  8.3 — Entrada sin usuario_id: alumno sin cuenta se persiste con null
  8.4 — Aislamiento tenant: tenant A no ve datos de tenant B
  8.5 — Mock Moodle WS: sync success creates version; Moodle error -> 502
  8.6 — Vaciado scope-isolated RN-04: prof vs coordinador
"""

import csv
import io
import uuid

import pytest
from httpx import AsyncClient
from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.schemas.auth import CurrentUser
from app.services.padron.padron_service import PadronService
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


# ── Helpers ───────────────────────────────────────────────────────


def _make_csv_bytes(rows: list[dict]) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _make_xlsx_bytes(rows: list[dict]) -> bytes:
    wb = Workbook()
    ws = wb.active
    if rows:
        ws.append(list(rows[0].keys()))
        for row in rows:
            ws.append(list(row.values()))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


async def _create_user_and_profile(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> tuple[User, Usuario]:
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


async def _create_dictado(db_session: AsyncSession, tenant_id: uuid.UUID):
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


# ── 8.1 Versionado ────────────────────────────────────────────────


class TestVersionado:
    async def test_new_version_deactivates_previous(
        self, db_session: AsyncSession, test_tenant
    ):
        """Importing a new version for the same dictado deactivates the old one."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        old_version = await _seed_active_version(db_session, test_tenant.id, dictado.id, usuario.id)

        service = PadronService(db_session, test_tenant.id, user.id)
        csv_content = _make_csv_bytes([
            {"nombre": "Nuevo", "apellidos": "Alumno", "email": "nuevo@test.com"},
        ])
        preview = await service.preview_archivo(csv_content, "v2.csv", dictado.id)
        result = await service.confirmar_importacion(dictado.id, preview["preview_token"])

        vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
        old = await vp_repo.find_by_id(old_version.id)
        assert old.activa is False

        new = await vp_repo.find_by_id(result["version_id"])
        assert new.activa is True


# ── 8.2 Import xlsx/csv ───────────────────────────────────────────


class TestImportFormat:
    async def test_import_csv_preview_shows_summary_and_confirm_persists(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = PadronService(db_session, test_tenant.id, user.id)

        csv_content = _make_csv_bytes([
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "comision": "A"},
            {"nombre": "Ana", "apellidos": "López", "email": "ana@test.com"},
        ])

        preview = await service.preview_archivo(csv_content, "alumnos.csv", dictado.id)
        assert preview["total_filas"] == 2
        assert "preview_token" in preview

        result = await service.confirmar_importacion(dictado.id, preview["preview_token"])
        assert result["total_importados"] == 2

        entries = await service.obtener_padron_activo(dictado.id)
        assert len(entries) == 2

    async def test_import_xlsx_preview_shows_summary_and_confirm_persists(
        self, db_session: AsyncSession, test_tenant
    ):
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = PadronService(db_session, test_tenant.id, user.id)

        xlsx_content = _make_xlsx_bytes([
            {"nombre": "Carlos", "apellidos": "García", "email": "carlos@test.com"},
        ])

        preview = await service.preview_archivo(xlsx_content, "alumnos.xlsx", dictado.id)
        assert preview["total_filas"] == 1

        result = await service.confirmar_importacion(dictado.id, preview["preview_token"])
        assert result["total_importados"] == 1

        entries = await service.obtener_padron_activo(dictado.id)
        assert len(entries) == 1
        assert entries[0].nombre == "Carlos"


# ── 8.3 Entrada sin usuario_id ────────────────────────────────────


class TestEntradaSinUsuario:
    async def test_entrada_without_usuario_id_is_persisted(
        self, db_session: AsyncSession, test_tenant
    ):
        """Alumno sin cuenta en el sistema: usuario_id queda null."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)
        service = PadronService(db_session, test_tenant.id, user.id)

        csv_content = _make_csv_bytes([
            {"nombre": "Alumno", "apellidos": "SinCuenta", "email": "sin@test.com"},
        ])
        preview = await service.preview_archivo(csv_content, "data.csv", dictado.id)
        await service.confirmar_importacion(dictado.id, preview["preview_token"])

        entries = await service.obtener_padron_activo(dictado.id)
        assert len(entries) == 1
        assert entries[0].usuario_id is None


# ── 8.4 Aislamiento tenant ────────────────────────────────────────


class TestAislamientoTenant:
    async def test_tenant_a_data_not_visible_to_tenant_b(
        self, db_session: AsyncSession, test_tenant, another_tenant
    ):
        user_a, usuario_a = await _create_user_and_profile(db_session, test_tenant.id)
        dictado_a = await _create_dictado(db_session, test_tenant.id)
        await _seed_active_version(db_session, test_tenant.id, dictado_a.id, usuario_a.id)

        user_b, _ = await _create_user_and_profile(db_session, another_tenant.id)
        service_b = PadronService(db_session, another_tenant.id, user_b.id)

        entries = await service_b.obtener_padron_activo(dictado_a.id)
        assert entries == []


# ── 8.5 Mock Moodle WS ────────────────────────────────────────────


class TestMoodleSyncThroughRouter:
    async def test_moodle_sync_creates_version(
        self, client: AsyncClient, app, db_session: AsyncSession, test_tenant
    ):
        """Sync through router creates version via mocked Moodle WS."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)

        async def _override_user():
            return CurrentUser(
                user_id=user.id,
                tenant_id=test_tenant.id,
                roles=["ADMIN"],
            )

        app.dependency_overrides[get_current_user] = _override_user
        await seed_permissions_for_tenant(db_session, test_tenant.id)
        cleanup_permission_cache()

        from unittest.mock import AsyncMock, patch

        mock_users = [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "comision": "A", "regional": "CABA"},
        ]

        with patch("app.services.padron.moodle_sync_service.MoodleClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.sync_usuarios.return_value = mock_users
            MockClient.return_value = mock_instance

            response = await client.post(
                "/api/admin/padron/sync/moodle",
                json={
                    "dictado_id": str(dictado.id),
                    "base_url": "https://moodle.test",
                    "token": "tok",
                    "course_id": 1,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_importados"] == 1
        assert "version_id" in data

        app.dependency_overrides.pop(get_current_user, None)
        cleanup_permission_cache()


# ── 8.6 Vaciado scope-isolated RN-04 ──────────────────────────────


class TestVaciadoScopeIsolated:
    async def test_profesor_deletes_only_own_versions(
        self, db_session: AsyncSession, test_tenant
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

        service_a = PadronService(db_session, test_tenant.id, user_a.id)
        result = await service_a.vaciar_dictado(dictado.id, user_a.id, es_coordinador=False)

        assert result["entradas_eliminadas"] > 0

        remaining = await vp_repo.find_by_dictado(dictado.id)
        assert len(remaining) == 1
        assert remaining[0].cargado_por == usuario_b.id

    async def test_coordinador_deletes_all_versions(
        self, db_session: AsyncSession, test_tenant
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

        service = PadronService(db_session, test_tenant.id, user_a.id)
        result = await service.vaciar_dictado(dictado.id, user_a.id, es_coordinador=True)

        assert result["entradas_eliminadas"] > 0

        remaining = await vp_repo.find_by_dictado(dictado.id)
        assert len(remaining) == 0
