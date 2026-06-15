"""Tests for new `AsignacionRepository` methods (C-08 task group 2).

Real ephemeral test DB (no DB mocks, regla dura #4). All queries scope by
`tenant_id` (D4) and `deleted_at IS NULL` (soft-delete, regla dura #13).
`estado_vigencia` (Vigente|Vencida) is derived by dates (D3), never stored.
"""

import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.base import BaseRepository
from tests.test_equipos.conftest import make_usuario_perfil

_HOY = datetime.date.today()


async def _make_asignacion(
    db_session, tenant_id, usuario_id, rol, *, materia_id=None, carrera_id=None,
    cohorte_id=None, desde, hasta=None, responsable_id=None, comisiones=None,
):
    repo = BaseRepository(model=Asignacion, session=db_session, tenant_id=tenant_id)
    data = {
        "usuario_id": usuario_id,
        "rol": rol,
        "materia_id": materia_id,
        "carrera_id": carrera_id,
        "cohorte_id": cohorte_id,
        "desde": desde,
        "hasta": hasta,
        "responsable_id": responsable_id,
    }
    if comisiones is not None:
        data["comisiones"] = comisiones
    return await repo.create(data)


# ── 2.1 RED / 2.2 GREEN: find_mis_equipos_vigentes ───────────────────────


