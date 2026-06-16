"""Integration tests for guardias API endpoints."""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from tests.helpers import cleanup_permission_cache

_URL_PREFIX = "/api/v1/guardias"


@pytest.mark.asyncio
async def test_registrar_guardia_201(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    tutor_user,
):
    """Registering a guardia should return 201."""
    from tests.test_guardias.conftest import make_token

    # Create dictado
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-GR-INT", "nombre": "Guardia Integración"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "GRI", "nombre": "Test GRI"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id, "nombre": "2026-GRI", "anio": 2026,
        "vig_desde": date(2026, 3, 1),
    })
    dictado_repo = BaseRepository(
        model=__import__("app.models.dictado", fromlist=["Dictado"]).Dictado,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    dictado = await dictado_repo.create({
        "materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id,
    })

    # Create Usuario + Asignacion for the tutor user
    from app.models.usuario import Usuario
    from app.models.asignacion import Asignacion

    usuario_repo = BaseRepository(
        model=Usuario, session=db_session, tenant_id=seeded_tenant.id,
    )
    usuario = await usuario_repo.create({
        "user_id": tutor_user.id, "nombre": "Tutor", "apellidos": "Guardia",
    })

    asig_repo = BaseRepository(
        model=Asignacion, session=db_session, tenant_id=seeded_tenant.id,
    )
    asignacion = await asig_repo.create({
        "usuario_id": usuario.id, "rol": "TUTOR",
        "dictado_id": dictado.id, "desde": date(2026, 3, 1),
    })

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(tutor_user)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "asignacion_id": str(asignacion.id),
        "dictado_id": str(dictado.id),
        "dia": "Martes",
        "horario": "14:00–14:45",
    }

    response = await client.post(
        _URL_PREFIX,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["dia"] == "Martes"
    assert data["estado"] == "Pendiente"


@pytest.mark.asyncio
async def test_listar_guardias_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
):
    """Listing guardias should return 200."""
    from tests.test_guardias.conftest import make_token

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(admin_user)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(_URL_PREFIX, headers=headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_guardia_sin_permiso_403(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    alumno_user,
):
    """User without encuentros:gestionar should get 403."""
    from tests.test_guardias.conftest import make_token

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(alumno_user)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(_URL_PREFIX, headers=headers)
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_exportar_guardias_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
):
    """Exporting guardias should return CSV."""
    from tests.test_guardias.conftest import make_token

    # Create dictado so there's data to export
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-EXP", "nombre": "Export Test"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "EXP", "nombre": "Test Exp"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id, "nombre": "2026-EXP", "anio": 2026,
        "vig_desde": date(2026, 3, 1),
    })
    dictado_repo = BaseRepository(
        model=__import__("app.models.dictado", fromlist=["Dictado"]).Dictado,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    await dictado_repo.create({
        "materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id,
    })

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(admin_user)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"{_URL_PREFIX}/export",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert "text/csv" in response.headers.get("content-type", "")
