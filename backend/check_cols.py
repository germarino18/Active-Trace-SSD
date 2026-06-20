"""Verify columns exist in hilo_conversacion."""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def check():
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        r = await conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'hilo_conversacion'")
        )
        cols = [row[0] for row in r]
        print("Columns:", cols)
    await engine.dispose()


asyncio.run(check())
