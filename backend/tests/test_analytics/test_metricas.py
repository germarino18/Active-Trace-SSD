from datetime import date

from httpx import AsyncClient
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.services.auth.password_service import PasswordService
from tests.helpers import cleanup_permission_cache, seed_permissions_for_tenant


def make_token_admin(user, secret="a" * 32):
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4
    from jose import jwt
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": user.roles,
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


async def _create_user(db_session, tenant_id, email, roles):
    pw = PasswordService()
    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=pw.hash_password("Password123!"),
        display_name=email,
        roles=roles,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def _create_usuario(db_session, tenant_id, user_id):
    repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    return await repo.create(
        {
            "user_id": user_id,
            "nombre": "Test",
            "apellidos": "User",
            "facturador": False,
            "estado": "Activo",
        }
    )


# ── Metricas endpoint ─────────────────────────────────────────────────────


async def test_get_metricas_returns_zero_when_empty(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()

    token = make_token_admin(admin_user)
    resp = await client.get(
        "/api/admin/metricas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_alumnos"] == 0
    assert body["alumnos_activos"] == 0
    assert body["total_docentes"] == 0
    assert body["total_materias_activas"] == 0
    assert body["total_carreras_activas"] == 0


async def test_get_metricas_with_data(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user
):
    cleanup_permission_cache()
    await db_session.commit()

    tenant_id = seeded_tenant.id
    token = make_token_admin(admin_user)

    # Create users
    admin_user_2 = await _create_user(db_session, tenant_id, "metrics_admin@test.test", ["ADMIN"])
    user_alumno = await _create_user(db_session, tenant_id, "alumno_metricas@test.test", ["ALUMNO"])

    # Create Usuario profiles
    usuario_admin = await _create_usuario(db_session, tenant_id, admin_user_2.id)
    usuario_alumno = await _create_usuario(db_session, tenant_id, user_alumno.id)

    # Assign roles via Asignacion
    hoy = date(2025, 1, 1)
    for usuario_id, rol in [(usuario_alumno.id, "ALUMNO"), (usuario_admin.id, "ADMIN")]:
        await db_session.execute(
            sql_text("""
                INSERT INTO asignacion (id, tenant_id, usuario_id, rol, desde, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :usuario_id, :rol, :desde, now(), now())
            """),
            {"tenant_id": tenant_id, "usuario_id": usuario_id, "rol": rol, "desde": hoy},
        )

    # Create active carreras and materias
    for codigo in ("MET-1", "MET-2", "MET-3"):
        await db_session.execute(
            sql_text("""
                INSERT INTO carrera (id, tenant_id, codigo, nombre, estado, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, 'Activa', now(), now())
            """),
            {"tenant_id": tenant_id, "codigo": codigo, "nombre": f"Carrera {codigo}"},
        )

    for codigo in ("MAT-MET-1", "MAT-MET-2"):
        await db_session.execute(
            sql_text("""
                INSERT INTO materia (id, tenant_id, codigo, nombre, estado, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, 'Activa', now(), now())
            """),
            {"tenant_id": tenant_id, "codigo": codigo, "nombre": f"Materia {codigo}"},
        )

    await db_session.commit()

    resp = await client.get(
        "/api/admin/metricas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_alumnos"] >= 1
    assert body["alumnos_activos"] >= 1
    assert body["total_materias_activas"] == 2
    assert body["total_carreras_activas"] == 3
    assert body["total_docentes"] >= 0


async def test_get_metricas_sin_permiso_returns_403(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, alumno_user
):
    cleanup_permission_cache()
    await db_session.commit()

    token = make_token_admin(alumno_user)
    resp = await client.get(
        "/api/admin/metricas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


async def test_get_metricas_tenant_isolation(
    client: AsyncClient, db_session: AsyncSession, seeded_tenant, admin_user, another_tenant, another_tenant_admin
):
    cleanup_permission_cache()
    await db_session.commit()

    token_a = make_token_admin(admin_user)
    token_b = make_token_admin(another_tenant_admin)
    tenant_a_id = seeded_tenant.id

    # Create data in tenant_a only
    await db_session.execute(
        sql_text("""
            INSERT INTO carrera (id, tenant_id, codigo, nombre, estado, created_at, updated_at)
            VALUES (gen_random_uuid(), :tenant_id, 'MET-ISO', 'Carrera Isolation', 'Activa', now(), now())
        """),
        {"tenant_id": tenant_a_id},
    )
    await db_session.commit()

    resp_a = await client.get(
        "/api/admin/metricas",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    resp_b = await client.get(
        "/api/admin/metricas",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_a.status_code == 200
    assert resp_b.status_code == 200
    assert resp_a.json()["total_carreras_activas"] > resp_b.json()["total_carreras_activas"]
