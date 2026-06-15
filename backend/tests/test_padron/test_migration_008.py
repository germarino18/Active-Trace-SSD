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
    / "008_create_version_padron_entrada_padron.py"
)
_spec = importlib.util.spec_from_file_location("migration_008", _MIGRATION_PATH)
migration_008 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration_008)


async def _run_migration_fn(engine, fn_name: str):
    async with engine.begin() as conn:
        def _run(sync_conn):
            ctx = MigrationContext.configure(sync_conn)
            with Operations.context(ctx):
                getattr(migration_008, fn_name)()
        await conn.run_sync(_run)


async def _seed_rol_catalog(conn, tenant_id: str) -> None:
    """Seed minimal roles needed for seed permission grants."""
    for codigo, nombre in (
        ("COORDINADOR", "Coordinador"),
        ("ADMIN", "Admin"),
    ):
        await conn.execute(
            text("""
                INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, NULL, now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
            """),
            {"tenant_id": tenant_id, "codigo": codigo, "nombre": nombre},
        )


async def test_migration_008_up_and_down(test_db_url: str):
    engine = create_async_engine(test_db_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS entrada_padron CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS version_padron CASCADE"))
            await conn.execute(
                text(
                    "INSERT INTO tenant (id, name, slug, created_at, updated_at) "
                    "VALUES ('11111111-1111-1111-1111-111111111111', 'Migration 008 Tenant', "
                    "'migration-008-test-tenant', now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )
            await _seed_rol_catalog(conn, "11111111-1111-1111-1111-111111111111")

        await _run_migration_fn(engine, "upgrade")

        async with engine.connect() as conn:
            version_padron_exists = await conn.scalar(
                text("SELECT to_regclass('public.version_padron') IS NOT NULL")
            )
            assert version_padron_exists is True

            entrada_padron_exists = await conn.scalar(
                text("SELECT to_regclass('public.entrada_padron') IS NOT NULL")
            )
            assert entrada_padron_exists is True

            for perm_codigo in ("padron:importar", "padron:vaciar", "padron:ver"):
                seeded = await conn.scalar(
                    text(
                        "SELECT EXISTS (SELECT 1 FROM permiso WHERE codigo = :codigo "
                        "AND tenant_id = '11111111-1111-1111-1111-111111111111')"
                    ),
                    {"codigo": perm_codigo},
                )
                assert seeded is True, f"Permission {perm_codigo} was not seeded"

            for perm_codigo in ("padron:importar", "padron:vaciar", "padron:ver"):
                granted_roles = await conn.execute(
                    text("""
                        SELECT r.codigo FROM rol_permiso rp
                        JOIN rol r ON r.id = rp.rol_id
                        JOIN permiso p ON p.id = rp.permiso_id
                        WHERE p.codigo = :codigo
                        AND rp.tenant_id = '11111111-1111-1111-1111-111111111111'
                    """),
                    {"codigo": perm_codigo},
                )
                granted = {row[0] for row in granted_roles}
                assert granted == {"COORDINADOR", "ADMIN"}, (
                    f"Permission {perm_codigo} granted to {granted}, expected COORDINADOR, ADMIN"
                )

        await _run_migration_fn(engine, "downgrade")

        async with engine.connect() as conn:
            version_padron_exists = await conn.scalar(
                text("SELECT to_regclass('public.version_padron') IS NOT NULL")
            )
            assert version_padron_exists is False

            entrada_padron_exists = await conn.scalar(
                text("SELECT to_regclass('public.entrada_padron') IS NOT NULL")
            )
            assert entrada_padron_exists is False

            for perm_codigo in ("padron:importar", "padron:vaciar", "padron:ver"):
                seeded = await conn.scalar(
                    text(
                        "SELECT EXISTS (SELECT 1 FROM permiso WHERE codigo = :codigo "
                        "AND tenant_id = '11111111-1111-1111-1111-111111111111')"
                    ),
                    {"codigo": perm_codigo},
                )
                assert seeded is False, f"Permission {perm_codigo} still seeded after downgrade"

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.tables["version_padron"].create)
            await conn.run_sync(Base.metadata.tables["entrada_padron"].create)
    finally:
        await engine.dispose()


async def test_migration_008_seed_is_idempotent(test_db_url: str):
    engine = create_async_engine(test_db_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS entrada_padron CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS version_padron CASCADE"))
            await conn.execute(
                text(
                    "INSERT INTO tenant (id, name, slug, created_at, updated_at) "
                    "VALUES ('33333333-3333-3333-3333-333333333333', 'Migration 008 Idempotent', "
                    "'migration-008-idempotent-tenant', now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
            )
            await _seed_rol_catalog(conn, "33333333-3333-3333-3333-333333333333")

        await _run_migration_fn(engine, "upgrade")

        async with engine.begin() as conn:
            def _rerun(sync_conn):
                ctx = MigrationContext.configure(sync_conn)
                with Operations.context(ctx):
                    migration_008._seed_padron_permisos_for_tenant(
                        sync_conn, "33333333-3333-3333-3333-333333333333"
                    )
            await conn.run_sync(_rerun)

        async with engine.connect() as conn:
            for perm_codigo in ("padron:importar", "padron:vaciar", "padron:ver"):
                permiso_count = await conn.scalar(
                    text(
                        "SELECT COUNT(*) FROM permiso WHERE codigo = :codigo "
                        "AND tenant_id = '33333333-3333-3333-3333-333333333333'"
                    ),
                    {"codigo": perm_codigo},
                )
                assert permiso_count == 1, (
                    f"Permission {perm_codigo} duplicated (count={permiso_count})"
                )

        await _run_migration_fn(engine, "downgrade")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.tables["version_padron"].create)
            await conn.run_sync(Base.metadata.tables["entrada_padron"].create)
    finally:
        await engine.dispose()
