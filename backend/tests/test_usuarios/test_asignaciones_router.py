"""Router tests for `/api/asignaciones` (C-07 task group 8).

CRUD for `Asignacion` (E5), gated by `require_permission("equipos:asignar")`
(D5). `estado_vigencia` (Vigente|Vencida) is derived by dates and exposed in
responses, never stored (D3). A Vencida asignacion is retained but does NOT
contribute to effective roles (KB E5, cross-checked against
`AsignacionRepository.find_roles_vigentes` from group 5).
"""

import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.usuario import Usuario
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.base import BaseRepository
from tests.helpers import cleanup_permission_cache
from tests.test_usuarios.conftest import make_token

_HOY = datetime.date.today()


async def _make_usuario_perfil(db_session: AsyncSession, tenant_id, user_id) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await repo.create({"user_id": user_id, "nombre": "Perfil", "apellidos": "Test"})


# ── 8.1 RED: CRUD happy paths ────────────────────────────────────────────


async def test_create_and_get_asignacion_with_admin_returns_201_and_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "PROFESOR",
            "desde": str(_HOY - datetime.timedelta(days=10)),
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["usuario_id"] == str(usuario.id)
    assert body["rol"] == "PROFESOR"
    assert body["tenant_id"] == str(seeded_tenant.id)

    get_resp = await client.get(
        f"/api/asignaciones/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == body["id"]


async def test_list_asignaciones_with_admin_returns_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={"usuario_id": str(usuario.id), "rol": "TUTOR", "desde": str(_HOY)},
    )

    list_resp = await client.get(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    assert any(a["rol"] == "TUTOR" for a in list_resp.json())


async def test_update_asignacion_changes_fields(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={"usuario_id": str(usuario.id), "rol": "TUTOR", "desde": str(_HOY)},
    )
    asignacion_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/asignaciones/{asignacion_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"comisiones": ["A", "B"]},
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["comisiones"] == ["A", "B"]
    assert body["rol"] == "TUTOR"


async def test_delete_asignacion_soft_deletes(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={"usuario_id": str(usuario.id), "rol": "TUTOR", "desde": str(_HOY)},
    )
    asignacion_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/asignaciones/{asignacion_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_at"] is True

    get_resp = await client.get(
        f"/api/asignaciones/{asignacion_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


# ── 8.2 RED: fail-closed without equipos:asignar ─────────────────────────


async def test_create_asignacion_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={"usuario_id": str(usuario.id), "rol": "TUTOR", "desde": str(_HOY)},
    )
    assert response.status_code == 403


async def test_list_asignaciones_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.get(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ── 8.3 RED: derived estado_vigencia, never stored ───────────────────────


async def test_asignacion_response_includes_derived_estado_vigencia_vigente(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "PROFESOR",
            "desde": str(_HOY - datetime.timedelta(days=5)),
            "hasta": None,
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["estado_vigencia"] == "Vigente"


async def test_asignacion_response_includes_derived_estado_vigencia_vencida(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "PROFESOR",
            "desde": str(_HOY - datetime.timedelta(days=30)),
            "hasta": str(_HOY - datetime.timedelta(days=1)),
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["estado_vigencia"] == "Vencida"


async def test_estado_vigencia_is_not_a_stored_column(db_session: AsyncSession):
    assert not hasattr(__import__("app.models.asignacion", fromlist=["Asignacion"]).Asignacion, "estado_vigencia")


# ── 8.4 RED: Vencida is retained but excluded from effective roles ───────


async def test_vencida_asignacion_retained_but_not_in_effective_roles(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "PROFESOR",
            "desde": str(_HOY - datetime.timedelta(days=60)),
            "hasta": str(_HOY - datetime.timedelta(days=30)),
        },
    )
    assert create_resp.status_code == 201
    asignacion_id = create_resp.json()["id"]

    # Row remains retrievable (retained).
    get_resp = await client.get(
        f"/api/asignaciones/{asignacion_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["estado_vigencia"] == "Vencida"

    # Does not contribute to effective roles.
    asignacion_repo = AsignacionRepository(session=db_session, tenant_id=seeded_tenant.id)
    roles = await asignacion_repo.find_roles_vigentes(seeded_tenant.id, usuario.id)
    assert "PROFESOR" not in roles


# ── 8.5 RED: responsable_id + comisiones round-trip, NEXO accepted ──────


async def test_responsable_id_and_comisiones_round_trip(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user, another_tenant_admin
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    responsable = await _make_usuario_perfil(db_session, seeded_tenant.id, admin_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "PROFESOR",
            "desde": str(_HOY),
            "comisiones": ["A", "B", "C"],
            "responsable_id": str(responsable.id),
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["comisiones"] == ["A", "B", "C"]
    assert body["responsable_id"] == str(responsable.id)

    get_resp = await client.get(
        f"/api/asignaciones/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.json()["comisiones"] == ["A", "B", "C"]
    assert get_resp.json()["responsable_id"] == str(responsable.id)


async def test_rol_nexo_is_accepted(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={"usuario_id": str(usuario.id), "rol": "NEXO", "desde": str(_HOY)},
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["rol"] == "NEXO"


# ── 8.7 TRIANGULATE: cross-tenant rejected; context FK tenant-validated ─


async def test_get_asignacion_from_other_tenant_returns_404(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    plain_user,
    another_tenant_admin,
):
    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    await db_session.commit()
    token_a = make_token(admin_user)
    token_b = make_token(another_tenant_admin)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"usuario_id": str(usuario.id), "rol": "TUTOR", "desde": str(_HOY)},
    )
    assert create_resp.status_code == 201
    asignacion_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/asignaciones/{asignacion_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_resp.status_code == 404


async def test_create_asignacion_with_carrera_from_other_tenant_returns_404(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    plain_user,
    another_tenant_admin,
):
    """`carrera_id` context FK MUST belong to the caller's tenant — a
    carrera from another tenant is rejected like any unknown id (D5/regla
    dura #9)."""
    from app.models.carrera import Carrera

    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)

    other_carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=another_tenant_admin.tenant_id)
    other_carrera = await other_carrera_repo.create({"codigo": "OTHER", "nombre": "Otra carrera"})
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "COORDINADOR",
            "desde": str(_HOY),
            "carrera_id": str(other_carrera.id),
        },
    )
    assert create_resp.status_code == 404


async def test_create_asignacion_with_carrera_from_same_tenant_succeeds(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    from app.models.carrera import Carrera

    cleanup_permission_cache()
    usuario = await _make_usuario_perfil(db_session, seeded_tenant.id, plain_user.id)
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=seeded_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/asignaciones",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "usuario_id": str(usuario.id),
            "rol": "COORDINADOR",
            "desde": str(_HOY),
            "carrera_id": str(carrera.id),
        },
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["carrera_id"] == str(carrera.id)
