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
    / "009_create_calificacion_umbral_materia.py"
)
_spec = importlib.util.spec_from_file_location("migration_009", _MIGRATION_PATH)
migration_009 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration_009)


async def _run_migration_fn(engine, fn_name: str):
    async with engine.begin() as conn:
        def _run(sync_conn):
            ctx = MigrationContext.configure(sync_conn)
            with Operations.context(ctx):
                getattr(migration_009, fn_name)()
        await conn.run_sync(_run)


async def test_migration_009_up_and_down(test_db_url: str):
    engine = create_async_engine(test_db_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS calificacion"))
            await conn.execute(text("DROP TABLE IF EXISTS umbral_materia"))

        await _run_migration_fn(engine, "upgrade")

        async with engine.connect() as conn:
            calificacion_exists = await conn.scalar(
                text("SELECT to_regclass('public.calificacion') IS NOT NULL")
            )
            assert calificacion_exists is True

            umbral_materia_exists = await conn.scalar(
                text("SELECT to_regclass('public.umbral_materia') IS NOT NULL")
            )
            assert umbral_materia_exists is True

            # Assert indexes exist via pg_indexes
            indexes = (await conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE tablename IN ('calificacion', 'umbral_materia')")
            )).scalars().all()
            index_names = set(indexes)
            assert "ix_calificacion_tenant_dictado" in index_names
            assert "ix_calificacion_tenant_entrada" in index_names
            assert "ix_umbral_materia_tenant_asignacion_dictado" in index_names

        await _run_migration_fn(engine, "downgrade")

        async with engine.connect() as conn:
            calificacion_exists = await conn.scalar(
                text("SELECT to_regclass('public.calificacion') IS NOT NULL")
            )
            assert calificacion_exists is False

            umbral_materia_exists = await conn.scalar(
                text("SELECT to_regclass('public.umbral_materia') IS NOT NULL")
            )
            assert umbral_materia_exists is False

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.tables["calificacion"].create)
            await conn.run_sync(Base.metadata.tables["umbral_materia"].create)
    finally:
        await engine.dispose()
