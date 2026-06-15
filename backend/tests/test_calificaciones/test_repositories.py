import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenancy import TenantContext
from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository


# ── Helpers ─────────────────────────────────────────────────────────────


async def _create_usuario(
    db_session: AsyncSession, tenant_id: uuid.UUID,
) -> Usuario:
    from app.models.user import User
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create({
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
        "is_active": True,
        "roles": [],
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
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


async def _create_version_padron(
    db_session: AsyncSession, tenant_id: uuid.UUID, dictado_id: uuid.UUID, usuario_id: uuid.UUID
) -> VersionPadron:
    repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=tenant_id)
    return await repo.create({
        "dictado_id": dictado_id,
        "cargado_por": usuario_id,
        "activa": True,
    })


async def _create_entrada_padron(
    db_session: AsyncSession, tenant_id: uuid.UUID, version_id: uuid.UUID
) -> EntradaPadron:
    repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=tenant_id)
    return await repo.create({
        "version_id": version_id,
        "nombre": "Juan",
        "apellidos": "Pérez",
    })


async def _create_asignacion(
    db_session: AsyncSession, tenant_id: uuid.UUID, usuario_id: uuid.UUID, dictado_id: uuid.UUID
) -> Asignacion:
    from datetime import date
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    return await repo.create({
        "usuario_id": usuario_id,
        "rol": "PROFESOR",
        "dictado_id": dictado_id,
        "desde": date(2024, 1, 1),
    })


# ── CalificacionRepository ──────────────────────────────────────────────


async def test_calificacion_repo_bulk_create(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version = await _create_version_padron(db_session, test_tenant.id, dictado.id, usuario.id)
    entrada = await _create_entrada_padron(db_session, test_tenant.id, version.id)

    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    entries = await repo.bulk_create([
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "Parcial 1", "nota_numerica": 85, "aprobado": True},
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "TP 1", "nota_numerica": 60, "aprobado": True},
    ])

    assert len(entries) == 2
    assert entries[0].actividad == "Parcial 1"
    assert entries[1].actividad == "TP 1"
    assert entries[0].tenant_id == test_tenant.id


async def test_calificacion_repo_bulk_create_empty(
    db_session: AsyncSession, test_tenant
):
    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    entries = await repo.bulk_create([])
    assert entries == []


async def test_calificacion_repo_find_by_dictado(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version = await _create_version_padron(db_session, test_tenant.id, dictado.id, usuario.id)
    entrada = await _create_entrada_padron(db_session, test_tenant.id, version.id)

    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.bulk_create([
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "Parcial 1", "nota_numerica": 85, "aprobado": True},
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "TP 1", "nota_numerica": 60, "aprobado": True},
    ])

    found = await repo.find_by_dictado(dictado.id)
    assert len(found) == 2


async def test_calificacion_repo_find_by_dictado_empty_when_no_match(
    db_session: AsyncSession, test_tenant
):
    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_dictado(uuid.uuid4())
    assert found == []


