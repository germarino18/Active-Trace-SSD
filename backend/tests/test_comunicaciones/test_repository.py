"""Tests for ComunicacionRepository."""

import hashlib
import uuid

import pytest
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion, ComunicacionEstado
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.repositories.comunicacion_repository import ComunicacionRepository


@pytest.fixture
async def test_materia(db_session: AsyncSession, test_tenant: Tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"codigo": "MAT-COM", "nombre": "Comunicaciones Test"})


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"prof-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Profesor",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Profesor",
        "apellidos": "Test",
    })


@pytest.fixture
def repo(db_session: AsyncSession, test_tenant: Tenant) -> ComunicacionRepository:
    return ComunicacionRepository(session=db_session, tenant_id=test_tenant.id)


async def _crear_comunicacion(repo, usuario, materia, **overrides) -> Comunicacion:
    data = {
        "enviado_por": usuario.id,
        "materia_id": materia.id,
        "destinatario": "alumno@test.com",
        "destinatario_hash": hashlib.sha256(b"alumno@test.com").hexdigest(),
        "asunto": "Notificación",
        "cuerpo": "Cuerpo del mensaje",
        "lote_id": uuid.uuid4(),
    }
    data.update(overrides)
    return await repo.create(data)


@pytest.mark.asyncio
async def test_create(repo, test_materia, test_usuario):
    com = await _crear_comunicacion(repo, test_usuario, test_materia)
    assert com.id is not None
    assert com.tenant_id is not None
    assert com.estado == ComunicacionEstado.PENDIENTE
    assert com.destinatario == "alumno@test.com"
    assert com.asunto == "Notificación"
    assert com.enviado_at is None
    assert com.reintentos == 0


@pytest.mark.asyncio
async def test_get_by_id(repo, test_materia, test_usuario):
    com = await _crear_comunicacion(repo, test_usuario, test_materia)
    found = await repo.find_by_id(com.id)
    assert found is not None
    assert found.id == com.id
    assert found.asunto == com.asunto


@pytest.mark.asyncio
async def test_get_by_lote(repo, test_materia, test_usuario):
    lote_id = uuid.uuid4()
    for i in range(3):
        await _crear_comunicacion(
            repo, test_usuario, test_materia, lote_id=lote_id, asunto=f"Msg {i}"
        )
    results = await repo.get_by_lote(lote_id)
    assert len(results) == 3
    assert all(c.lote_id == lote_id for c in results)


@pytest.mark.asyncio
async def test_get_by_lote_empty(repo):
    results = await repo.get_by_lote(uuid.uuid4())
    assert results == []


@pytest.mark.asyncio
async def test_get_pendientes(repo, test_materia, test_usuario):
    await _crear_comunicacion(repo, test_usuario, test_materia)
    await _crear_comunicacion(
        repo, test_usuario, test_materia, estado=ComunicacionEstado.ENVIADO.value,
    )
    pendientes = await repo.get_pendientes()
    assert len(pendientes) == 1
    assert pendientes[0].estado == ComunicacionEstado.PENDIENTE.value


@pytest.mark.asyncio
async def test_get_pendientes_respects_limit(repo, test_materia, test_usuario):
    for _ in range(5):
        await _crear_comunicacion(repo, test_usuario, test_materia)
    result = await repo.get_pendientes(limit=3)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_update_estado_transitions(repo, test_materia, test_usuario):
    com = await _crear_comunicacion(repo, test_usuario, test_materia)
    assert com.estado == ComunicacionEstado.PENDIENTE.value
    com = await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)
    assert com.estado == ComunicacionEstado.ENVIANDO.value
    com = await repo.update_estado(com.id, ComunicacionEstado.ENVIADO)
    assert com.estado == ComunicacionEstado.ENVIADO.value
    com = await repo.update_estado(com.id, ComunicacionEstado.ERROR)
    assert com.estado == ComunicacionEstado.ERROR.value
    com = await repo.update_estado(com.id, ComunicacionEstado.CANCELADO)
    assert com.estado == ComunicacionEstado.CANCELADO.value


@pytest.mark.asyncio
async def test_update_estado_sets_enviado_at(repo, test_materia, test_usuario):
    com = await _crear_comunicacion(repo, test_usuario, test_materia)
    com = await repo.update_estado(com.id, ComunicacionEstado.ENVIADO)
    assert com.enviado_at is not None


