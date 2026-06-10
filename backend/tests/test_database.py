import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db


async def test_db_select_one(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1


async def test_db_session_close_on_exception(db_session: AsyncSession):
    connection = db_session.sync_session.connection()
    pool = connection.engine.pool
    checked_out_before = pool.checkedout()
    try:
        async with db_session as session:
            await session.execute(text("SELECT 1"))
            raise ValueError("test error")
    except ValueError:
        pass
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
