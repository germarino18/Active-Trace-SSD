"""Create audit_log table with append-only trigger and seed impersonacion:usar

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-12 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import text

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TRIGGER_FUNCTION_NAME = "audit_log_block_update_delete"
TRIGGER_NAME = "trg_audit_log_block_update_delete"

PERMISO_CODIGO = "impersonacion:usar"
PERMISO_MODULO = "impersonacion"


def _seed_impersonacion_permiso_for_tenant(conn, tenant_id: str) -> None:
    conn.execute(
        text("""
            INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
            VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :descripcion, :modulo, now(), now())
            ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
        """),
        {
            "tenant_id": tenant_id,
            "codigo": PERMISO_CODIGO,
            "nombre": PERMISO_CODIGO,
            "descripcion": None,
            "modulo": PERMISO_MODULO,
        },
    )


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("impersonado_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), nullable=True),
        sa.Column("accion", sa.String(100), nullable=False),
        sa.Column("detalle", JSONB, nullable=True),
        sa.Column("filas_afectadas", sa.Integer, nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_log_tenant_id", "audit_log", ["tenant_id"])
    op.create_index("ix_audit_log_fecha_hora", "audit_log", ["fecha_hora"])

    # ── Append-only enforcement (D2): DB-level trigger ──────────────────
    op.execute(f"""
        CREATE OR REPLACE FUNCTION {TRIGGER_FUNCTION_NAME}()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: % is not permitted', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute(f"DROP TRIGGER IF EXISTS {TRIGGER_NAME} ON audit_log")
    op.execute(f"""
        CREATE TRIGGER {TRIGGER_NAME}
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW EXECUTE FUNCTION {TRIGGER_FUNCTION_NAME}();
    """)

    # ── Seed impersonacion:usar permission for every existing tenant (D1) ──
    conn = op.get_bind()
    result = conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL"))
    for row in result:
        _seed_impersonacion_permiso_for_tenant(conn, str(row[0]))


def downgrade() -> None:
    op.execute(f"DROP TRIGGER IF EXISTS {TRIGGER_NAME} ON audit_log")
    op.execute(f"DROP FUNCTION IF EXISTS {TRIGGER_FUNCTION_NAME}()")

    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM permiso WHERE codigo = :codigo"),
        {"codigo": PERMISO_CODIGO},
    )

    op.drop_index("ix_audit_log_fecha_hora", table_name="audit_log")
    op.drop_index("ix_audit_log_tenant_id", table_name="audit_log")
    op.drop_table("audit_log")
