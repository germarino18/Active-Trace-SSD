"""Test that migration 007 (usuario, asignacion, equipos:asignar seed,
backfill of users.roles -> asignacion) applies and reverts cleanly.

Follows the pattern of tests/test_audit_log/test_migration_004.py: runs the
migration's `upgrade()`/`downgrade()` directly against a dedicated
connection bound via `MigrationContext`/`Operations`, independent of the
ORM-driven `Base.metadata.create_all` used by the session-scoped `db_engine`
fixture.
"""

import importlib.util
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from app.core.database import Base

_MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "alembic"
    / "versions"
    / "007_create_usuario_asignacion.py"
)
_spec = importlib.util.spec_from_file_location("migration_007", _MIGRATION_PATH)
migration_007 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration_007)


async def _run_migration_fn(engine, fn_name: str):
    async with engine.begin() as conn:
        def _run(sync_conn):
            ctx = MigrationContext.configure(sync_conn)
            with Operations.context(ctx):
                getattr(migration_007, fn_name)()
        await conn.run_sync(_run)


async def _seed_rol_catalog(conn, tenant_id: str) -> None:
    """Seed the minimal `rol` catalog (migration 003) that migration 007's
    `equipos:asignar` rol_permiso seed expects to already exist for COORDINADOR
    and ADMIN."""
    for codigo, nombre in (("COORDINADOR", "Coordinador"), ("ADMIN", "Admin")):
        await conn.execute(
            text("""
                INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, NULL, now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
            """),
            {"tenant_id": tenant_id, "codigo": codigo, "nombre": nombre},
        )


async def test_migration_007_up_and_down(test_db_url: str):
    engine = create_async_engine(test_db_url)
    try:
        # 1. Drop the plain ORM-created tables (usuario/asignacion are part
        # of Base.metadata via app.models.__init__), seed a tenant and a
        # user with roles so the backfill loop has data to act on.
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS asignacion CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS usuario CASCADE"))
            await conn.execute(
                text(
                    "INSERT INTO tenant (id, name, slug, created_at, updated_at) "
                    "VALUES ('11111111-1111-1111-1111-111111111111', 'Migration 007 Tenant', "
                    "'migration-007-test-tenant', now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )
            await _seed_rol_catalog(conn, "11111111-1111-1111-1111-111111111111")
            await conn.execute(
                text(
                    "INSERT INTO users (id, tenant_id, email, password_hash, display_name, "
                    "roles, is_active, created_at, updated_at) "
                    "VALUES ('22222222-2222-2222-2222-222222222222', "
                    "'11111111-1111-1111-1111-111111111111', "
                    "'migration007@example.com', 'hash', 'Migration User', "
                    "ARRAY['PROFESOR','TUTOR'], true, now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )

        # 2. Apply migration 007.
        await _run_migration_fn(engine, "upgrade")

        # 3. Assert tables, indexes, seed, and backfill exist.
        async with engine.connect() as conn:
            usuario_exists = await conn.scalar(
                text("SELECT to_regclass('public.usuario') IS NOT NULL")
            )
            assert usuario_exists is True

            asignacion_exists = await conn.scalar(
                text("SELECT to_regclass('public.asignacion') IS NOT NULL")
            )
            assert asignacion_exists is True

            # equipos:asignar seeded for the tenant
            permiso_seeded = await conn.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM permiso WHERE codigo = 'equipos:asignar' "
                    "AND tenant_id = '11111111-1111-1111-1111-111111111111')"
                )
            )
            assert permiso_seeded is True

            # equipos:asignar granted to COORDINADOR and ADMIN
            granted_roles = await conn.execute(
                text(
                    "SELECT r.codigo FROM rol_permiso rp "
                    "JOIN rol r ON r.id = rp.rol_id "
                    "JOIN permiso p ON p.id = rp.permiso_id "
                    "WHERE p.codigo = 'equipos:asignar' "
                    "AND rp.tenant_id = '11111111-1111-1111-1111-111111111111'"
                )
            )
            granted = {row[0] for row in granted_roles}
            assert granted == {"COORDINADOR", "ADMIN"}

            # backfill: a usuario shell exists for the migrated user
            usuario_row = await conn.execute(
                text(
                    "SELECT id FROM usuario WHERE user_id = "
                    "'22222222-2222-2222-2222-222222222222'"
                )
            )
            usuario_id = usuario_row.scalar()
            assert usuario_id is not None

            # backfill: an asignacion exists per users.roles entry, NULL
            # context, hasta IS NULL
            asignacion_roles = await conn.execute(
                text(
                    "SELECT rol, hasta, dictado_id, materia_id, carrera_id, cohorte_id "
                    "FROM asignacion WHERE usuario_id = :usuario_id"
                ),
                {"usuario_id": usuario_id},
            )
            rows = asignacion_roles.fetchall()
            roles_found = {row[0] for row in rows}
            assert roles_found == {"PROFESOR", "TUTOR"}
            for row in rows:
                assert row[1] is None  # hasta
                assert row[2] is None and row[3] is None  # dictado/materia
                assert row[4] is None and row[5] is None  # carrera/cohorte

            # users.roles is left intact
            users_roles = await conn.scalar(
                text(
                    "SELECT roles FROM users WHERE id = "
                    "'22222222-2222-2222-2222-222222222222'"
                )
            )
            assert set(users_roles) == {"PROFESOR", "TUTOR"}

        # 4. Revert migration 007.
        await _run_migration_fn(engine, "downgrade")

        # 5. Assert tables and seed are fully removed.
        async with engine.connect() as conn:
            usuario_exists = await conn.scalar(
                text("SELECT to_regclass('public.usuario') IS NOT NULL")
            )
            assert usuario_exists is False

            asignacion_exists = await conn.scalar(
                text("SELECT to_regclass('public.asignacion') IS NOT NULL")
            )
            assert asignacion_exists is False

            permiso_seeded = await conn.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM permiso WHERE codigo = 'equipos:asignar' "
                    "AND tenant_id = '11111111-1111-1111-1111-111111111111')"
                )
            )
            assert permiso_seeded is False

            # users.roles remains intact even after downgrade
            users_roles = await conn.scalar(
                text(
                    "SELECT roles FROM users WHERE id = "
                    "'22222222-2222-2222-2222-222222222222'"
                )
            )
            assert set(users_roles) == {"PROFESOR", "TUTOR"}

        # 6. Recreate the plain ORM tables for the rest of the test session.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.tables["usuario"].create)
            await conn.run_sync(Base.metadata.tables["asignacion"].create)
    finally:
        await engine.dispose()


