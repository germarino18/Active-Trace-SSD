"""One-shot remediation: re-encrypt plaintext emails in entrada_padron.

Reads `entrada_padron.email` via raw SQL (bypassing the EncryptedString
TypeDecorator), detects plaintext values, and encrypts them in-place using
`encrypt_value()`. Already-encrypted values are skipped.

Usage:
    python -m scripts.remediate_encrypted_entrada_padron
    python -m scripts.remediate_encrypted_entrada_padron --dry-run

Exit codes:
    0 = success (all rows processed or no-op)
    1 = error (transaction rolled back)
"""
import argparse
import asyncio
import base64
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.security import decrypt_value, encrypt_value, get_encryption_key


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-encrypt plaintext emails in entrada_padron"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview rows that would be updated without writing changes",
    )
    args = parser.parse_args()

    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    key = get_encryption_key()

    async with session_factory() as session:
        try:
            rows = await session.execute(
                text("SELECT id, email FROM entrada_padron WHERE email IS NOT NULL")
            )
            remediated = 0
            skipped = 0

            for row in rows:
                row_id, email_value = row

                # Check if already encrypted (valid base64 + decrypts)
                already_encrypted = False
                try:
                    raw = base64.b64decode(email_value)
                    if len(raw) > 12:
                        decrypt_value(email_value, key)
                        already_encrypted = True
                except Exception:
                    already_encrypted = False

                if already_encrypted:
                    skipped += 1
                    continue

                encrypted = encrypt_value(email_value, key)

                if args.dry_run:
                    print(
                        f"[DRY-RUN] Would update entrada_padron.id={row_id}: "
                        f"'{email_value}' → '{encrypted[:32]}...'"
                    )
                else:
                    await session.execute(
                        text("UPDATE entrada_padron SET email = :enc WHERE id = :id"),
                        {"enc": encrypted, "id": row_id},
                    )

                remediated += 1

            if not args.dry_run:
                await session.commit()

        except Exception as exc:
            await session.rollback()
            print(f"ERROR: {exc}", flush=True)
            await engine.dispose()
            return 1

    if args.dry_run:
        if remediated == 0:
            print("No rows to remediate.")
        else:
            print(f"Would remediate {remediated} rows. Run without --dry-run to apply.")
    else:
        if remediated == 0 and skipped == 0:
            print("No rows to remediate.")
        elif remediated == 0 and skipped > 0:
            print(f"No rows to remediate, skipped {skipped} already-encrypted rows.")
        else:
            print(f"Remediated {remediated} rows, skipped {skipped} rows.")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