@pytest.mark.asyncio
async def test_count_by_lote(repo, test_materia, test_usuario):
    lote_id = uuid.uuid4()
    c1 = await _crear_comunicacion(repo, test_usuario, test_materia, lote_id=lote_id)
    c2 = await _crear_comunicacion(repo, test_usuario, test_materia, lote_id=lote_id)
    c3 = await _crear_comunicacion(repo, test_usuario, test_materia, lote_id=lote_id)
    await repo.update_estado(c2.id, ComunicacionEstado.ENVIADO)
    await repo.update_estado(c3.id, ComunicacionEstado.ERROR)
    counts = await repo.count_by_lote(lote_id)
    assert counts["total"] == 3
    assert counts["Pendiente"] == 1
    assert counts["Enviado"] == 1
    assert counts["Error"] == 1
    assert counts["Cancelado"] == 0


@pytest.mark.asyncio
async def test_get_pendientes_count(repo, test_materia, test_usuario):
    c1 = await _crear_comunicacion(repo, test_usuario, test_materia)
    c2 = await _crear_comunicacion(repo, test_usuario, test_materia)
    await repo.update_estado(c2.id, ComunicacionEstado.ENVIADO)
    count = await repo.get_pendientes_count()
    assert count == 1


@pytest.mark.asyncio
async def test_get_stuck_enviando(db_session, repo, test_materia, test_usuario):
    recent = await _crear_comunicacion(repo, test_usuario, test_materia)
    await repo.update_estado(recent.id, ComunicacionEstado.ENVIANDO)

    stuck = await _crear_comunicacion(repo, test_usuario, test_materia)
    await repo.update_estado(stuck.id, ComunicacionEstado.ENVIANDO)
    await db_session.execute(
        sql_text(
            "UPDATE comunicacion SET updated_at = NOW() - INTERVAL '10 minutes' WHERE id = :id"
        ),
        {"id": stuck.id},
    )
    await db_session.flush()

    result = await repo.get_stuck_enviando(timeout_minutes=5)
    ids = [c.id for c in result]
    assert stuck.id in ids
    assert recent.id not in ids


@pytest.mark.asyncio
async def test_get_stuck_enviando_skips_max_retries(db_session, repo, test_materia, test_usuario):
    com = await _crear_comunicacion(repo, test_usuario, test_materia)
    await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO, extra={"reintentos": 3})
    await db_session.execute(
        sql_text(
            "UPDATE comunicacion SET updated_at = NOW() - INTERVAL '10 minutes' WHERE id = :id"
        ),
        {"id": com.id},
    )
    await db_session.flush()
    result = await repo.get_stuck_enviando(timeout_minutes=5)
    assert all(c.id != com.id for c in result)


@pytest.mark.asyncio
async def test_tenant_isolation(db_session, test_tenant, another_tenant):
    m_repo1 = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    m1 = await m_repo1.create({"codigo": "MT1", "nombre": "Materia T1"})
    u_repo1 = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    u1 = await u_repo1.create({
        "email": f"u1-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "h",
        "display_name": "U1",
    })
    us_repo1 = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    us1 = await us_repo1.create({"user_id": u1.id, "nombre": "U1", "apellidos": "T1"})

    m_repo2 = BaseRepository(model=Materia, session=db_session, tenant_id=another_tenant.id)
    m2 = await m_repo2.create({"codigo": "MT2", "nombre": "Materia T2"})
    u_repo2 = BaseRepository(model=User, session=db_session, tenant_id=another_tenant.id)
    u2 = await u_repo2.create({
        "email": f"u2-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "h",
        "display_name": "U2",
    })
    us_repo2 = BaseRepository(model=Usuario, session=db_session, tenant_id=another_tenant.id)
    us2 = await us_repo2.create({"user_id": u2.id, "nombre": "U2", "apellidos": "T2"})

    lote = uuid.uuid4()
    repo1 = ComunicacionRepository(session=db_session, tenant_id=test_tenant.id)
    repo2 = ComunicacionRepository(session=db_session, tenant_id=another_tenant.id)

    await _crear_comunicacion(repo1, us1, m1, lote_id=lote)
    await _crear_comunicacion(repo2, us2, m2, lote_id=lote)

    t1_results = await repo1.get_by_lote(lote)
    t2_results = await repo2.get_by_lote(lote)

    assert len(t1_results) == 1
    assert len(t2_results) == 1
    assert t1_results[0].destinatario == "alumno@test.com"
    assert t2_results[0].destinatario == "alumno@test.com"
