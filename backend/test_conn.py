import asyncio
import asyncpg


async def main():
    # Try with no password (trust auth on localhost)
    print("Trying with no password...")
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            database="postgres",
        )
        result = await conn.fetchval("SELECT 1")
        print(f"Connected! Result: {result}")
        await conn.close()
    except Exception as e:
        print(f"No-pw error: {type(e).__name__}: {e}")

    # Try with ssl=False
    print("\nTrying with ssl=False...")
    try:
        from asyncpg import connect_utils
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres",
        )
        result = await conn.fetchval("SELECT 1")
        print(f"Connected! Result: {result}")
        await conn.close()
    except Exception as e:
        print(f"SSL=False error: {type(e).__name__}: {e}")

    # Print capabilities
    print(f"\nasyncpg version: {asyncpg.__version__}")


asyncio.run(main())
