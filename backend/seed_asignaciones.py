"""Seed additional data: create usuario records and asignaciones for dev users."""
import asyncio
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Get tenant
        r = await session.execute(text("SELECT id FROM tenant WHERE slug = 'demo'"))
        tenant = r.scalar_one_or_none()
        if not tenant:
            print("Tenant 'demo' not found. Run seed_dev.py first.")
            await engine.dispose()
            return

        # Get all users
        r = await session.execute(
            text("SELECT id, email, roles FROM users WHERE tenant_id = :tid"),
            {"tid": tenant},
        )
        users = r.all()
        print(f"Found {len(users)} users")

        for uid, email, roles in users:
            # Insert into usuario table (PII fields)
            # Generate legajo
            legajo = email.split("@")[0]

            # Check if usuario already exists for this user
            existing = await session.execute(
                text("SELECT id FROM usuario WHERE user_id = :uid AND tenant_id = :tid"),
                {"uid": uid, "tid": tenant},
            )
            if existing.scalar_one_or_none():
                print(f"  ⏭️  {email} — usuario entry already exists")
                continue

            usuario_id = uuid.uuid4()
            await session.execute(
                text(
                    "INSERT INTO usuario (id, tenant_id, user_id, nombre, legajo, created_at, updated_at) "
                    "VALUES (:id, :tid, :uid, :nombre, :legajo, NOW(), NOW())"
                ),
                {
                    "id": usuario_id,
                    "tid": tenant,
                    "uid": uid,
                    "nombre": email.split("@")[0].capitalize(),
                    "legajo": legajo,
                },
            )
            print(f"  ✅ {email} → usuario created")

            # Create asignacion records for each role
            for role in roles:
                existing_asi = await session.execute(
                    text(
                        "SELECT id FROM asignacion "
                        "WHERE tenant_id = :tid AND user_id = :uid AND rol = :rol AND deleted_at IS NULL"
                    ),
                    {"tid": tenant, "uid": uid, "rol": role},
                )
                if existing_asi.scalar_one_or_none():
                    print(f"     ⏭️  {role} — already assigned")
                    continue

                asi_id = uuid.uuid4()
                await session.execute(
                    text(
                        "INSERT INTO asignacion (id, tenant_id, user_id, usuario_id, rol, activo, desde, hasta, created_at, updated_at) "
                        "VALUES (:id, :tid, :uid, :usid, :rol, true, NOW(), '2099-12-31 23:59:59+00', NOW(), NOW())"
                    ),
                    {
                        "id": asi_id,
                        "tid": tenant,
                        "uid": uid,
                        "usid": usuario_id,
                        "rol": role,
                    },
                )
                print(f"     ✅ {email} → {role} assigned")

        await session.commit()
        print("\n✅ Asignaciones creadas exitosamente!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
