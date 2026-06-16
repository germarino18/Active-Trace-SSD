"""Tests for AvisoRepository."""

from datetime import UTC, datetime, timedelta
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso, AcknowledgmentAviso, AlcanceAviso, SeveridadAviso
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.user import User
from app.models.carrera import Carrera
from app.repositories.base import BaseRepository
from app.repositories.aviso_repository import AvisoRepository


_JAN2026 = datetime(2026, 1, 1, tzinfo=UTC)
_DEC2026 = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"usr-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
    })


@pytest.fixture
async def test_materia(db_session: AsyncSession, test_tenant: Tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"codigo": "MAT-AVS", "nombre": "Materia Avisos"})


@pytest.fixture
async def test_cohorte(db_session: AsyncSession, test_tenant: Tenant) -> Cohorte:
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"nombre": "Ingenieria", "codigo": "ING"})
    repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "carrera_id": carrera.id,
        "nombre": "2026",
        "anio": 2026,
    })


@pytest.fixture
def repo(db_session: AsyncSession, test_tenant: Tenant) -> AvisoRepository:
    return AvisoRepository(session=db_session, tenant_id=test_tenant.id)


async def _crear_aviso(repo, **overrides) -> Aviso:
    data = {
        "alcance": AlcanceAviso.GLOBAL.value,
        "severidad": SeveridadAviso.INFO.value,
        "titulo": "Aviso test",
        "cuerpo": "Cuerpo test",
        "inicio_en": _JAN2026,
        "fin_en": _DEC2026,
        "orden": 0,
        "activo": True,
        "requiere_ack": False,
    }
    data.update(overrides)
    return await repo.create(data)


@pytest.mark.asyncio
async def test_find_visible_global(repo):
    await _crear_aviso(repo, titulo="Global 1")
    await _crear_aviso(repo, titulo="Global 2")
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    assert len(results) == 2


@pytest.mark.asyncio
async def test_find_visible_excludes_inactive(repo):
    await _crear_aviso(repo, titulo="Activo")
    await _crear_aviso(repo, titulo="Inactivo", activo=False)
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    titles = [r.titulo for r in results]
    assert "Activo" in titles
    assert "Inactivo" not in titles


@pytest.mark.asyncio
async def test_find_visible_excludes_soft_deleted(repo):
    a = await _crear_aviso(repo, titulo="To delete")
    await repo.soft_delete(a.id)
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    assert len(results) == 0


@pytest.mark.asyncio
async def test_find_visible_respects_date_window(repo):
    past = _JAN2026 - timedelta(days=365)
    future = _JAN2026 + timedelta(days=365)
    await _crear_aviso(repo, titulo="Past", inicio_en=past - timedelta(days=30), fin_en=past)
    await _crear_aviso(repo, titulo="Current", inicio_en=_JAN2026, fin_en=_DEC2026)
    await _crear_aviso(repo, titulo="Future", inicio_en=future, fin_en=future + timedelta(days=30))
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    titles = [r.titulo for r in results]
    assert "Current" in titles
    assert "Past" not in titles
    assert "Future" not in titles


@pytest.mark.asyncio
async def test_find_visible_por_rol(repo):
    await _crear_aviso(repo, alcance=AlcanceAviso.POR_ROL.value, rol_destino="ALUMNO", titulo="Para Alumno")
    await _crear_aviso(repo, alcance=AlcanceAviso.POR_ROL.value, rol_destino="PROFESOR", titulo="Para Profesor")
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=["ALUMNO"],
        materia_ids=[],
        cohorte_ids=[],
    )
    titles = [r.titulo for r in results]
    assert "Para Alumno" in titles
    assert "Para Profesor" not in titles


@pytest.mark.asyncio
async def test_find_visible_por_materia(repo, test_materia, db_session, test_tenant):
    otro = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    other_materia = await otro.create({"codigo": "MAT-OTR", "nombre": "Otra Materia"})
    await _crear_aviso(repo, alcance=AlcanceAviso.POR_MATERIA.value, materia_id=test_materia.id, titulo="Materia Match")
    await _crear_aviso(repo, alcance=AlcanceAviso.POR_MATERIA.value, materia_id=other_materia.id, titulo="Materia Other")
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[test_materia.id],
        cohorte_ids=[],
    )
    titles = [r.titulo for r in results]
    assert "Materia Match" in titles
    assert "Materia Other" not in titles


