"""Tests for ComunicacionesService."""

import uuid
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.template_engine import TemplateEngine
from app.models.comunicacion import ComunicacionEstado
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.schemas.comunicaciones import EnvioMasivoItem, EnvioMasivoRequest
from app.services.comunicaciones_service import ComunicacionesService
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
        "nombre": "Coordinador",
        "apellidos": "Test",
    })


@pytest.fixture
async def test_materia(db_session, test_tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})


@pytest.fixture
def current_user(test_user, test_tenant) -> CurrentUser:
    return CurrentUser(user_id=test_user.id, tenant_id=test_tenant.id, roles=["COORDINADOR"])


@pytest.fixture
def current_user_no_perm(db_session, test_tenant, test_user) -> CurrentUser:
    return CurrentUser(user_id=test_user.id, tenant_id=test_tenant.id, roles=["ALUMNO"])


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {"user-agent": "test-agent"}
    return request


def service_factory(db_session, tenant_id) -> ComunicacionesService:
    return ComunicacionesService.create(db_session, tenant_id)


@pytest.mark.asyncio
async def test_preview_renders_templates(db_session, test_tenant):
    service = service_factory(db_session, test_tenant.id)
    engine = TemplateEngine(
        allowed_variables={"alumno_nombre", "alumno_apellido", "materia", "docente_nombre"}
    )
    result = await service.preview(
        template_engine=engine,
        asunto_template="Hola $alumno_nombre",
        cuerpo_template="Materia: $materia",
        destinatario_info={
            "alumno_nombre": "Juan",
            "alumno_apellido": "Pérez",
            "materia": "Matemática",
            "docente_nombre": "Prof. García",
        },
    )
    assert result.asunto == "Hola Juan"
    assert result.cuerpo == "Materia: Matemática"


@pytest.mark.asyncio
async def test_enqueue_masivo_creates_pendientes(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    service = service_factory(db_session, test_tenant.id)
    req = EnvioMasivoRequest(
        materia_id=test_materia.id,
        asunto_template="Hola $alumno_nombre",
        cuerpo_template="Cuerpo genérico",
        destinatarios=[
            EnvioMasivoItem(
                usuario_id=test_usuario.id,
                destinatario_email="alumno@test.com",
                destinatario_nombre="Juan",
                destinatario_apellido="Pérez",
            ),
        ],
    )
    result = await service.enqueue_masivo(
        envio_data=req, current_user=current_user, request=mock_request
    )
    assert result.lote_id is not None
    assert result.total == 1


@pytest.mark.asyncio
async def test_enqueue_masivo_auto_aprobado(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    assert test_tenant.aprobacion_comunicaciones is False
    service = service_factory(db_session, test_tenant.id)
    req = EnvioMasivoRequest(
        materia_id=test_materia.id,
        asunto_template="Auto $alumno_nombre",
        cuerpo_template="Cuerpo",
        destinatarios=[
            EnvioMasivoItem(
                usuario_id=test_usuario.id,
                destinatario_email="a@b.com",
                destinatario_nombre="Ana",
                destinatario_apellido="López",
            ),
        ],
    )
    result = await service.enqueue_masivo(
        envio_data=req, current_user=current_user, request=mock_request
    )
    repo = service._repo
    comunicaciones = await repo.get_by_lote(result.lote_id)
    assert len(comunicaciones) == 1
    assert comunicaciones[0].estado == ComunicacionEstado.ENVIANDO.value


@pytest.mark.asyncio
async def test_enqueue_masivo_con_aprobacion(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    test_tenant.aprobacion_comunicaciones = True
    await db_session.flush()
    service = service_factory(db_session, test_tenant.id)
    req = EnvioMasivoRequest(
        materia_id=test_materia.id,
        asunto_template="Pend $alumno_nombre",
        cuerpo_template="Cuerpo",
        destinatarios=[
            EnvioMasivoItem(
                usuario_id=test_usuario.id,
                destinatario_email="b@c.com",
                destinatario_nombre="Pedro",
                destinatario_apellido="García",
            ),
        ],
    )
    result = await service.enqueue_masivo(
        envio_data=req, current_user=current_user, request=mock_request
    )
    repo = service._repo
    comunicaciones = await repo.get_by_lote(result.lote_id)
    assert len(comunicaciones) == 1
    assert comunicaciones[0].estado == ComunicacionEstado.PENDIENTE.value


@pytest.mark.asyncio
async def test_get_estado(db_session, test_tenant, test_materia, test_usuario, current_user):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    lote_id = uuid.uuid4()
    com = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "alumno@test.com",
        "destinatario_hash": "abc",
        "asunto": "Test",
        "cuerpo": "Cuerpo",
        "lote_id": lote_id,
    })
    result = await service.get_estado(com.id)
    assert result.id == com.id
    assert result.asunto == "Test"
    assert result.estado == ComunicacionEstado.PENDIENTE.value


@pytest.mark.asyncio
async def test_get_estado_not_found(db_session, test_tenant):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException, match="Comunicacion"):
        await service.get_estado(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_resumen_lote(db_session, test_tenant, test_materia, test_usuario):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    lote_id = uuid.uuid4()
    c1 = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "a@b.com",
        "destinatario_hash": "h1",
        "asunto": "A",
        "cuerpo": "C1",
        "lote_id": lote_id,
    })
    c2 = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "b@c.com",
        "destinatario_hash": "h2",
        "asunto": "B",
        "cuerpo": "C2",
        "lote_id": lote_id,
    })
    await repo.update_estado(c2.id, ComunicacionEstado.ENVIADO)
    resumen = await service.get_resumen_lote(lote_id)
    assert resumen.lote_id == lote_id
    assert resumen.total == 2
    assert resumen.pendientes == 1
    assert resumen.enviados == 1
    assert resumen.errores == 0
    assert resumen.cancelados == 0


