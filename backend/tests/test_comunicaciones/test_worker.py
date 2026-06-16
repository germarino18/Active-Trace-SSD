"""Tests for the worker business logic (state machine, retries, timeout).

Tests simulate what CommunicationsWorker._process_pending and
_process_stuck do, at the repository + state machine level.
"""

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
    return await repo.create({"codigo": "MAT-WRK", "nombre": "Materia Worker"})


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


async def _crear_pendiente(repo, usuario, materia) -> Comunicacion:
    return await repo.create({
        "enviado_por": usuario.id,
        "materia_id": materia.id,
        "destinatario": "alumno@test.com",
        "destinatario_hash": "hash",
        "asunto": "Notificación",
        "cuerpo": "Cuerpo del mensaje",
        "lote_id": uuid.uuid4(),
    })


@pytest.mark.asyncio
async def test_pendiente_to_enviando_to_enviado_flow(repo, test_materia, test_usuario):
    """Simulate worker _process_pending: Pendiente → Enviando → Enviado."""
    com = await _crear_pendiente(repo, test_usuario, test_materia)
    assert com.estado == ComunicacionEstado.PENDIENTE.value
    com = await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)
    assert com.estado == ComunicacionEstado.ENVIANDO.value
    com = await repo.update_estado(com.id, ComunicacionEstado.ENVIADO)
    assert com.estado == ComunicacionEstado.ENVIADO.value
    assert com.enviado_at is not None


@pytest.mark.asyncio
async def test_stuck_enviando_timeout(repo, test_materia, test_usuario, db_session):
    """Simulate worker _process_stuck: detect stale Enviando records."""
    com = await _crear_pendiente(repo, test_usuario, test_materia)
    await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)
    await db_session.execute(
        sql_text(
            "UPDATE comunicacion SET updated_at = NOW() - INTERVAL '10 minutes' WHERE id = :id"
        ),
        {"id": com.id},
    )
    await db_session.flush()
    stuck = await repo.get_stuck_enviando(timeout_minutes=5)
    assert len(stuck) == 1
    assert stuck[0].id == com.id


@pytest.mark.asyncio
async def test_stuck_enviando_reintenta(repo, test_materia, test_usuario, db_session):
    """Simulate worker retry: stuck Enviando with <3 retries → Pendiente."""
    com = await _crear_pendiente(repo, test_usuario, test_materia)
    await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO)
    await db_session.execute(
        sql_text(
            "UPDATE comunicacion SET updated_at = NOW() - INTERVAL '10 minutes' WHERE id = :id"
        ),
        {"id": com.id},
    )
    await db_session.flush()
    stuck = await repo.get_stuck_enviando(timeout_minutes=5)
    assert len(stuck) == 1
    s = stuck[0]
    assert s.reintentos == 0
    s.reintentos = s.reintentos + 1
    s.estado = ComunicacionEstado.PENDIENTE.value
    await db_session.flush()
    refreshed = await repo.find_by_id(com.id)
    assert refreshed.reintentos == 1
    assert refreshed.estado == ComunicacionEstado.PENDIENTE.value


@pytest.mark.asyncio
async def test_max_retries_marks_error(repo, test_materia, test_usuario, db_session):
    """Simulate worker max retries: 3rd retry → Error state."""
    com = await _crear_pendiente(repo, test_usuario, test_materia)
    await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO, extra={"reintentos": 2})
    await db_session.execute(
        sql_text(
            "UPDATE comunicacion SET updated_at = NOW() - INTERVAL '10 minutes' WHERE id = :id"
        ),
        {"id": com.id},
    )
    await db_session.flush()
    stuck = await repo.get_stuck_enviando(timeout_minutes=5)
    assert len(stuck) == 1
    s = stuck[0]
    assert s.reintentos == 2
    s.reintentos = s.reintentos + 1
    s.estado = ComunicacionEstado.ERROR.value
    await db_session.flush()
    refreshed = await repo.find_by_id(com.id)
    assert refreshed.reintentos == 3
    assert refreshed.estado == ComunicacionEstado.ERROR.value


@pytest.mark.asyncio
async def test_max_retries_reached_not_returned_by_get_stuck(
    repo, test_materia, test_usuario, db_session
):
    """Verify get_stuck_enviando excludes records at max retries."""
    com = await _crear_pendiente(repo, test_usuario, test_materia)
    await repo.update_estado(com.id, ComunicacionEstado.ENVIANDO, extra={"reintentos": 3})
    await db_session.execute(
        sql_text(
            "UPDATE comunicacion SET updated_at = NOW() - INTERVAL '10 minutes' WHERE id = :id"
        ),
        {"id": com.id},
    )
    await db_session.flush()
    stuck = await repo.get_stuck_enviando(timeout_minutes=5)
    assert all(c.id != com.id for c in stuck)
