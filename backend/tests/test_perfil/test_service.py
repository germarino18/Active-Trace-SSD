"""Tests for PerfilService."""
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.schemas.perfil import PerfilUpdate
from app.services.perfil_service import PerfilService


@pytest.fixture
def service(db_session: AsyncSession, test_tenant: Tenant) -> PerfilService:
    return PerfilService(db=db_session, tenant_id=test_tenant.id)


class TestGetPerfil:
    async def test_returns_profile(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: PerfilService,
        auth_user: CurrentUser,
    ):
        usuario, email = await service.get_perfil(auth_user.user_id)
        assert usuario.nombre == "Test"
        assert usuario.apellidos == "User"
        assert email  # should resolve from users table

    async def test_no_profile_returns_404(
        self,
        service: PerfilService,
        auth_user_no_profile: CurrentUser,
    ):
        with pytest.raises(NotFoundException):
            await service.get_perfil(auth_user_no_profile.user_id)

    async def test_wrong_tenant_scoped(
        self,
        db_session: AsyncSession,
        another_tenant: Tenant,
        auth_user: CurrentUser,
    ):
        """Usuario de tenant A no puede ver perfil en tenant B."""
        wrong_service = PerfilService(db=db_session, tenant_id=another_tenant.id)
        with pytest.raises(NotFoundException):
            await wrong_service.get_perfil(auth_user.user_id)


class TestUpdatePerfil:
    async def test_updates_fields(
        self,
        db_session: AsyncSession,
        service: PerfilService,
        auth_user: CurrentUser,
    ):
        data = PerfilUpdate(nombre="Updated", banco="Nación")
        usuario, email = await service.update_perfil(auth_user.user_id, data)
        assert usuario.nombre == "Updated"
        assert usuario.banco == "Nación"

    async def test_no_profile_raises_404(
        self,
        service: PerfilService,
        auth_user_no_profile: CurrentUser,
    ):
        data = PerfilUpdate(nombre="X")
        with pytest.raises(NotFoundException):
            await service.update_perfil(auth_user_no_profile.user_id, data)

    async def test_empty_data_raises_error(
        self,
        service: PerfilService,
        auth_user: CurrentUser,
    ):
        data = PerfilUpdate()
        with pytest.raises(ValueError, match="No se proporcionaron campos editables"):
            await service.update_perfil(auth_user.user_id, data)

    async def test_tenant_isolation(
        self,
        db_session: AsyncSession,
        another_tenant: Tenant,
        auth_user: CurrentUser,
    ):
        wrong_service = PerfilService(db=db_session, tenant_id=another_tenant.id)
        data = PerfilUpdate(nombre="X")
        with pytest.raises(NotFoundException):
            await wrong_service.update_perfil(auth_user.user_id, data)
