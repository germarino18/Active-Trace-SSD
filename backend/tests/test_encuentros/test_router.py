"""Integration tests for encuentros API endpoints."""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from tests.helpers import cleanup_permission_cache

_URL_PREFIX = "/api/v1/encuentros"


@pytest.mark.asyncio
async def test_crear_slot_recurrente_201(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
):
    """Creating a recurrent slot should return 201."""
    from tests.test_encuentros.conftest import make_token

    # Create dictado
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-INT", "nombre": "Integración"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "INT", "nombre": "Test Integración"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id, "nombre": "2026-I1", "anio": 2026,
        "vig_desde": date(2026, 3, 1),
    })
    dictado_repo = BaseRepository(
        model=__import__("app.models.dictado", fromlist=["Dictado"]).Dictado,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    dictado = await dictado_repo.create({
        "materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id,
    })

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "dictado_id": str(dictado.id),
        "titulo": "Clase Semanal",
        "hora": "18:00",
        "dia_semana": "Lunes",
        "fecha_inicio": "2026-03-15",
        "cant_semanas": 14,
        "vig_desde": "2026-03-01",
    }

    response = await client.post(
        f"{_URL_PREFIX}/slots",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["titulo"] == "Clase Semanal"
    assert data["cant_semanas"] == 14


@pytest.mark.asyncio
async def test_crear_slot_sin_permiso_403(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    alumno_user,
):
    """User without encuentros:gestionar should get 403."""
    from tests.test_encuentros.conftest import make_token

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(alumno_user)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "dictado_id": "00000000-0000-0000-0000-000000000001",
        "titulo": "Test",
        "hora": "18:00",
        "dia_semana": "Lunes",
        "fecha_inicio": "2026-03-15",
        "cant_semanas": 1,
        "vig_desde": "2026-03-01",
    }

    response = await client.post(
        f"{_URL_PREFIX}/slots",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_listar_instancias_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
):
    """Listing instances should return 200."""
    from tests.test_encuentros.conftest import make_token

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"{_URL_PREFIX}/instancias",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_generar_bloque_html_200(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    profesor_user,
):
    """Generate HTML block should return 200 with html."""
    from tests.test_encuentros.conftest import make_token

    # Create dictado
    materias_repo = BaseRepository(
        model=__import__("app.models.materia", fromlist=["Materia"]).Materia,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    materia = await materias_repo.create({"codigo": "MAT-HTML", "nombre": "HTML Test"})
    carreras_repo = BaseRepository(
        model=__import__("app.models.carrera", fromlist=["Carrera"]).Carrera,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    carrera = await carreras_repo.create({"codigo": "HTML", "nombre": "Test HTML"})
    cohortes_repo = BaseRepository(
        model=__import__("app.models.cohorte", fromlist=["Cohorte"]).Cohorte,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    cohorte = await cohortes_repo.create({
        "carrera_id": carrera.id, "nombre": "2026-H1", "anio": 2026,
        "vig_desde": date(2026, 3, 1),
    })
    dictado_repo = BaseRepository(
        model=__import__("app.models.dictado", fromlist=["Dictado"]).Dictado,
        session=db_session, tenant_id=seeded_tenant.id,
    )
    dictado = await dictado_repo.create({
        "materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id,
    })

    await db_session.commit()
    cleanup_permission_cache()
    token = make_token(profesor_user)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"{_URL_PREFIX}/bloque-html?dictado_id={dictado.id}",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "html" in data
    assert data["dictado_id"] == str(dictado.id)
