"""Create comunicacion table + tenant.aprobacion_comunicaciones flag.

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-06-15 22:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── comunicacion ─────────────────────────────────────────────────────
    op.create_table(
        "comunicacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enviado_por", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id", ondelete="CASCADE"), nullable=False),
        sa.Column("destinatario", sa.Text(), nullable=False),
        sa.Column("destinatario_hash", sa.String(64), nullable=False),
        sa.Column("asunto", sa.String(255), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Pendiente"),
        sa.Column("lote_id", UUID(as_uuid=True), nullable=False),
        sa.Column("enviado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reintentos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_comunicacion_tenant_lote", "comunicacion", ["tenant_id", "lote_id"])
    op.create_index("ix_comunicacion_tenant_estado", "comunicacion", ["tenant_id", "estado"])

    # ── tenant.aprobacion_comunicaciones flag ────────────────────────────
    op.add_column(
        "tenant",
        sa.Column("aprobacion_comunicaciones", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("tenant", "aprobacion_comunicaciones")
    op.drop_index("ix_comunicacion_tenant_estado", table_name="comunicacion")
    op.drop_index("ix_comunicacion_tenant_lote", table_name="comunicacion")
    op.drop_table("comunicacion")
