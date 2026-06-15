import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository


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


# ── VersionPadronRepository ────────────────────────────────────────────


async def test_version_padron_repo_create_and_find(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    version = await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    found = await repo.find_by_id(version.id)
    assert found is not None
    assert found.id == version.id


async def test_version_padron_repo_find_active_by_dictado(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    v1 = await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })
    await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": False,
    })

    active = await repo.find_active_by_dictado(dictado.id)
    assert active is not None
    assert active.id == v1.id
    assert active.activa is True


async def test_version_padron_repo_find_active_returns_none_when_none_active(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": False,
    })

    active = await repo.find_active_by_dictado(dictado.id)
    assert active is None


async def test_version_padron_repo_find_by_dictado(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })
    await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": False,
    })

    versions = await repo.find_by_dictado(dictado.id)
    assert len(versions) == 2


async def test_version_padron_repo_deactivate_version(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    version = await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    updated = await repo.deactivate_version(version.id)
    assert updated.activa is False

    found = await repo.find_by_id(version.id)
    assert found.activa is False


async def test_version_padron_repo_delete_by_dictado_and_cargador(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    deleted = await repo.delete_by_dictado_and_cargador(dictado.id, usuario.id)
    assert deleted > 0

    remaining = await repo.find_by_dictado(dictado.id)
    assert len(remaining) == 0


async def test_version_padron_repo_delete_all_by_dictado(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)

    await repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    deleted = await repo.delete_all_by_dictado(dictado.id)
    assert deleted > 0

    remaining = await repo.find_by_dictado(dictado.id)
    assert len(remaining) == 0


async def test_version_padron_repo_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant
):
    usuario_a = await _create_usuario(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    usuario_b = await _create_usuario(db_session, another_tenant.id)
    dictado_b = await _create_dictado(db_session, another_tenant.id)

    repo_a = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    await repo_a.create({
        "dictado_id": dictado_a.id,
        "cargado_por": usuario_a.id,
        "activa": True,
    })

    repo_b = VersionPadronRepository(session=db_session, tenant_id=another_tenant.id)
    await repo_b.create({
        "dictado_id": dictado_b.id,
        "cargado_por": usuario_b.id,
        "activa": True,
    })

    all_a = await repo_a.find_all()
    assert len(all_a) == 1
    assert all_a[0].tenant_id == test_tenant.id


# ── EntradaPadronRepository ────────────────────────────────────────────


async def test_entrada_padron_repo_bulk_create(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    entries = await ep_repo.bulk_create([
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez"},
        {"version_id": version.id, "nombre": "María", "apellidos": "García", "comision": "A"},
    ])

    assert len(entries) == 2
    assert entries[0].nombre == "Juan"
    assert entries[1].nombre == "María"


async def test_entrada_padron_repo_find_by_version(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    await ep_repo.bulk_create([
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez"},
        {"version_id": version.id, "nombre": "Ana", "apellidos": "López"},
    ])

    found = await ep_repo.find_by_version(version.id)
    assert len(found) == 2


async def test_entrada_padron_repo_count_by_version(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    await ep_repo.bulk_create([
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez"},
        {"version_id": version.id, "nombre": "Ana", "apellidos": "López"},
        {"version_id": version.id, "nombre": "Luis", "apellidos": "Martínez"},
    ])

    count = await ep_repo.count_by_version(version.id)
    assert count == 3


async def test_entrada_padron_repo_delete_by_version(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    await ep_repo.bulk_create([
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez"},
    ])

    deleted = await ep_repo.delete_by_version(version.id)
    assert deleted > 0

    count = await ep_repo.count_by_version(version.id)
    assert count == 0


async def test_entrada_padron_repo_find_by_version_empty_when_no_entries(
    db_session: AsyncSession, test_tenant
):
    dictado = await _create_dictado(db_session, test_tenant.id)
    usuario = await _create_usuario(db_session, test_tenant.id)
    vp_repo = VersionPadronRepository(session=db_session, tenant_id=test_tenant.id)
    version = await vp_repo.create({
        "dictado_id": dictado.id,
        "cargado_por": usuario.id,
        "activa": True,
    })

    ep_repo = EntradaPadronRepository(session=db_session, tenant_id=test_tenant.id)
    found = await ep_repo.find_by_version(version.id)
    assert found == []
