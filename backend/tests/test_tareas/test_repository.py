"""Tests for TareaRepository."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.tarea import ComentarioTarea, Tarea, TareaEstado
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.repositories.tarea_repository import TareaRepository


@pytest.fixture
async def test_user_a(db_session: AsyncSession, test_tenant: Tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"user-a-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "User A",
    })


@pytest.fixture
async def test_user_b(db_session: AsyncSession, test_tenant: Tenant) -> User:
    repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "email": f"user-b-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "User B",
    })


@pytest.fixture
async def test_usuario_a(db_session: AsyncSession, test_tenant: Tenant, test_user_a) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": test_user_a.id, "nombre": "A", "apellidos": "User A"})


@pytest.fixture
async def test_usuario_b(db_session: AsyncSession, test_tenant: Tenant, test_user_b) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"user_id": test_user_b.id, "nombre": "B", "apellidos": "User B"})


@pytest.fixture
def repo(db_session: AsyncSession, test_tenant: Tenant) -> TareaRepository:
    return TareaRepository(session=db_session, tenant_id=test_tenant.id)


async def _crear_tarea(repo: TareaRepository, asignado_a: uuid.UUID, asignado_por: uuid.UUID | None = None, **overrides) -> Tarea:
    data = {
        "asignado_a": asignado_a,
        "asignado_por": asignado_por or asignado_a,
        "descripcion": "Tarea de prueba",
        "estado": TareaEstado.PENDIENTE.value,
    }
    data.update(overrides)
    return await repo.create(data)


@pytest.mark.asyncio
async def test_find_by_asignado_returns_matched(repo, test_usuario_a, test_usuario_b):
    ua = test_usuario_a.id
    ub = test_usuario_b.id
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Tarea A1")
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Tarea A2")
    await _crear_tarea(repo, asignado_a=ub, asignado_por=ub, descripcion="Tarea B1")

    results = await repo.find_by_asignado(usuario_id=ua)
    assert len(results) == 2
    assert all(r.asignado_a == ua for r in results)


@pytest.mark.asyncio
async def test_find_by_asignado_filters_by_estado(repo, test_usuario_a):
    ua = test_usuario_a.id
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, estado=TareaEstado.EN_PROGRESO.value, descripcion="Progreso")
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, estado=TareaEstado.PENDIENTE.value, descripcion="Pendiente")

    results = await repo.find_by_asignado(usuario_id=ua, estado=TareaEstado.EN_PROGRESO.value)
    assert len(results) == 1
    assert results[0].descripcion == "Progreso"


@pytest.mark.asyncio
async def test_find_by_asignado_filters_by_texto(repo, test_usuario_a):
    ua = test_usuario_a.id
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Corregir examenes")
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Preparar material")
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Revisar trabajos")

    results = await repo.find_by_asignado(usuario_id=ua, texto="corregir")
    assert len(results) == 1
    assert "corregir" in results[0].descripcion.lower()


@pytest.mark.asyncio
async def test_find_by_asignado_pagination(repo, test_usuario_a):
    ua = test_usuario_a.id
    for i in range(5):
        await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion=f"Tarea {i}")

    results = await repo.find_by_asignado(usuario_id=ua, skip=0, limit=3)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_find_all_managed_filters(repo, test_usuario_a, test_usuario_b):
    ua = test_usuario_a.id
    ub = test_usuario_b.id
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ub, estado=TareaEstado.PENDIENTE.value, descripcion="T1")
    await _crear_tarea(repo, asignado_a=ub, asignado_por=ua, estado=TareaEstado.EN_PROGRESO.value, descripcion="T2")
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ub, estado=TareaEstado.RESUELTA.value, descripcion="T3")

    results = await repo.find_all_managed(estado=TareaEstado.PENDIENTE.value)
    assert len(results) == 1
    assert results[0].descripcion == "T1"

    results2 = await repo.find_all_managed(asignado_a_id=ua)
    assert len(results2) == 2


@pytest.mark.asyncio
async def test_find_all_managed_text_search(repo, test_usuario_a):
    ua = test_usuario_a.id
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Buscar esta tarea urgente")
    await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Otra tarea cualquiera")

    results = await repo.find_all_managed(texto="urgente")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_find_all_managed_pagination(repo, test_usuario_a):
    ua = test_usuario_a.id
    for i in range(5):
        await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion=f"Tarea {i}")

    results = await repo.find_all_managed(skip=0, limit=3)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_get_with_comments_returns_task_with_comments(repo, db_session, test_tenant, test_usuario_a):
    ua = test_usuario_a.id
    tarea = await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Con comentarios")
    comentario_repo = BaseRepository(model=ComentarioTarea, session=db_session, tenant_id=test_tenant.id)
    await comentario_repo.create({"tarea_id": tarea.id, "autor_id": ua, "texto": "Primero"})
    await comentario_repo.create({"tarea_id": tarea.id, "autor_id": ua, "texto": "Segundo"})

    result = await repo.get_with_comments(tarea.id)
    assert result is not None
    assert result.id == tarea.id
    assert len(result.comentarios) == 2
    assert result.comentarios[0].texto == "Primero"
    assert result.comentarios[1].texto == "Segundo"


@pytest.mark.asyncio
async def test_get_with_comments_returns_none_for_missing(repo):
    result = await repo.get_with_comments(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_tenant_isolation(repo, db_session, another_tenant, test_usuario_a):
    repo1 = TareaRepository(session=db_session, tenant_id=repo._tenant_id)
    repo2 = TareaRepository(session=db_session, tenant_id=another_tenant.id)
    u = test_usuario_a.id
    await _crear_tarea(repo1, asignado_a=u, asignado_por=u, descripcion="T1")
    await _crear_tarea(repo2, asignado_a=u, asignado_por=u, descripcion="T2")

    t1 = await repo1.find_by_asignado(usuario_id=u)
    t2 = await repo2.find_by_asignado(usuario_id=u)
    assert len(t1) == 1
    assert len(t2) == 1
    assert t1[0].descripcion == "T1"
    assert t2[0].descripcion == "T2"


@pytest.mark.asyncio
async def test_find_all_managed_excludes_soft_deleted(repo, test_usuario_a):
    ua = test_usuario_a.id
    t = await _crear_tarea(repo, asignado_a=ua, asignado_por=ua, descripcion="Borrame")
    await repo.soft_delete(t.id)

    results = await repo.find_all_managed()
    ids = [r.id for r in results]
    assert t.id not in ids
