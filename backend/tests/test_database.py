import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db


async def test_db_select_one(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1


async def test_db_session_close_on_exception(db_engine):
    """Verify connections are returned to pool after exception in session.

    Uses its own connection/session (not db_session fixture) to avoid
    corrupting the shared transactional session state.
    """
    pool = db_engine.pool
    checked_out_before = pool.checkedout()

    connection = await db_engine.connect()
    try:
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            async with session.begin():
                await session.execute(text("SELECT 1"))
                raise ValueError("test error")
        except ValueError:
            pass
        await session.close()
    finally:
        await connection.close()

    checked_out_after = pool.checkedout()
    assert checked_out_after == checked_out_before


async def test_get_db_raises_if_not_initialized():
    from app.core.database import async_session_maker, engine
    original_maker = async_session_maker
    original_engine = engine
    try:
        import app.core.database as db_module
        db_module.async_session_maker = None
        db_module.engine = None
        gen = get_db()
        with pytest.raises(RuntimeError, match="not initialized"):
            await gen.__anext__()
    finally:
        db_module.async_session_maker = original_maker
        db_module.engine = original_engine