@pytest.mark.asyncio
async def test_aprobar_lote(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    lote_id = uuid.uuid4()
    c1 = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "a@b.com",
        "destinatario_hash": "h1",
        "asunto": "A",
        "cuerpo": "C1",
        "lote_id": lote_id,
    })
    c2 = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "b@c.com",
        "destinatario_hash": "h2",
        "asunto": "B",
        "cuerpo": "C2",
        "lote_id": lote_id,
    })
    await service.aprobar_lote(lote_id, current_user=current_user, request=mock_request)
    c1_actualizado = await repo.find_by_id(c1.id)
    c2_actualizado = await repo.find_by_id(c2.id)
    assert c1_actualizado.estado == ComunicacionEstado.ENVIANDO.value
    assert c2_actualizado.estado == ComunicacionEstado.ENVIANDO.value


@pytest.mark.asyncio
async def test_aprobar_individual(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    com = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "a@b.com",
        "destinatario_hash": "h",
        "asunto": "Test",
        "cuerpo": "Cuerpo",
        "lote_id": uuid.uuid4(),
    })
    await service.aprobar_individual(
        com.id, current_user=current_user, request=mock_request
    )
    actualizado = await repo.find_by_id(com.id)
    assert actualizado.estado == ComunicacionEstado.ENVIANDO.value


@pytest.mark.asyncio
async def test_cancelar_lote(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    lote_id = uuid.uuid4()
    c1 = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "a@b.com",
        "destinatario_hash": "h1",
        "asunto": "A",
        "cuerpo": "C1",
        "lote_id": lote_id,
    })
    await service.cancelar_lote(lote_id, current_user=current_user, request=mock_request)
    actualizado = await repo.find_by_id(c1.id)
    assert actualizado.estado == ComunicacionEstado.CANCELADO.value


@pytest.mark.asyncio
async def test_cancelar_individual(
    db_session, test_tenant, test_materia, test_usuario, current_user, mock_request,
):
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    com = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "a@b.com",
        "destinatario_hash": "h",
        "asunto": "Test",
        "cuerpo": "Cuerpo",
        "lote_id": uuid.uuid4(),
    })
    await service.cancelar_individual(
        com.id, current_user=current_user, request=mock_request
    )
    actualizado = await repo.find_by_id(com.id)
    assert actualizado.estado == ComunicacionEstado.CANCELADO.value


@pytest.mark.asyncio
async def test_aprobar_individual_not_found(
    db_session, test_tenant, current_user, mock_request,
):
    service = service_factory(db_session, test_tenant.id)
    with pytest.raises(NotFoundException, match="Comunicacion"):
        await service.aprobar_individual(
            uuid.uuid4(), current_user=current_user, request=mock_request
        )


@pytest.mark.asyncio
async def test_aprobar_individual_forbidden(
    db_session, test_tenant, test_materia, test_usuario, mock_request,
):
    cu_no_perm = CurrentUser(
        user_id=test_usuario.id, tenant_id=test_tenant.id, roles=["ALUMNO"]
    )
    service = service_factory(db_session, test_tenant.id)
    repo = service._repo
    com = await repo.create({
        "enviado_por": test_usuario.id,
        "materia_id": test_materia.id,
        "destinatario": "a@b.com",
        "destinatario_hash": "h",
        "asunto": "Test",
        "cuerpo": "Cuerpo",
        "lote_id": uuid.uuid4(),
    })
    with pytest.raises(ForbiddenException, match="comunicacion:aprobar"):
        await service.aprobar_individual(
            com.id, current_user=cu_no_perm, request=mock_request
        )
