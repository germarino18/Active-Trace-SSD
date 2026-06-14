"""Model tests for `Asignacion` (C-07 task group 3).

`Asignacion` links a `Usuario` to a `rol` within an optional academic
context (`dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`, all NULL =
tenant-global role), with a supervisory `responsable_id` and a validity
window `desde`/`hasta`. `estado_vigencia` is derived (D3), NOT stored.
"""

import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.services.auth.password_service import PasswordService


async def _make_usuario(db_session: AsyncSession, tenant_id, email):
    pw = PasswordService()
    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=pw.hash_password("Password123!"),
        display_name=email,
        roles=[],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await usuario_repo.create({"user_id": user.id, "nombre": "N", "apellidos": "A"})


# ── 3.1 RED: shape of Asignacion ─────────────────────────────────────────


async def test_asignacion_persists_with_expected_columns(db_session: AsyncSession, test_tenant):
    usuario = await _make_usuario(db_session, test_tenant.id, "asig1@example.com")
    responsable = await _make_usuario(db_session, test_tenant.id, "resp1@example.com")
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)

    hoy = datetime.date.today()
    asignacion = await repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "PROFESOR",
            "dictado_id": None,
            "materia_id": None,
            "carrera_id": None,
            "cohorte_id": None,
            "comisiones": ["A", "B"],
            "responsable_id": responsable.id,
            "desde": hoy - datetime.timedelta(days=30),
            "hasta": None,
        }
    )

    assert asignacion.id is not None
    assert asignacion.tenant_id == test_tenant.id
    assert asignacion.usuario_id == usuario.id
    assert asignacion.rol == "PROFESOR"
    assert asignacion.dictado_id is None
    assert asignacion.materia_id is None
    assert asignacion.carrera_id is None
    assert asignacion.cohorte_id is None
    assert asignacion.comisiones == ["A", "B"]
    assert asignacion.responsable_id == responsable.id
    assert asignacion.hasta is None
    assert asignacion.deleted_at is None
    assert not hasattr(Asignacion, "estado_vigencia")


async def test_asignacion_comisiones_defaults_to_empty_list(
    db_session: AsyncSession, test_tenant
):
    usuario = await _make_usuario(db_session, test_tenant.id, "asig2@example.com")
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)

    asignacion = await repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "ALUMNO",
            "desde": datetime.date.today(),
        }
    )

    assert asignacion.comisiones == []
    assert asignacion.responsable_id is None
    assert asignacion.hasta is None


# ── 3.3 TRIANGULATE: NEXO role + tenant-global vs partial context ────────


async def test_asignacion_rol_nexo_persists(db_session: AsyncSession, test_tenant):
    usuario = await _make_usuario(db_session, test_tenant.id, "asig3@example.com")
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)

    asignacion = await repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "NEXO",
            "desde": datetime.date.today(),
        }
    )

    assert asignacion.rol == "NEXO"


async def test_asignacion_all_null_context_is_tenant_global(
    db_session: AsyncSession, test_tenant
):
    usuario = await _make_usuario(db_session, test_tenant.id, "asig4@example.com")
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)

    asignacion = await repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "ADMIN",
            "desde": datetime.date.today(),
        }
    )

    assert asignacion.dictado_id is None
    assert asignacion.materia_id is None
    assert asignacion.carrera_id is None
    assert asignacion.cohorte_id is None


async def test_asignacion_partial_context_persists(db_session: AsyncSession, test_tenant):
    from app.models.carrera import Carrera

    usuario = await _make_usuario(db_session, test_tenant.id, "asig5@example.com")
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=test_tenant.id)
    asignacion = await repo.create(
        {
            "usuario_id": usuario.id,
            "rol": "COORDINADOR",
            "carrera_id": carrera.id,
            "desde": datetime.date.today(),
        }
    )

    assert asignacion.carrera_id == carrera.id
    assert asignacion.materia_id is None
    assert asignacion.dictado_id is None
    assert asignacion.cohorte_id is None
