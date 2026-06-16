"""Seed liquidacion permissions for all existing tenants.

Adds liquidaciones:ver, liquidaciones:calcular, liquidaciones:configurar-salarios
to the FINANZAS role for every tenant.

Revision ID: 16aeacd08188
Revises: a6f5588d22a5
Create Date: 2026-06-16 18:30:49.148092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = "16aeacd08188"
down_revision: Union[str, Sequence[str], None] = "a6f5588d22a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_PERMISOS = [
    ("liquidaciones:ver", "Ver liquidaciones del período", "liquidaciones"),
    ("liquidaciones:calcular", "Calcular liquidaciones del período", "liquidaciones"),
    ("liquidaciones:configurar-salarios", "Configurar grilla salarial", "liquidaciones"),
]


def upgrade() -> None:
    conn = op.get_bind()

    # Get all active tenants
    tenants = conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL")).fetchall()
    if not tenants:
        return

    for (tenant_id,) in tenants:
        tid = str(tenant_id)

        # Look up FINANZAS role for this tenant
        row = conn.execute(
            text("SELECT id FROM rol WHERE tenant_id = :tid AND codigo = 'FINANZAS' AND deleted_at IS NULL"),
            {"tid": tid},
        ).fetchone()
        if row is None:
            # No FINANZAS role for this tenant yet — skip
            continue
        finanzas_rol_id = str(row[0])

        for codigo, descripcion, modulo in NEW_PERMISOS:
            # Check if permission already exists for this tenant
            existing = conn.execute(
                text("SELECT id FROM permiso WHERE tenant_id = :tid AND codigo = :cod AND deleted_at IS NULL"),
                {"tid": tid, "cod": codigo},
            ).fetchone()

            if existing is not None:
                continue  # Already seeded

            # Create permission
            conn.execute(
                text("""
                    INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
                    VALUES (gen_random_uuid(), :tid, :cod, :cod, :desc, :mod, NOW(), NOW())
                """),
                {"tid": tid, "cod": codigo, "desc": descripcion, "mod": modulo},
            )

            # Fetch the newly created permission id
            perm = conn.execute(
                text("SELECT id FROM permiso WHERE tenant_id = :tid AND codigo = :cod AND deleted_at IS NULL"),
                {"tid": tid, "cod": codigo},
            ).fetchone()
            if perm is None:
                continue
            perm_id = str(perm[0])

            # Assign to FINANZAS
            existing_rp = conn.execute(
                text("SELECT id FROM rol_permiso WHERE tenant_id = :tid AND rol_id = :rid AND permiso_id = :pid"),
                {"tid": tid, "rid": finanzas_rol_id, "pid": perm_id},
            ).fetchone()
            if existing_rp is None:
                conn.execute(
                    text("""
                        INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at)
                        VALUES (gen_random_uuid(), :tid, :rid, :pid, false, NOW(), NOW())
                    """),
                    {"tid": tid, "rid": finanzas_rol_id, "pid": perm_id},
                )


def downgrade() -> None:
    conn = op.get_bind()
    tenants = conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL")).fetchall()

    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for codigo, _, _ in NEW_PERMISOS:
            conn.execute(
                text("""
                    DELETE FROM rol_permiso
                    WHERE permiso_id IN (
                        SELECT id FROM permiso
                        WHERE tenant_id = :tid AND codigo = :cod
                    )
                    AND tenant_id = :tid
                """),
                {"tid": tid, "cod": codigo},
            )
            conn.execute(
                text("DELETE FROM permiso WHERE tenant_id = :tid AND codigo = :cod"),
                {"tid": tid, "cod": codigo},
            )
