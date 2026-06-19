"""Dependency injection para FastAPI.

Slots implementados en C-01:
    get_db: sesión async de base de datos por request.

Slots reservados (a llenar en changes posteriores):
    get_current_user   → C-03 (JWT + Argon2id)
    get_tenant         → C-02 (resolución de tenant)
    require_permission → C-04 (RBAC) — see api/dependencies/permissions.py
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import database as db_module


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if db_module.async_session_maker is None:
        raise RuntimeError(
            "Database engine not initialized. Call init_engine() first."
        )
    async with db_module.async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