async def test_calificacion_repo_find_by_dictado_scoped_to_tenant(
    db_session: AsyncSession, test_tenant, another_tenant
):
    usuario_a = await _create_usuario(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    version_a = await _create_version_padron(db_session, test_tenant.id, dictado_a.id, usuario_a.id)
    entrada_a = await _create_entrada_padron(db_session, test_tenant.id, version_a.id)

    repo_a = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo_a.bulk_create([
        {"entrada_padron_id": entrada_a.id, "dictado_id": dictado_a.id, "actividad": "Parcial", "nota_numerica": 90, "aprobado": True},
    ])

    repo_b = CalificacionRepository(session=db_session, tenant_id=another_tenant.id)
    found = await repo_b.find_by_dictado(dictado_a.id)
    assert found == []


async def test_calificacion_repo_find_by_dictado_and_entrada(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version = await _create_version_padron(db_session, test_tenant.id, dictado.id, usuario.id)
    entrada_1 = await _create_entrada_padron(db_session, test_tenant.id, version.id)
    entrada_2 = await _create_entrada_padron(db_session, test_tenant.id, version.id)

    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.bulk_create([
        {"entrada_padron_id": entrada_1.id, "dictado_id": dictado.id, "actividad": "Parcial 1", "nota_numerica": 85, "aprobado": True},
        {"entrada_padron_id": entrada_1.id, "dictado_id": dictado.id, "actividad": "TP 1", "nota_numerica": 60, "aprobado": True},
        {"entrada_padron_id": entrada_2.id, "dictado_id": dictado.id, "actividad": "Parcial 1", "nota_numerica": 45, "aprobado": False},
    ])

    found = await repo.find_by_dictado_and_entrada(dictado.id, entrada_1.id)
    assert len(found) == 2
    assert all(c.entrada_padron_id == entrada_1.id for c in found)

    found_2 = await repo.find_by_dictado_and_entrada(dictado.id, entrada_2.id)
    assert len(found_2) == 1


async def test_calificacion_repo_find_by_dictado_and_entrada_empty(
    db_session: AsyncSession, test_tenant
):
    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_dictado_and_entrada(uuid.uuid4(), uuid.uuid4())
    assert found == []


async def test_calificacion_repo_recalcular_aprobado_numerica(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version = await _create_version_padron(db_session, test_tenant.id, dictado.id, usuario.id)
    entrada = await _create_entrada_padron(db_session, test_tenant.id, version.id)

    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.bulk_create([
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "Parcial", "nota_numerica": 85, "aprobado": False},
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "TP", "nota_numerica": 40, "aprobado": True},
    ])

    updated = await repo.recalcular_aprobado_por_dictado(dictado.id, umbral_pct=60)
    assert updated == 2

    califs = await repo.find_by_dictado(dictado.id)
    califs_by_act = {c.actividad: c for c in califs}
    assert califs_by_act["Parcial"].aprobado is True    # 85 >= 60
    assert califs_by_act["TP"].aprobado is False         # 40 < 60


async def test_calificacion_repo_recalcular_aprobado_textual(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version = await _create_version_padron(db_session, test_tenant.id, dictado.id, usuario.id)
    entrada = await _create_entrada_padron(db_session, test_tenant.id, version.id)

    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.bulk_create([
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "TP 1", "nota_textual": "Aprobado", "aprobado": False},
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "TP 2", "nota_textual": "Desaprobado", "aprobado": True},
    ])

    updated = await repo.recalcular_aprobado_por_dictado(
        dictado.id, umbral_pct=60, valores_aprobatorios=["Aprobado", "Promocionado"]
    )
    assert updated == 2

    califs = await repo.find_by_dictado(dictado.id)
    califs_by_act = {c.actividad: c for c in califs}
    assert califs_by_act["TP 1"].aprobado is True    # "Aprobado" in valores
    assert califs_by_act["TP 2"].aprobado is False    # "Desaprobado" not in valores


async def test_calificacion_repo_recalcular_aprobado_both_numerica_and_textual(
    db_session: AsyncSession, test_tenant
):
    """If both nota_numerica and nota_textual exist, either condition can make aprobado=True."""
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    version = await _create_version_padron(db_session, test_tenant.id, dictado.id, usuario.id)
    entrada = await _create_entrada_padron(db_session, test_tenant.id, version.id)

    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.bulk_create([
        # nota_numerica < umbral BUT nota_textual in valores → aprobado
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "Recup", "nota_numerica": 30, "nota_textual": "Aprobado", "aprobado": False},
        # nota_numerica >= umbral → aprobado (nota_textual irrelevant)
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "Parcial", "nota_numerica": 80, "nota_textual": "Mal", "aprobado": False},
        # Both fail
        {"entrada_padron_id": entrada.id, "dictado_id": dictado.id, "actividad": "TP", "nota_numerica": 20, "nota_textual": "Mal", "aprobado": True},
    ])

    updated = await repo.recalcular_aprobado_por_dictado(
        dictado.id, umbral_pct=60, valores_aprobatorios=["Aprobado"]
    )
    assert updated == 3

    califs = await repo.find_by_dictado(dictado.id)
    califs_by_act = {c.actividad: c for c in califs}
    assert califs_by_act["Recup"].aprobado is True   # textual match
    assert califs_by_act["Parcial"].aprobado is True  # numerica >= umbral
    assert califs_by_act["TP"].aprobado is False       # both fail


async def test_calificacion_repo_recalcular_aprobado_no_calificaciones(
    db_session: AsyncSession, test_tenant
):
    repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    updated = await repo.recalcular_aprobado_por_dictado(uuid.uuid4(), umbral_pct=60)
    assert updated == 0


