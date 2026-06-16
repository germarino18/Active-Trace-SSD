import os
import uuid
from io import BytesIO

import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.programas import ProgramaMateriaUpdate
from app.services.programas_service import ProgramasService


def _make_request() -> Request:
    scope = {
        "type": "http",
        "client": ("203.0.113.5", 12345),
        "headers": [(b"user-agent", b"pytest-agent")],
    }
    return Request(scope)


def _make_current_user(user_id, tenant_id) -> CurrentUser:
    return CurrentUser(user_id=user_id, tenant_id=tenant_id, roles=["ADMIN"])


@pytest.mark.asyncio
async def test_upload_programa_creates_record_and_file(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)
    file_content = b"%PDF-1.4 test content"
    upload_file = UploadFile(filename="programa2024.pdf", file=BytesIO(file_content))

    result = await service.upload_programa(
        seeded_dictado, "Programa 2024", upload_file,
        current_user=current_user, request=_make_request(),
    )

    assert result.titulo == "Programa 2024"
    assert result.dictado_id == seeded_dictado
    assert os.path.exists(result.referencia_archivo)
    with open(result.referencia_archivo, "rb") as f:
        assert f.read() == file_content

    os.remove(result.referencia_archivo)


@pytest.mark.asyncio
async def test_upload_programa_duplicate_rejected(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.upload_programa(
        seeded_dictado, "Programa", UploadFile(filename="a.pdf", file=BytesIO(b"data")),
        current_user=current_user, request=_make_request(),
    )
    assert result is not None

    with pytest.raises(ValidationException) as exc:
        await service.upload_programa(
            seeded_dictado, "Duplicado", UploadFile(filename="b.pdf", file=BytesIO(b"data")),
            current_user=current_user, request=_make_request(),
        )
    assert "Ya existe" in str(exc.value)


@pytest.mark.asyncio
async def test_update_programa_title(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.upload_programa(
        seeded_dictado, "Original", UploadFile(filename="a.pdf", file=BytesIO(b"data")),
        current_user=current_user, request=_make_request(),
    )

    updated = await service.update_programa(
        result.id, ProgramaMateriaUpdate(titulo="Actualizado"), None,
        current_user=current_user, request=_make_request(),
    )
    assert updated.titulo == "Actualizado"
    assert updated.referencia_archivo == result.referencia_archivo


@pytest.mark.asyncio
async def test_update_programa_with_file_replaces_reference(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.upload_programa(
        seeded_dictado, "Original", UploadFile(filename="a.pdf", file=BytesIO(b"old")),
        current_user=current_user, request=_make_request(),
    )

    updated = await service.update_programa(
        result.id, ProgramaMateriaUpdate(), UploadFile(filename="b.pdf", file=BytesIO(b"new")),
        current_user=current_user, request=_make_request(),
    )
    assert updated.referencia_archivo != result.referencia_archivo
    assert os.path.exists(updated.referencia_archivo)
    os.remove(updated.referencia_archivo)
    if os.path.exists(result.referencia_archivo):
        os.remove(result.referencia_archivo)


@pytest.mark.asyncio
async def test_get_programa_returns_program(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.upload_programa(
        seeded_dictado, "Test", UploadFile(filename="t.pdf", file=BytesIO(b"data")),
        current_user=current_user, request=_make_request(),
    )

    found = await service.get_programa(result.id, current_user=current_user)
    assert found.id == result.id
    assert found.titulo == "Test"


@pytest.mark.asyncio
async def test_get_programa_not_found_raises(
    db_session: AsyncSession, test_tenant, admin_user
):
    service = ProgramasService.create(db_session, test_tenant.id)
    current_user = _make_current_user(admin_user.id, test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.get_programa(uuid.uuid4(), current_user=current_user)


@pytest.mark.asyncio
async def test_soft_delete_preserves_file_reference(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    result = await service.upload_programa(
        seeded_dictado, "To Delete", UploadFile(filename="del.pdf", file=BytesIO(b"data")),
        current_user=current_user, request=_make_request(),
    )

    await service.delete_programa(result.id, current_user=current_user, request=_make_request())

    assert os.path.exists(result.referencia_archivo)
    os.remove(result.referencia_archivo)

    repo = ProgramaMateriaRepository(session=db_session, tenant_id=test_tenant.id)
    with pytest.raises(NotFoundException):
        await service.get_programa(result.id, current_user=current_user)


@pytest.mark.asyncio
async def test_get_by_dictado_returns_program(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)

    await service.upload_programa(
        seeded_dictado, "By Dictado", UploadFile(filename="bd.pdf", file=BytesIO(b"data")),
        current_user=current_user, request=_make_request(),
    )

    found = await service.get_by_dictado(seeded_dictado, current_user=current_user)
    assert found.titulo == "By Dictado"


@pytest.mark.asyncio
async def test_download_returns_file(
    db_session: AsyncSession, test_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user = _make_current_user(admin_user.id, test_tenant.id)
    file_content = b"download test content"

    result = await service.upload_programa(
        seeded_dictado, "Download Test", UploadFile(filename="dl.pdf", file=BytesIO(file_content)),
        current_user=current_user, request=_make_request(),
    )

    response = await service.download_programa(result.id, current_user=current_user)
    assert response.path == result.referencia_archivo
    os.remove(result.referencia_archivo)


@pytest.mark.asyncio
async def test_tenant_isolation_rejects_other_tenant(
    db_session: AsyncSession, test_tenant, another_tenant, seeded_dictado, admin_user
):
    upload_dir = os.path.join("C:\\Users\\navar\\AppData\\Local\\Temp\\opencode", "test_uploads")
    service1 = ProgramasService.create(db_session, test_tenant.id, upload_dir=upload_dir)
    current_user1 = _make_current_user(admin_user.id, test_tenant.id)

    result = await service1.upload_programa(
        seeded_dictado, "Tenant 1", UploadFile(filename="t1.pdf", file=BytesIO(b"data")),
        current_user=current_user1, request=_make_request(),
    )

    service2 = ProgramasService.create(db_session, another_tenant.id, upload_dir=upload_dir)
    current_user2 = _make_current_user(admin_user.id, another_tenant.id)
    with pytest.raises(NotFoundException):
        await service2.get_programa(result.id, current_user=current_user2)
