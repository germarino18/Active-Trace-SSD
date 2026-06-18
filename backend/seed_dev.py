"""Seed desarrollo: usuarios + asignaciones."""
import asyncio
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.auth.password_service import PasswordService


async def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Check if already seeded
        r = await session.execute(text("SELECT COUNT(*) FROM tenant"))
        if r.scalar() and r.scalar() > 0:
            print("Ya hay datos — omitiendo seed.")
            await engine.dispose()
            return

        tenant_id = uuid.uuid4()

        # 1. Create tenant
        await session.execute(
            text(
                "INSERT INTO tenant (id, tenant_id, name, slug, is_active, created_at, updated_at) "
                "VALUES (:tid, :tid, :name, :slug, true, NOW(), NOW())"
            ),
            {"tid": tenant_id, "name": "Universidad Demo", "slug": "demo"},
        )

        users_data = [
            {
                "email": "admin@demo.com",
                "pw": "Admin123!",
                "name": "Admin",
                "apellidos": "Demo",
                "roles": ["ADMIN", "COORDINADOR"],
            },
            {
                "email": "coordinador@demo.com",
                "pw": "Coord123!",
                "name": "Coordinador",
                "apellidos": "Demo",
                "roles": ["COORDINADOR"],
            },
            {
                "email": "profesor@demo.com",
                "pw": "Demo123!",
                "name": "Profesor",
                "apellidos": "Demo",
                "roles": ["PROFESOR"],
            },
            {
                "email": "finanzas@demo.com",
                "pw": "Fin123!",
                "name": "Finanzas",
                "apellidos": "Demo",
                "roles": ["FINANZAS"],
            },
            {
                "email": "nexo@demo.com",
                "pw": "Nexo123!",
                "name": "Nexo",
                "apellidos": "Demo",
                "roles": ["NEXO"],
            },
        ]

        for u in users_data:
            user_id = uuid.uuid4()
            usuario_id = uuid.uuid4()

            # users table
            await session.execute(
                text(
                    "INSERT INTO users (id, tenant_id, email, password_hash, display_name, is_active, roles, created_at, updated_at) "
                    "VALUES (:uid, :tid, :email, :pw, :name, true, :roles, NOW(), NOW())"
                ),
                {
                    "uid": user_id,
                    "tid": tenant_id,
                    "email": u["email"],
                    "pw": PasswordService.hash_password(u["pw"]),
                    "name": f"{u['name']} {u['apellidos']}",
                    "roles": u["roles"],
                },
            )

            # usuario table (business profile)
            await session.execute(
                text(
                    "INSERT INTO usuario (id, tenant_id, user_id, nombre, apellidos, legajo, facturador, estado, created_at, updated_at) "
                    "VALUES (:usid, :tid, :uid, :nom, :ape, :leg, false, 'Activo', NOW(), NOW())"
                ),
                {
                    "usid": usuario_id,
                    "tid": tenant_id,
                    "uid": user_id,
                    "nom": u["name"],
                    "ape": u["apellidos"],
                    "leg": u["email"].split("@")[0],
                },
            )

            # asignacion for each role
            for role in u["roles"]:
                asi_id = uuid.uuid4()
                await session.execute(
                    text(
                        "INSERT INTO asignacion (id, tenant_id, usuario_id, rol, desde, hasta, created_at, updated_at) "
                        "VALUES (:aid, :tid, :usid, :rol, NOW(), '2099-12-31', NOW(), NOW())"
                    ),
                    {
                        "aid": asi_id,
                        "tid": tenant_id,
                        "usid": usuario_id,
                        "rol": role,
                    },
                )

        await session.commit()
        print("\n✅ Seed completado exitosamente!\n")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║              CREDENCIALES DE DESARROLLO                 ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║  ROL          │ EMAIL                   │ PASSWORD     ║")
        print("║───────────────┼────────────────────────┼───────────────║")
        print("║  ADMIN        │ admin@demo.com          │ Admin123!    ║")
        print("║  COORDINADOR  │ coordinador@demo.com    │ Coord123!    ║")
        print("║  PROFESOR     │ profesor@demo.com       │ Demo123!     ║")
        print("║  FINANZAS     │ finanzas@demo.com       │ Fin123!      ║")
        print("║  NEXO         │ nexo@demo.com           │ Nexo123!     ║")
        print("╚══════════════════════════════════════════════════════════╝\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
