"""Tests for TareasService."""

from unittest.mock import MagicMock
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.tarea import Tarea, TareaEstado
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.schemas.tareas import TareaCreate, TareaUpdateEstado
from app.services.tareas_service import TareasService
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


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
async def coord_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"coord-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Coordinador",
        "is_active": True,
    })


@pytest.fixture
async def prof_user(db_session, test_tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Profesor",
        "is_active": True,
    })


@pytest.fixture
async def coord_usuario(db_session, test_tenant, coord_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": coord_user.id, "nombre": "Coord", "apellidos": "Test"})


@pytest.fixture
async def prof_usuario(db_session, test_tenant, prof_user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": prof_user.id, "nombre": "Prof", "apellidos": "Test"})


@pytest.fixture
def current_user_coord(coord_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=coord_user.id, tenant_id=test_tenant.id, roles=["COORDINADOR"])


@pytest.fixture
def current_user_prof(prof_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=prof_user.id, tenant_id=test_tenant.id, roles=["PROFESOR"])


@pytest.fixture
def current_user_admin(coord_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=coord_user.id, tenant_id=test_tenant.id, roles=["ADMIN"])


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {"user-agent": "test-agent"}
    return request


def service_factory(db_session, tenant_id) -> TareasService:
    return TareasService.create(db_session, tenant_id)


@pytest.mark.asyncio
async def test_create_tarea(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    data = TareaCreate(
        asignado_a=prof_usuario.id,
        descripcion="Corregir trabajos practicos",
    )
    result = await service.create_tarea(data, current_user=current_user_coord, request=mock_request)
    assert result.id is not None
    assert result.descripcion == "Corregir trabajos practicos"
    assert result.asignado_a == prof_usuario.id
    assert result.asignado_por == coord_usuario.id
    assert result.estado == TareaEstado.PENDIENTE.value


@pytest.mark.asyncio
async def test_cambiar_estado_valido(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({
        "asignado_a": prof_usuario.id,
        "asignado_por": coord_usuario.id,
        "descripcion": "Test",
        "estado": TareaEstado.PENDIENTE.value,
    })
    result = await service.cambiar_estado(
        t.id, TareaUpdateEstado(estado=TareaEstado.EN_PROGRESO),
        current_user=current_user_coord, request=mock_request,
    )
    assert result.estado == TareaEstado.EN_PROGRESO.value


@pytest.mark.asyncio
async def test_cambiar_estado_invalido_raises(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({
        "asignado_a": prof_usuario.id,
        "asignado_por": coord_usuario.id,
        "descripcion": "Test",
        "estado": TareaEstado.PENDIENTE.value,
    })
    with pytest.raises(ValidationException):
        await service.cambiar_estado(
            t.id, TareaUpdateEstado(estado=TareaEstado.RESUELTA),
            current_user=current_user_coord, request=mock_request,
        )


@pytest.mark.asyncio
async def test_cambiar_estado_resuelta_a_en_progreso_coord(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({
        "asignado_a": prof_usuario.id,
        "asignado_por": coord_usuario.id,
        "descripcion": "Test",
        "estado": TareaEstado.RESUELTA.value,
    })
    result = await service.cambiar_estado(
        t.id, TareaUpdateEstado(estado=TareaEstado.EN_PROGRESO),
        current_user=current_user_coord, request=mock_request,
    )
    assert result.estado == TareaEstado.EN_PROGRESO.value


@pytest.mark.asyncio
async def test_cambiar_estado_resuelta_a_en_progreso_prof_raises(db_session, test_tenant, coord_usuario, prof_usuario, current_user_prof, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({
        "asignado_a": prof_usuario.id,
        "asignado_por": coord_usuario.id,
        "descripcion": "Test",
        "estado": TareaEstado.RESUELTA.value,
    })
    with pytest.raises(ForbiddenException):
        await service.cambiar_estado(
            t.id, TareaUpdateEstado(estado=TareaEstado.EN_PROGRESO),
            current_user=current_user_prof, request=mock_request,
        )


@pytest.mark.asyncio
async def test_cambiar_estado_admin_can_reopen(db_session, test_tenant, coord_usuario, prof_usuario, current_user_admin, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({
        "asignado_a": prof_usuario.id,
        "asignado_por": coord_usuario.id,
        "descripcion": "Test",
        "estado": TareaEstado.RESUELTA.value,
    })
    result = await service.cambiar_estado(
        t.id, TareaUpdateEstado(estado=TareaEstado.EN_PROGRESO),
        current_user=current_user_admin, request=mock_request,
    )
    assert result.estado == TareaEstado.EN_PROGRESO.value


@pytest.mark.asyncio
async def test_cambiar_estado_not_found(db_session, test_tenant, coord_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.cambiar_estado(
            uuid.uuid4(), TareaUpdateEstado(estado=TareaEstado.EN_PROGRESO),
            current_user=current_user_coord, request=mock_request,
        )


@pytest.mark.asyncio
async def test_cambiar_estado_with_auto_comment(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({
        "asignado_a": prof_usuario.id,
        "asignado_por": coord_usuario.id,
        "descripcion": "Test",
        "estado": TareaEstado.PENDIENTE.value,
    })
    result = await service.cambiar_estado(
        t.id, TareaUpdateEstado(estado=TareaEstado.EN_PROGRESO, comentario="Empiezo ahora"),
        current_user=current_user_coord, request=mock_request,
    )
    assert len(result.comentarios) == 1
    assert result.comentarios[0].texto == "Empiezo ahora"
    assert result.comentarios[0].autor_id == coord_usuario.id


@pytest.mark.asyncio
async def test_get_mis_tareas(db_session, test_tenant, coord_usuario, prof_usuario, current_user_prof):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "T1", "estado": TareaEstado.PENDIENTE.value})
    await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "T2", "estado": TareaEstado.PENDIENTE.value})

    results = await service.get_mis_tareas(current_user_prof)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_get_mis_tareas_respects_tenant(db_session, test_tenant, another_tenant, prof_usuario, current_user_prof):
    service1 = service_factory(db_session, test_tenant.id)
    service2 = service_factory(db_session, another_tenant.id)
    await service1._repo.create({"asignado_a": prof_usuario.id, "asignado_por": prof_usuario.id, "descripcion": "T1", "estado": TareaEstado.PENDIENTE.value})

    results2 = await service2.get_mis_tareas(current_user_prof)
    assert len(results2) == 0


@pytest.mark.asyncio
async def test_get_all_managed(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "T1", "estado": TareaEstado.PENDIENTE.value})
    await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "T2", "estado": TareaEstado.EN_PROGRESO.value})

    results = await service.get_all_managed(current_user_coord)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_get_tarea_with_comments(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "Test", "estado": TareaEstado.PENDIENTE.value})

    result = await service.get_tarea(t.id, current_user_coord)
    assert result.id == t.id
    assert result.comentarios == []


@pytest.mark.asyncio
async def test_get_tarea_not_found(db_session, test_tenant, current_user_coord):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.get_tarea(uuid.uuid4(), current_user_coord)


@pytest.mark.asyncio
async def test_delete_tarea(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "Delete me", "estado": TareaEstado.PENDIENTE.value})

    await service.delete_tarea(t.id, current_user=current_user_coord, request=mock_request)
    deleted = await repo.find_by_id(t.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_tarea_not_found(db_session, test_tenant, current_user_coord, mock_request):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.delete_tarea(uuid.uuid4(), current_user=current_user_coord, request=mock_request)


@pytest.mark.asyncio
async def test_agregar_comentario(db_session, test_tenant, coord_usuario, prof_usuario, current_user_coord):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    t = await repo.create({"asignado_a": prof_usuario.id, "asignado_por": coord_usuario.id, "descripcion": "Test", "estado": TareaEstado.PENDIENTE.value})

    comentario = await service.agregar_comentario(t.id, "Un comentario", current_user_coord)
    assert comentario.texto == "Un comentario"
    assert comentario.tarea_id == t.id
    assert comentario.autor_id == coord_usuario.id


@pytest.mark.asyncio
async def test_agregar_comentario_tarea_not_found(db_session, test_tenant, current_user_coord):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.agregar_comentario(uuid.uuid4(), "Comentario", current_user_coord)
