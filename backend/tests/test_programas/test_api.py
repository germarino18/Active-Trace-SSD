from io import BytesIO
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from tests.helpers import cleanup_permission_cache
from tests.test_programas.conftest import make_token


@pytest.mark.asyncio
async def test_upload_programa_returns_201(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    resp = await client.post(
        "/api/v1/programas",
        headers={"Authorization": f"Bearer {token}"},
        data={"dictado_id": str(seeded_dictado), "titulo": "Programa 2024"},
        files={"archivo": ("programa.pdf", b"%PDF-1.4 content", "application/pdf")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["titulo"] == "Programa 2024"
    assert body["dictado_id"] == str(seeded_dictado)
    assert "referencia_archivo" in body
    assert "id" in body


@pytest.mark.asyncio
async def test_upload_programa_duplicate_returns_422(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    data = {"dictado_id": str(seeded_dictado), "titulo": "Programa"}
    files = {"archivo": ("p.pdf", b"data", "application/pdf")}
    first = await client.post(
        "/api/v1/programas", headers={"Authorization": f"Bearer {token}"}, data=data, files=files
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/programas", headers={"Authorization": f"Bearer {token}"}, data=data, files=files
    )
    assert second.status_code == 422


@pytest.mark.asyncio
async def test_get_programa_returns_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create = await client.post(
        "/api/v1/programas",
        headers={"Authorization": f"Bearer {token}"},
        data={"dictado_id": str(seeded_dictado), "titulo": "Programa"},
        files={"archivo": ("p.pdf", b"data", "application/pdf")},
    )
    assert create.status_code == 201
    program_id = create.json()["id"]

    get = await client.get(
        f"/api/v1/programas/{program_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 200
    assert get.json()["id"] == program_id


@pytest.mark.asyncio
async def test_get_programa_by_dictado_returns_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/v1/programas",
        headers={"Authorization": f"Bearer {token}"},
        data={"dictado_id": str(seeded_dictado), "titulo": "Programa"},
        files={"archivo": ("p.pdf", b"data", "application/pdf")},
    )

    get = await client.get(
        f"/api/v1/programas/por-dictado/{seeded_dictado}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 200
    assert get.json()["dictado_id"] == str(seeded_dictado)


@pytest.mark.asyncio
async def test_delete_programa_returns_204(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create = await client.post(
        "/api/v1/programas",
        headers={"Authorization": f"Bearer {token}"},
        data={"dictado_id": str(seeded_dictado), "titulo": "To Delete"},
        files={"archivo": ("d.pdf", b"data", "application/pdf")},
    )
    assert create.status_code == 201
    program_id = create.json()["id"]

    delete = await client.delete(
        f"/api/v1/programas/{program_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete.status_code == 204

    get = await client.get(
        f"/api/v1/programas/{program_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_download_programa_returns_file(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create = await client.post(
        "/api/v1/programas",
        headers={"Authorization": f"Bearer {token}"},
        data={"dictado_id": str(seeded_dictado), "titulo": "Download"},
        files={"archivo": ("dl.pdf", b"file content", "application/pdf")},
    )
    assert create.status_code == 201
    program_id = create.json()["id"]

    download = await client.get(
        f"/api/v1/programas/{program_id}/descargar",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert download.status_code == 200
    assert download.content == b"file content"


@pytest.mark.asyncio
async def test_programas_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    resp = await client.post(
        "/api/v1/programas",
        headers={"Authorization": f"Bearer {token}"},
        data={"dictado_id": str(seeded_dictado), "titulo": "No Perm"},
        files={"archivo": ("n.pdf", b"data", "application/pdf")},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_programas_other_tenant_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, another_tenant_admin, seeded_dictado
):
    cleanup_permission_cache()
    await db_session.commit()

    admin_token = make_token(another_tenant_admin)

    get = await client.get(
        f"/api/v1/programas/{uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get.status_code == 404