async def test_find_mis_equipos_vigentes_returns_only_vigentes_of_user(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.find_mis_equipos_vigentes(test_tenant.id, usuario.id, filtros={})

    assert len(rows) == 1
    assert rows[0].usuario_id == usuario.id
    assert rows[0].rol == "PROFESOR"


async def test_find_mis_equipos_vigentes_excludes_other_user(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    otro = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")
    await _make_asignacion(
        db_session, test_tenant.id, otro.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.find_mis_equipos_vigentes(test_tenant.id, usuario.id, filtros={})

    assert rows == []


# ── 2.3 TRIANGULATE: vencidas excluidas y filtros materia/rol ────────────


async def test_find_mis_equipos_vigentes_excludes_vencidas(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=60),
        hasta=_HOY - datetime.timedelta(days=1),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.find_mis_equipos_vigentes(test_tenant.id, usuario.id, filtros={})

    assert rows == []


async def test_find_mis_equipos_vigentes_applies_materia_and_rol_filters(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)

    materia_repo = BaseRepository(model=__import__("app.models.materia", fromlist=["Materia"]).Materia, session=db_session, tenant_id=test_tenant.id)
    materia_a = await materia_repo.create({"codigo": "MAT-A", "nombre": "Materia A"})
    materia_b = await materia_repo.create({"codigo": "MAT-B", "nombre": "Materia B"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia_a.id,
        desde=_HOY - datetime.timedelta(days=10),
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "TUTOR",
        materia_id=materia_b.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)

    rows_by_materia = await repo.find_mis_equipos_vigentes(
        test_tenant.id, usuario.id, filtros={"materia_id": materia_a.id}
    )
    assert len(rows_by_materia) == 1
    assert rows_by_materia[0].materia_id == materia_a.id

    rows_by_rol = await repo.find_mis_equipos_vigentes(
        test_tenant.id, usuario.id, filtros={"rol": "TUTOR"}
    )
    assert len(rows_by_rol) == 1
    assert rows_by_rol[0].rol == "TUTOR"


# ── 2.4 RED+GREEN+TRIANGULATE: find_by_filtros (listado del tenant) ─────


async def test_find_by_filtros_returns_tenant_asignaciones(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.find_by_filtros(test_tenant.id, filtros={})

    assert len(rows) == 1
    assert rows[0].usuario_id == usuario.id


async def test_find_by_filtros_filters_by_responsable(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    responsable = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
        responsable_id=responsable.id,
    )
    await _make_asignacion(
        db_session, test_tenant.id, responsable.id, "COORDINADOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.find_by_filtros(test_tenant.id, filtros={"responsable_id": responsable.id})

    assert len(rows) == 1
    assert rows[0].usuario_id == usuario.id
    assert rows[0].responsable_id == responsable.id


async def test_find_by_filtros_excludes_soft_deleted(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    asignacion = await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.soft_delete(asignacion.id)

    rows = await repo.find_by_filtros(test_tenant.id, filtros={})
    assert rows == []


# ── 2.5 RED+GREEN+TRIANGULATE: find_equipo (por tripleta) ────────────────


async def test_find_equipo_returns_alive_asignaciones_of_tripleta(
    db_session: AsyncSession, test_tenant, plain_user
):
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia

    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)

    materia = await materia_repo.create({"codigo": "MAT-X", "nombre": "Materia X"})
    carrera = await carrera_repo.create({"codigo": "CAR-X", "nombre": "Carrera X"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-1"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
        hasta=_HOY - datetime.timedelta(days=1),  # vencida
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.find_equipo(test_tenant.id, materia.id, carrera.id, cohorte.id)

    assert len(rows) == 1
    assert rows[0].usuario_id == usuario.id


async def test_find_equipo_solo_vigentes_excludes_vencidas(
    db_session: AsyncSession, test_tenant, plain_user
):
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia

    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)

    materia = await materia_repo.create({"codigo": "MAT-Y", "nombre": "Materia Y"})
    carrera = await carrera_repo.create({"codigo": "CAR-Y", "nombre": "Carrera Y"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-2"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
        hasta=_HOY - datetime.timedelta(days=1),  # vencida
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=5),  # vigente
    )

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)

    todas = await repo.find_equipo(test_tenant.id, materia.id, carrera.id, cohorte.id)
    assert len(todas) == 2

    vigentes = await repo.find_equipo(
        test_tenant.id, materia.id, carrera.id, cohorte.id, solo_vigentes=True
    )
    assert len(vigentes) == 1
    assert vigentes[0].rol == "TUTOR"


async def test_find_equipo_other_tenant_returns_empty(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user, another_tenant_admin
):
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia

    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)
    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)

    materia = await materia_repo.create({"codigo": "MAT-Z", "nombre": "Materia Z"})
    carrera = await carrera_repo.create({"codigo": "CAR-Z", "nombre": "Carrera Z"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-3"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=another_tenant.id)
    rows = await repo.find_equipo(another_tenant.id, materia.id, carrera.id, cohorte.id)

    assert rows == []


# ── 2.6 RED+GREEN+TRIANGULATE: create_many ───────────────────────────────


async def test_create_many_with_single_row(
    db_session: AsyncSession, test_tenant, plain_user
):
    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    created = await repo.create_many([
        {
            "usuario_id": usuario.id,
            "rol": "PROFESOR",
            "desde": _HOY,
        }
    ])

    assert len(created) == 1
    assert created[0].tenant_id == test_tenant.id
    assert created[0].usuario_id == usuario.id
    assert created[0].id is not None


async def test_create_many_with_multiple_rows(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    created = await repo.create_many([
        {"usuario_id": usuario_a.id, "rol": "PROFESOR", "desde": _HOY},
        {"usuario_id": usuario_b.id, "rol": "TUTOR", "desde": _HOY},
    ])

    assert len(created) == 2
    assert all(row.tenant_id == test_tenant.id for row in created)
    assert {row.usuario_id for row in created} == {usuario_a.id, usuario_b.id}


# ── 2.7 RED+GREEN+TRIANGULATE: update_vigencia_equipo ────────────────────


async def test_update_vigencia_equipo_updates_alive_rows_and_returns_count(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia

    usuario_a = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "A", "A")
    usuario_b = await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "B", "B")

    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)

    materia = await materia_repo.create({"codigo": "MAT-V", "nombre": "Materia V"})
    carrera = await carrera_repo.create({"codigo": "CAR-V", "nombre": "Carrera V"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-V"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario_a.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=100),
    )
    await _make_asignacion(
        db_session, test_tenant.id, usuario_b.id, "TUTOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=100),
    )

    nueva_desde = _HOY
    nueva_hasta = _HOY + datetime.timedelta(days=180)

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    afectadas = await repo.update_vigencia_equipo(
        test_tenant.id,
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id},
        desde=nueva_desde,
        hasta=nueva_hasta,
    )

    assert afectadas == 2

    rows = await repo.find_equipo(test_tenant.id, materia.id, carrera.id, cohorte.id)
    for row in rows:
        assert row.desde == nueva_desde
        assert row.hasta == nueva_hasta


async def test_update_vigencia_equipo_other_tenant_returns_zero(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user
):
    from app.models.carrera import Carrera
    from app.models.cohorte import Cohorte
    from app.models.materia import Materia

    usuario = await make_usuario_perfil(db_session, test_tenant.id, plain_user.id)

    materia_repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    cohorte_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)

    materia = await materia_repo.create({"codigo": "MAT-W", "nombre": "Materia W"})
    carrera = await carrera_repo.create({"codigo": "CAR-W", "nombre": "Carrera W"})
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2026-W"})

    await _make_asignacion(
        db_session, test_tenant.id, usuario.id, "PROFESOR",
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        desde=_HOY - datetime.timedelta(days=10),
    )

    repo = AsignacionRepository(session=db_session, tenant_id=another_tenant.id)
    afectadas = await repo.update_vigencia_equipo(
        another_tenant.id,
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id},
        desde=_HOY,
        hasta=None,
    )

    assert afectadas == 0


# ── 2.8 RED+GREEN+TRIANGULATE: buscar_docentes (RN-30, ILIKE) ───────────


async def test_buscar_docentes_matches_partial_nombre(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "Carolina", "Gomez")
    await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "Martin", "Fernandez")

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.buscar_docentes(test_tenant.id, "carol")

    assert len(rows) == 1
    assert rows[0].nombre == "Carolina"


async def test_buscar_docentes_matches_partial_apellido(
    db_session: AsyncSession, test_tenant, plain_user, admin_user
):
    await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "Carolina", "Gomez")
    await make_usuario_perfil(db_session, test_tenant.id, admin_user.id, "Martin", "Fernandez")

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.buscar_docentes(test_tenant.id, "fernan")

    assert len(rows) == 1
    assert rows[0].apellidos == "Fernandez"


async def test_buscar_docentes_no_match_returns_empty(
    db_session: AsyncSession, test_tenant, plain_user
):
    await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "Carolina", "Gomez")

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.buscar_docentes(test_tenant.id, "zzz-no-existe")

    assert rows == []


async def test_buscar_docentes_scoped_to_tenant(
    db_session: AsyncSession, test_tenant, another_tenant, plain_user, another_tenant_admin
):
    await make_usuario_perfil(db_session, test_tenant.id, plain_user.id, "Carolina", "Gomez")
    await make_usuario_perfil(db_session, another_tenant.id, another_tenant_admin.id, "Carlitos", "Gomez")

    repo = AsignacionRepository(session=db_session, tenant_id=test_tenant.id)
    rows = await repo.buscar_docentes(test_tenant.id, "Gomez")

    assert len(rows) == 1
    assert rows[0].nombre == "Carolina"
