from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from tests.helpers import cleanup_permission_cache, seed_asignaciones_for_user
from tests.test_usuarios.conftest import make_token


async def _create_usuario(db_session, tenant_id, user) -> Usuario:
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await repo.create(
        {
            "user_id": user.id,
            "nombre": "Test",
            "apellidos": "User",
            "facturador": False,
            "estado": "Activo",
        }
    )
    return usuario


async def _create_rol(db_session, tenant_id, codigo="TEST-ROL"):
    from app.models.rol import Rol
    repo = BaseRepository(model=Rol, session=db_session, tenant_id=tenant_id)
    rol = await repo.create(
        {
            "codigo": codigo,
            "nombre": f"Rol {codigo}",
            "descripcion": "Test role",
        }
    )
    return rol


# ── POST / roles ──────────────────────────────────────────────────────────


async def test_assign_rol_to_usuario(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)
    rol = await _create_rol(db_session, seeded_tenant.id, "ADMIN-ROL-TEST-1")

    resp = await client.post(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": str(rol.id)},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["usuario_id"] == str(usuario.id)
    assert body["rol_id"] == str(rol.id)
    assert body["rol_nombre"] == rol.nombre


async def test_assign_rol_with_vigencia(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)
    rol = await _create_rol(db_session, seeded_tenant.id, "ADMIN-ROL-TEST-2")

    today = date.today()
    desde = today - timedelta(days=30)
    hasta = today + timedelta(days=365)

    resp = await client.post(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "rol_id": str(rol.id),
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat(),
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["desde"] == desde.isoformat()
    assert body["hasta"] == hasta.isoformat()


async def test_assign_rol_usuario_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    rol = await _create_rol(db_session, seeded_tenant.id, "ADMIN-ROL-TEST-3")

    resp = await client.post(
        f"/api/admin/usuarios/00000000-0000-0000-0000-000000000000/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": str(rol.id)},
    )
    assert resp.status_code == 404


async def test_assign_rol_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)

    resp = await client.post(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 404


async def test_assign_rol_sin_permiso_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    resp = await client.post(
        "/api/admin/usuarios/00000000-0000-0000-0000-000000000000/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 403


# ── GET / usuarios/{id}/roles ─────────────────────────────────────────────


async def test_list_usuario_roles(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)
    rol1 = await _create_rol(db_session, seeded_tenant.id, "ADMIN-ROL-LIST-1")
    rol2 = await _create_rol(db_session, seeded_tenant.id, "ADMIN-ROL-LIST-2")

    await client.post(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": str(rol1.id)},
    )
    await client.post(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": str(rol2.id)},
    )

    resp = await client.get(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    rol_ids = {r["rol_id"] for r in body}
    assert str(rol1.id) in rol_ids
    assert str(rol2.id) in rol_ids


async def test_list_usuario_roles_empty(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)

    resp = await client.get(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []


# ── DELETE / usuarios/{id}/roles/{rol_id} ─────────────────────────────────


async def test_remove_rol_from_usuario(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)
    rol = await _create_rol(db_session, seeded_tenant.id, "ADMIN-ROL-DEL-1")

    assign_resp = await client.post(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"rol_id": str(rol.id)},
    )
    assert assign_resp.status_code == 201

    delete_resp = await client.delete(
        f"/api/admin/usuarios/{usuario.id}/roles/{rol.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["detail"] == "Rol removed from user"

    list_resp = await client.get(
        f"/api/admin/usuarios/{usuario.id}/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.json() == []


async def test_remove_rol_inexistente_returns_404(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)
    usuario = await _create_usuario(db_session, seeded_tenant.id, admin_user)

    resp = await client.delete(
        f"/api/admin/usuarios/{usuario.id}/roles/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