@pytest.mark.asyncio
async def test_find_visible_por_cohorte(repo, test_cohorte, db_session, test_tenant):
    otro = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    otra_carrera = await carrera_repo.create({"nombre": "Otra", "codigo": "OTR"})
    other_cohorte = await otro.create({"carrera_id": otra_carrera.id, "nombre": "2025", "anio": 2025})
    await _crear_aviso(repo, alcance=AlcanceAviso.POR_COHORTE.value, cohorte_id=test_cohorte.id, titulo="Cohorte Match")
    await _crear_aviso(repo, alcance=AlcanceAviso.POR_COHORTE.value, cohorte_id=other_cohorte.id, titulo="Cohorte Other")
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[],
        cohorte_ids=[test_cohorte.id],
    )
    titles = [r.titulo for r in results]
    assert "Cohorte Match" in titles
    assert "Cohorte Other" not in titles


@pytest.mark.asyncio
async def test_find_visible_ordering(repo):
    for i in range(3):
        await _crear_aviso(repo, titulo=f"Order {i}", orden=i)
    results = await repo.find_visible(
        usuario_id=uuid.uuid4(),
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    assert results[0].orden <= results[1].orden <= results[2].orden


@pytest.mark.asyncio
async def test_find_pending_ack(repo, test_usuario):
    ack = await _crear_aviso(repo, titulo="Requiere ack", requiere_ack=True)
    await _crear_aviso(repo, titulo="No requiere ack", requiere_ack=False)
    results = await repo.find_pending_ack(
        usuario_id=test_usuario.id,
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    titles = [r.titulo for r in results]
    assert "Requiere ack" in titles
    assert "No requiere ack" not in titles


@pytest.mark.asyncio
async def test_find_pending_ack_excludes_already_confirmed(repo, db_session, test_tenant, test_usuario):
    a = await _crear_aviso(repo, titulo="Ya confirmado", requiere_ack=True)
    b = await _crear_aviso(repo, titulo="Pendiente", requiere_ack=True)
    ack_repo = BaseRepository(model=AcknowledgmentAviso, session=db_session, tenant_id=test_tenant.id)
    await ack_repo.create({"aviso_id": a.id, "usuario_id": test_usuario.id})
    results = await repo.find_pending_ack(
        usuario_id=test_usuario.id,
        roles=[],
        materia_ids=[],
        cohorte_ids=[],
    )
    titles = [r.titulo for r in results]
    assert "Pendiente" in titles
    assert "Ya confirmado" not in titles


@pytest.mark.asyncio
async def test_find_all_managed(repo):
    for i in range(5):
        await _crear_aviso(repo, titulo=f"Aviso {i}")
    results = await repo.find_all_managed(skip=0, limit=3)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_find_all_managed_includes_inactive(repo):
    await _crear_aviso(repo, titulo="Activo")
    await _crear_aviso(repo, titulo="Inactivo", activo=False)
    results = await repo.find_all_managed(skip=0, limit=10)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_count_acknowledgments(repo, db_session, test_tenant, test_usuario):
    a = await _crear_aviso(repo, requiere_ack=True)
    ack_repo = BaseRepository(model=AcknowledgmentAviso, session=db_session, tenant_id=test_tenant.id)
    await ack_repo.create({"aviso_id": a.id, "usuario_id": test_usuario.id})
    other = await _crear_aviso(repo, requiere_ack=False)
    stats = await repo.count_acknowledgments(a.id)
    assert stats is not None
    assert stats["total"] == 1
    assert stats["confirmados"] == 1
    assert stats["pendientes"] == 0
    stats2 = await repo.count_acknowledgments(other.id)
    assert stats2["total"] == 0
    assert stats2["confirmados"] == 0


@pytest.mark.asyncio
async def test_tenant_isolation(repo, db_session, another_tenant):
    repo2 = AvisoRepository(session=db_session, tenant_id=another_tenant.id)
    await _crear_aviso(repo, titulo="Tenant 1")
    await _crear_aviso(repo2, titulo="Tenant 2")
    t1 = await repo.find_all_managed(skip=0, limit=10)
    t2 = await repo2.find_all_managed(skip=0, limit=10)
    assert len(t1) == 1
    assert len(t2) == 1
    assert t1[0].titulo == "Tenant 1"
    assert t2[0].titulo == "Tenant 2"
