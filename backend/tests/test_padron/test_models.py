import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository


async def _create_usuario(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create({
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test Cargador",
        "is_active": True,
        "roles": [],
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "Cargador",
        "estado": "Activo",
    })


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


async def test_version_padron_persists_with_tenant_and_dictado(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)

    version = await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    assert version.id is not None
    assert version.tenant_id == test_tenant.id
    assert version.dictado_id == dictado.id
    assert version.cargado_por == usuario.id
    assert version.activa is True
    assert version.cargado_at is not None


async def test_version_padron_unique_active_per_dictado(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)

    v1 = await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })
    assert v1.activa is True

    # Deactivate v1, create v2 active
    v1.activa = False
    await db_session.flush()

    v2 = await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })
    assert v2.id != v1.id
    assert v2.activa is True


async def test_version_padron_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant
):
    usuario_a = await _create_usuario(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    repo_a = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
    await repo_a.create({
        "dictado_id": dictado_a.id,
        "cargado_por": usuario_a.id,
        "activa": True,
    })

    usuario_b = await _create_usuario(db_session, another_tenant.id)
    dictado_b = await _create_dictado(db_session, another_tenant.id)
    repo_b = BaseRepository(model=VersionPadron, session=db_session, tenant_id=another_tenant.id)
    await repo_b.create({
        "dictado_id": dictado_b.id,
        "cargado_por": usuario_b.id,
        "activa": True,
    })

    all_a = await repo_a.find_all()
    assert len(all_a) == 1
    for v in all_a:
        assert v.tenant_id == test_tenant.id


async def test_entrada_padron_persists_with_version_fk(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
    entrada = await ep_repo.create({
        "version_id": version.id,
        "nombre": "Juan",
        "apellidos": "Pérez",
        "email": "juan@example.com",
        "comision": "A",
        "regional": "CABA",
    })

    assert entrada.id is not None
    assert entrada.tenant_id == test_tenant.id
    assert entrada.version_id == version.id
    assert entrada.nombre == "Juan"
    assert entrada.apellidos == "Pérez"
    assert entrada.email == "juan@example.com"
    assert entrada.comision == "A"
    assert entrada.regional == "CABA"


async def test_entrada_padron_nullable_fields(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=test_tenant.id)
    entrada = await ep_repo.create({
        "version_id": version.id,
        "nombre": "María",
        "apellidos": "García",
    })

    assert entrada.email is None
    assert entrada.comision is None
    assert entrada.regional is None
    assert entrada.usuario_id is None


async def test_version_padron_partial_index_allows_two_active_across_tenants(
    db_session: AsyncSession, test_tenant, another_tenant
):
    usuario_a = await _create_usuario(db_session, test_tenant.id)
    usuario_b = await _create_usuario(db_session, another_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    dictado_b = await _create_dictado(db_session, another_tenant.id)

    repo_a = BaseRepository(model=VersionPadron, session=db_session, tenant_id=test_tenant.id)
    v1 = await repo_a.create({
        "dictado_id": dictado_a.id,
        "cargado_por": usuario_a.id,
        "activa": True,
    })
    assert v1.id is not None

    repo_b = BaseRepository(model=VersionPadron, session=db_session, tenant_id=another_tenant.id)
    v2 = await repo_b.create({
        "dictado_id": dictado_b.id,
        "cargado_por": usuario_b.id,
        "activa": True,
    })
    assert v2.id is not None