async def test_calificacion_repo_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant
):
    usuario_a = await _create_usuario(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    version_a = await _create_version_padron(db_session, test_tenant.id, dictado_a.id, usuario_a.id)
    entrada_a = await _create_entrada_padron(db_session, test_tenant.id, version_a.id)

    repo_a = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo_a.bulk_create([
        {"entrada_padron_id": entrada_a.id, "dictado_id": dictado_a.id, "actividad": "Parcial", "nota_numerica": 90, "aprobado": True},
    ])

    repo_b = CalificacionRepository(session=db_session, tenant_id=another_tenant.id)
    all_b = await repo_b.find_all()
    assert len(all_b) == 0

    all_a = await repo_a.find_all()
    assert len(all_a) == 1


# ── UmbralMateriaRepository ────────────────────────────────────────────


async def test_umbral_repo_upsert_creates(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)

    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    umbral = await repo.upsert(
        asignacion_id=asignacion.id,
        dictado_id=dictado.id,
        umbral_pct=70,
        valores_aprobatorios=["Aprobado", "Promocionado"],
    )

    assert umbral.umbral_pct == 70
    assert umbral.valores_aprobatorios == ["Aprobado", "Promocionado"]
    assert umbral.asignacion_id == asignacion.id
    assert umbral.dictado_id == dictado.id


async def test_umbral_repo_upsert_updates(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)

    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    first = await repo.upsert(
        asignacion_id=asignacion.id,
        dictado_id=dictado.id,
        umbral_pct=60,
    )
    assert first.umbral_pct == 60

    second = await repo.upsert(
        asignacion_id=asignacion.id,
        dictado_id=dictado.id,
        umbral_pct=80,
        valores_aprobatorios=["Promocionado"],
    )
    assert second.umbral_pct == 80
    assert second.valores_aprobatorios == ["Promocionado"]
    assert second.id == first.id  # same row


async def test_umbral_repo_find_by_asignacion_dictado(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)

    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.upsert(asignacion_id=asignacion.id, dictado_id=dictado.id, umbral_pct=75)

    found = await repo.find_by_asignacion_dictado(asignacion.id, dictado.id)
    assert found is not None
    assert found.umbral_pct == 75


async def test_umbral_repo_find_by_asignacion_dictado_returns_none_when_missing(
    db_session: AsyncSession, test_tenant
):
    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_asignacion_dictado(uuid.uuid4(), uuid.uuid4())
    assert found is None


async def test_umbral_repo_delete(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)

    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.upsert(asignacion_id=asignacion.id, dictado_id=dictado.id, umbral_pct=60)

    deleted = await repo.delete(asignacion.id, dictado.id)
    assert deleted is True

    found = await repo.find_by_asignacion_dictado(asignacion.id, dictado.id)
    assert found is None


async def test_umbral_repo_delete_not_found(
    db_session: AsyncSession, test_tenant
):
    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    deleted = await repo.delete(uuid.uuid4(), uuid.uuid4())
    assert deleted is False


async def test_umbral_repo_tenant_isolation(
    db_session: AsyncSession, test_tenant, another_tenant
):
    usuario_a = await _create_usuario(db_session, test_tenant.id)
    dictado_a = await _create_dictado(db_session, test_tenant.id)
    asignacion_a = await _create_asignacion(db_session, test_tenant.id, usuario_a.id, dictado_a.id)

    repo_a = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo_a.upsert(asignacion_id=asignacion_a.id, dictado_id=dictado_a.id, umbral_pct=60)

    repo_b = UmbralMateriaRepository(session=db_session, tenant_id=another_tenant.id)
    found_b = await repo_b.find_by_asignacion_dictado(asignacion_a.id, dictado_a.id)
    assert found_b is None


async def test_umbral_repo_upsert_minimal(
    db_session: AsyncSession, test_tenant
):
    usuario = await _create_usuario(db_session, test_tenant.id)
    dictado = await _create_dictado(db_session, test_tenant.id)
    asignacion = await _create_asignacion(db_session, test_tenant.id, usuario.id, dictado.id)

    repo = UmbralMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    umbral = await repo.upsert(
        asignacion_id=asignacion.id,
        dictado_id=dictado.id,
        umbral_pct=60,
    )

    assert umbral.umbral_pct == 60
    assert umbral.valores_aprobatorios is None
