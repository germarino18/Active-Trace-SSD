"""Router tests for `/api/admin/usuarios` (C-07 task group 7).

ABM for the `Usuario` business profile (E4), gated by
`require_permission("usuarios:gestionar")` (D5). PII (`dni`/`cuil`/`cbu`/
`alias_cbu`) is encrypted at rest (D2) and never present in the default
list/read response (Regla Dura #12, spec `usuarios` "PII is not exposed in
default responses"). Identity is always the verified-JWT UUID — a supplied
`legajo` is never used as an identity selector (Reglas Duras #8/#14).
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from tests.helpers import cleanup_permission_cache
from tests.test_usuarios.conftest import make_token


# ── 7.1 RED: CRUD happy paths ────────────────────────────────────────────


async def test_create_and_get_usuario_with_admin_returns_201_and_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": str(plain_user.id),
            "nombre": "Ada",
            "apellidos": "Lovelace",
            "banco": "Banco Nación",
            "regional": "CABA",
            "legajo": "L-001",
            "facturador": True,
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["nombre"] == "Ada"
    assert body["apellidos"] == "Lovelace"
    assert body["user_id"] == str(plain_user.id)
    assert body["tenant_id"] == str(seeded_tenant.id)
    assert body["estado"] == "Activo"

    get_resp = await client.get(
        f"/api/admin/usuarios/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == body["id"]


async def test_list_usuarios_with_admin_returns_200(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": str(plain_user.id), "nombre": "Grace", "apellidos": "Hopper"},
    )

    list_resp = await client.get(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    assert any(u["nombre"] == "Grace" for u in list_resp.json())


async def test_update_usuario_changes_fields(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": str(plain_user.id), "nombre": "Marie", "apellidos": "Curie"},
    )
    usuario_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/admin/usuarios/{usuario_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"banco": "Banco Provincia", "estado": "Inactivo"},
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["banco"] == "Banco Provincia"
    assert body["estado"] == "Inactivo"
    assert body["nombre"] == "Marie"


async def test_delete_usuario_soft_deletes(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": str(plain_user.id), "nombre": "Rosalind", "apellidos": "Franklin"},
    )
    usuario_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/admin/usuarios/{usuario_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted_at"] is True

    get_resp = await client.get(
        f"/api/admin/usuarios/{usuario_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


# ── 7.2 RED: fail-closed without usuarios:gestionar ─────────────────────


async def test_create_usuario_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": str(plain_user.id), "nombre": "X", "apellidos": "Y"},
    )

    assert response.status_code == 403


async def test_list_usuarios_without_permission_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(alumno_user)

    response = await client.get(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


# ── 7.3 RED: PII not in default response, ciphertext at rest ────────────


async def test_usuario_response_does_not_include_pii_fields(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": str(plain_user.id),
            "nombre": "Pii",
            "apellidos": "Holder",
            "dni": "30222333",
            "cuil": "20-30222333-4",
            "cbu": "1111122223333344445555",
            "alias_cbu": "pii.holder.mp",
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    for field in ("dni", "cuil", "cbu", "alias_cbu"):
        assert field not in body

    usuario_id = body["id"]

    get_resp = await client.get(
        f"/api/admin/usuarios/{usuario_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    for field in ("dni", "cuil", "cbu", "alias_cbu"):
        assert field not in get_resp.json()

    raw = await db_session.execute(
        text("SELECT dni, cuil, cbu, alias_cbu FROM usuario WHERE id = :id"),
        {"id": usuario_id},
    )
    row = raw.one()
    assert row.dni != "30222333"
    assert row.cuil != "20-30222333-4"
    assert row.cbu != "1111122223333344445555"
    assert row.alias_cbu != "pii.holder.mp"


# ── 7.4 RED: legajo is never an identity selector ────────────────────────


async def test_legajo_in_body_does_not_change_identity(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    """A `legajo` value supplied in the create payload is stored as a
    business attribute but never resolves/overrides the `user_id` link —
    identity stays the verified-JWT UUID (Reglas Duras #8/#14)."""
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": str(plain_user.id),
            "nombre": "Legajo",
            "apellidos": "Holder",
            "legajo": "L-999",
        },
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["legajo"] == "L-999"
    assert body["user_id"] == str(plain_user.id)

    # UsuarioUpdate has no `user_id` field at all -- attempting to send one
    # is rejected by extra='forbid', proving the 1:1 link is immutable via
    # the ABM and cannot be used to "select" a different identity.
    update_resp = await client.patch(
        f"/api/admin/usuarios/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": str(admin_user.id), "legajo": "L-000"},
    )
    assert update_resp.status_code == 422


# ── 7.6 TRIANGULATE: cross-tenant rejected, soft-delete retains row ─────


async def test_get_usuario_from_other_tenant_returns_404(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_tenant,
    admin_user,
    plain_user,
    another_tenant_admin,
):
    cleanup_permission_cache()
    await db_session.commit()
    token_a = make_token(admin_user)
    token_b = make_token(another_tenant_admin)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"user_id": str(plain_user.id), "nombre": "Cross", "apellidos": "Tenant"},
    )
    assert create_resp.status_code == 201
    usuario_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/admin/usuarios/{usuario_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_resp.status_code == 404


async def test_soft_deleted_usuario_row_remains_in_database(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, plain_user
):
    cleanup_permission_cache()
    await db_session.commit()
    token = make_token(admin_user)

    create_resp = await client.post(
        "/api/admin/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": str(plain_user.id), "nombre": "Soft", "apellidos": "Delete"},
    )
    usuario_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/admin/usuarios/{usuario_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 200

    raw = await db_session.execute(
        text("SELECT id, deleted_at FROM usuario WHERE id = :id"),
        {"id": usuario_id},
    )
    row = raw.one()
    assert row.id is not None
    assert row.deleted_at is not None
