"""Tests for MoodleSyncService (Task 6.2).

Mocks MoodleClient to avoid real HTTP calls. Verifies that PadronService
is invoked to create versions from Moodle data. Uses real DB fixtures
for PadronService operation.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.dictado import Dictado
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.services.padron.padron_service import PadronService


# ── Helpers (from test_padron_service) ─────────────────────────────


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


async def _count_versions(db_session, tenant_id, dictado_id) -> int:
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
    return len(await vp_repo.find_by_dictado(dictado_id))


async def _count_entries(db_session, tenant_id) -> int:
    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
    all_entries = await ep_repo.find_all()
    return len(all_entries)


# ── Tests ──────────────────────────────────────────────────────────


class TestSyncOnDemand:
    async def test_sync_creates_version_with_moodle_users(
        self, db_session: AsyncSession, test_tenant
    ):
        """Successful sync creates a version with correct entries."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)

        moodle_config = {
            "base_url": "https://moodle.test",
            "token": "tok",
            "course_id": 42,
        }

        mock_users = [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "comision": "A", "regional": "CABA"},
            {"nombre": "Ana", "apellidos": "López", "email": "ana@test.com", "comision": None, "regional": None},
        ]

        with patch("app.services.padron.moodle_sync_service.MoodleClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.sync_usuarios.return_value = mock_users
            MockClient.return_value = mock_instance

            from app.services.padron.moodle_sync_service import MoodleSyncService
            service = MoodleSyncService(db_session, test_tenant.id, user.id)
            result = await service.sync_on_demand(dictado.id, moodle_config)

        assert "version_id" in result
        assert result["total_importados"] == 2

        versions = await _count_versions(db_session, test_tenant.id, dictado.id)
        assert versions == 1

        ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
        all_entries = await ep_repo.find_all()
        assert len(all_entries) == 2
        assert all_entries[0].nombre == "Juan"

    async def test_sync_empty_moodle_raises_validation_error(
        self, db_session: AsyncSession, test_tenant
    ):
        """Empty course from Moodle raises ValidationException (PadronService rejects empty imports)."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)

        moodle_config = {
            "base_url": "https://moodle.test",
            "token": "tok",
            "course_id": 1,
        }

        with patch("app.services.padron.moodle_sync_service.MoodleClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.sync_usuarios.return_value = []
            MockClient.return_value = mock_instance

            from app.services.padron.moodle_sync_service import MoodleSyncService
            service = MoodleSyncService(db_session, test_tenant.id, user.id)

            with pytest.raises(ValidationException, match="No hay filas"):
                await service.sync_on_demand(dictado.id, moodle_config)

    async def test_sync_moodle_down_raises_error(
        self, db_session: AsyncSession, test_tenant
    ):
        """When Moodle is unreachable, should propagate MoodleException."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        dictado = await _create_dictado(db_session, test_tenant.id)

        moodle_config = {
            "base_url": "https://moodle.test",
            "token": "tok",
            "course_id": 1,
        }

        from app.integrations.moodle_ws import MoodleException as ME

        with patch("app.services.padron.moodle_sync_service.MoodleClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.sync_usuarios.side_effect = ME("Moodle is down", status_code=502)
            MockClient.return_value = mock_instance

            from app.services.padron.moodle_sync_service import MoodleSyncService
            service = MoodleSyncService(db_session, test_tenant.id, user.id)

            with pytest.raises(ME) as exc_info:
                await service.sync_on_demand(dictado.id, moodle_config)

            assert exc_info.value.status_code == 502

    async def test_sync_non_existent_dictado_raises_integrity_error(
        self, db_session: AsyncSession, test_tenant
    ):
        """Sync for non-existent dictado fails with IntegrityError (FK violation)."""
        user, usuario = await _create_user_and_profile(db_session, test_tenant.id)
        fake_dictado_id = uuid.uuid4()

        moodle_config = {
            "base_url": "https://moodle.test",
            "token": "tok",
            "course_id": 1,
        }

        mock_users = [
            {"nombre": "Juan", "apellidos": "Pérez", "email": "juan@test.com", "comision": "A", "regional": "CABA"},
        ]

        with patch("app.services.padron.moodle_sync_service.MoodleClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.sync_usuarios.return_value = mock_users
            MockClient.return_value = mock_instance

            from app.services.padron.moodle_sync_service import MoodleSyncService
            service = MoodleSyncService(db_session, test_tenant.id, user.id)

            with pytest.raises(Exception) as exc_info:
                await service.sync_on_demand(fake_dictado_id, moodle_config)

            assert "viola" in str(exc_info.value) or "violates" in str(exc_info.value)


class TestSyncNocturna:
    async def test_nocturna_returns_results_per_tenant(self, db_session):
        """sync_nocturna iterates tenants and returns results."""
        from app.services.padron.moodle_sync_service import MoodleSyncService
        service = MoodleSyncService(db_session, uuid.uuid4(), uuid.uuid4())
        results = await service.sync_nocturna([])
        assert results == []