async def test_migration_007_seed_and_backfill_are_idempotent(test_db_url: str):
    """Re-running the seed/backfill helpers (e.g. a retried partial migration
    or a tenant processed twice) must not duplicate seed rows or
    asignaciones (D4/D5 — ON CONFLICT DO NOTHING + unique indexes).

    `upgrade()` itself is only ever applied once by Alembic (re-running
    `create_table` would always fail with "relation already exists" — that
    is expected and out of scope here). What MUST be idempotent is the
    seed/backfill logic, which could plausibly run again for a tenant.
    """
    engine = create_async_engine(test_db_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS asignacion CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS usuario CASCADE"))
            await conn.execute(
                text(
                    "INSERT INTO tenant (id, name, slug, created_at, updated_at) "
                    "VALUES ('33333333-3333-3333-3333-333333333333', 'Migration 007 Idempotent', "
                    "'migration-007-idempotent-tenant', now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )
            await _seed_rol_catalog(conn, "33333333-3333-3333-3333-333333333333")
            await conn.execute(
                text(
                    "INSERT INTO users (id, tenant_id, email, password_hash, display_name, "
                    "roles, is_active, created_at, updated_at) "
                    "VALUES ('44444444-4444-4444-4444-444444444444', "
                    "'33333333-3333-3333-3333-333333333333', "
                    "'idempotent007@example.com', 'hash', 'Idempotent User', "
                    "ARRAY['ADMIN'], true, now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )

        await _run_migration_fn(engine, "upgrade")

        # Re-run the seed/backfill helpers a second time against the same
        # tenant — must not duplicate anything.
        async with engine.begin() as conn:
            def _rerun(sync_conn):
                ctx = MigrationContext.configure(sync_conn)
                with Operations.context(ctx):
                    migration_007._seed_equipos_asignar_for_tenant(
                        sync_conn, "33333333-3333-3333-3333-333333333333"
                    )
                    migration_007._backfill_for_tenant(
                        sync_conn, "33333333-3333-3333-3333-333333333333"
                    )
            await conn.run_sync(_rerun)

        async with engine.connect() as conn:
            usuario_count = await conn.scalar(
                text(
                    "SELECT COUNT(*) FROM usuario WHERE user_id = "
                    "'44444444-4444-4444-4444-444444444444'"
                )
            )
            assert usuario_count == 1

            asignacion_count = await conn.scalar(
                text(
                    "SELECT COUNT(*) FROM asignacion a "
                    "JOIN usuario u ON u.id = a.usuario_id "
                    "WHERE u.user_id = '44444444-4444-4444-4444-444444444444' "
                    "AND a.rol = 'ADMIN'"
                )
            )
            assert asignacion_count == 1

            permiso_count = await conn.scalar(
                text(
                    "SELECT COUNT(*) FROM permiso WHERE codigo = 'equipos:asignar' "
                    "AND tenant_id = '33333333-3333-3333-3333-333333333333'"
                )
            )
            assert permiso_count == 1

        await _run_migration_fn(engine, "downgrade")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.tables["usuario"].create)
            await conn.run_sync(Base.metadata.tables["asignacion"].create)
    finally:
        await engine.dispose()
