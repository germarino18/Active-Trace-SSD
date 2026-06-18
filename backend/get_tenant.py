import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

async def main():
    e = create_async_engine(os.environ["DATABASE_URL"])
    sm = async_sessionmaker(e)
    async with sm() as s:
        r = await s.execute(text("SELECT id, slug FROM tenant"))
        for row in r.all():
            print(f"{row[0]} | {row[1]}")
    await e.dispose()

asyncio.run(main())
