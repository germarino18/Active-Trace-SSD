"""Test that migration 004 (audit_log + append-only trigger + seed) applies
and reverts cleanly against the test database.

This test runs the migration's `upgrade()`/`downgrade()` functions directly
against a dedicated connection (alembic `op` proxy bound via
`MigrationContext`), independent of the ORM-driven `Base.metadata.create_all`
used by the session-scoped `db_engine` fixture.

Because `audit_log` is part of `Base.metadata` (registered in
`app.models.__init__`), `db_engine` already created a plain `audit_log` table
(no trigger, no seed) for the rest of the test session. This test:
1. Drops that plain table (using its own dedicated engine/connection, to
   avoid lock contention with other session-scoped fixtures' open
   transactions).
2. Runs migration 004 `upgrade()` (creates table + trigger + seed).
3. Asserts table, trigger, and seed row exist.
4. Runs migration 004 `downgrade()` (drops trigger/function/seed/table).
5. Asserts everything is gone.
6. Recreates the plain ORM table so later tests in this session still work.
"""

import importlib.util
from pathlib import Path

from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.database import Base

_MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "alembic"
    / "versions"
    / "004_create_audit_log_table.py"
)
_spec = importlib.util.spec_from_file_location("migration_004", _MIGRATION_PATH)
migration_004 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration_004)


async def _run_migration_fn(engine, fn_name: str):
    async with engine.begin() as conn:
        def _run(sync_conn):
            ctx = MigrationContext.configure(sync_conn)
            with Operations.context(ctx):
                getattr(migration_004, fn_name)()
        await conn.run_sync(_run)


async def test_migration_004_up_and_down(test_db_url: str):
    engine = create_async_engine(test_db_url)
    try:
        # 1. Drop the plain ORM-created table (no trigger), and ensure at
        # least one tenant exists so the per-tenant seed loop has a row to
        # act on.
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS audit_log"))
            await conn.execute(
                text(
                    "INSERT INTO tenant (id, name, slug, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), 'Migration Test Tenant', "
                    "'migration-004-test-tenant', now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )

        # 2. Apply migration 004.
        await _run_migration_fn(engine, "upgrade")

        # 3. Assert table, trigger, and seed exist.
        async with engine.connect() as conn:
            table_exists = await conn.scalar(
                text("SELECT to_regclass('public.audit_log') IS NOT NULL")
            )
            assert table_exists is True

            trigger_exists = await conn.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM pg_trigger "
                    "WHERE tgname = 'trg_audit_log_block_update_delete')"
                )
            )
            assert trigger_exists is True

            seeded = await conn.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM permiso WHERE codigo = 'impersonacion:usar')"
                )
            )
            assert seeded is True

        # 4. Revert migration 004.
        await _run_migration_fn(engine, "downgrade")

        # 5. Assert table, trigger, and seed are gone.
        async with engine.connect() as conn:
            table_exists = await conn.scalar(
                text("SELECT to_regclass('public.audit_log') IS NOT NULL")
            )
            assert table_exists is False

            trigger_exists = await conn.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM pg_trigger "
                    "WHERE tgname = 'trg_audit_log_block_update_delete')"
                )
            )
            assert trigger_exists is False

            seeded = await conn.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM permiso WHERE codigo = 'impersonacion:usar')"
                )
            )
            assert seeded is False

        # 6. Recreate the plain ORM table for the rest of the test session.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.tables["audit_log"].create)
    finally:
        await engine.dispose()
