"""Tests for AvisoService."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.aviso import Aviso, AcknowledgmentAviso, AlcanceAviso, SeveridadAviso
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.schemas.avisos import AvisoCreate, AvisoUpdate
from app.services.avisos_service import AvisoService
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


_JAN2026 = datetime(2026, 1, 1, tzinfo=UTC)
_DEC2026 = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)


@pytest.fixture
async def _seed_perms(db_session, test_tenant):
    await seed_permissions_for_tenant(db_session, test_tenant.id)
    cleanup_permission_cache()
    yield
    cleanup_permission_cache()


@pytest.fixture(autouse=True)
async def _use_seed_perms(_seed_perms):
    pass


@pytest.fixture
async def test_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"coord-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Coordinador",
        "is_active": True,
    })


@pytest.fixture
async def test_usuario(db_session, test_tenant, test_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "user_id": test_user.id,
        "nombre": "Coord",
        "apellidos": "Test",
    })


@pytest.fixture
def current_user(test_user, test_tenant) -> CurrentUser:
    return CurrentUser(
        user_id=test_user.id,
        tenant_id=test_tenant.id,
        roles=["COORDINADOR"],
    )


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {"user-agent": "test-agent"}
    return request


def service_factory(db_session, tenant_id) -> AvisoService:
    return AvisoService.create(db_session, tenant_id)


@pytest.mark.asyncio
async def test_create_aviso(db_session, test_tenant, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    data = AvisoCreate(
        alcance=AlcanceAviso.GLOBAL.value,
        titulo="Nuevo aviso",
        cuerpo="Contenido del aviso",
        inicio_en=_JAN2026,
        fin_en=_DEC2026,
        orden=5,
    )
    result = await service.create_aviso(data, current_user=current_user, request=mock_request)
    assert result.id is not None
    assert result.titulo == "Nuevo aviso"
    assert result.alcance == "GLOBAL"
    assert result.orden == 5


@pytest.mark.asyncio
async def test_update_aviso(db_session, test_tenant, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    a = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Original",
        "cuerpo": "Original",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
    })
    update_data = AvisoUpdate(titulo="Actualizado", orden=10)
    result = await service.update(a.id, update_data, current_user=current_user, request=mock_request)
    assert result.titulo == "Actualizado"
    assert result.orden == 10


@pytest.mark.asyncio
async def test_update_not_found(db_session, test_tenant, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException, match="Aviso"):
        await service.update(
            uuid.uuid4(),
            AvisoUpdate(titulo="Nope"),
            current_user=current_user,
            request=mock_request,
        )


@pytest.mark.asyncio
async def test_delete_aviso(db_session, test_tenant, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    a = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Delete me",
        "cuerpo": "Bye",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
    })
    await service.delete(a.id, current_user=current_user, request=mock_request)
    deleted = await repo.find_by_id(a.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_visible(db_session, test_tenant, test_usuario, current_user):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Visible 1",
        "cuerpo": "Test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
    })
    results = await service.get_visible(current_user)
    assert len(results) >= 1
    titles = [r.titulo for r in results]
    assert "Visible 1" in titles


@pytest.mark.asyncio
async def test_get_pendientes(db_session, test_tenant, test_usuario, current_user):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    a = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Ack required",
        "cuerpo": "Test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "requiere_ack": True,
    })
    results = await service.get_pendientes(current_user)
    assert any(r.id == a.id for r in results)


@pytest.mark.asyncio
async def test_confirmar(db_session, test_tenant, test_usuario, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    a = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Confirm me",
        "cuerpo": "Test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "requiere_ack": True,
    })
    result = await service.confirmar(a.id, current_user=current_user, request=mock_request)
    assert result.acknowledged is True


@pytest.mark.asyncio
async def test_confirmar_idempotent(db_session, test_tenant, test_usuario, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    a = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Confirm twice",
        "cuerpo": "Test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "requiere_ack": True,
    })
    r1 = await service.confirmar(a.id, current_user=current_user, request=mock_request)
    assert r1.acknowledged is True
    r2 = await service.confirmar(a.id, current_user=current_user, request=mock_request)
    assert r2.acknowledged is True


@pytest.mark.asyncio
async def test_confirmar_not_found(db_session, test_tenant, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException, match="Aviso"):
        await service.confirmar(
            uuid.uuid4(), current_user=current_user, request=mock_request
        )


@pytest.mark.asyncio
async def test_get_stats(db_session, test_tenant, test_usuario, current_user, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    a = await repo.create({
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Stats test",
        "cuerpo": "Test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "requiere_ack": True,
    })
    stats = await service.get_stats(a.id, current_user=current_user)
    assert stats.total == 0
    assert stats.confirmados == 0

    ack_repo = BaseRepository(
        model=AcknowledgmentAviso,
        session=db_session,
        tenant_id=test_tenant.id,
    )
    await ack_repo.create({"aviso_id": a.id, "usuario_id": test_usuario.id})

    stats2 = await service.get_stats(a.id, current_user=current_user)
    assert stats2.total == 1
    assert stats2.confirmados == 1
