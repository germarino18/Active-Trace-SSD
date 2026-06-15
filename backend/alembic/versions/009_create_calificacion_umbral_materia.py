"""Create calificacion, umbral_materia tables.

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-06-15 20:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB as _JSONB, UUID

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── calificacion ────────────────────────────────────────────────────
    op.create_table(
        "calificacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entrada_padron_id", UUID(as_uuid=True), sa.ForeignKey("entrada_padron.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actividad", sa.String(255), nullable=False),
        sa.Column("nota_numerica", sa.Numeric(5, 2), nullable=True),
        sa.Column("nota_textual", sa.String(100), nullable=True),
        sa.Column("aprobado", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("origen", sa.String(20), nullable=False, server_default="Importado"),
        sa.Column("importado_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_calificacion_tenant_dictado",
        "calificacion",
        ["tenant_id", "dictado_id"],
    )
    op.create_index(
        "ix_calificacion_tenant_entrada",
        "calificacion",
        ["tenant_id", "entrada_padron_id"],
    )

    # ── umbral_materia ──────────────────────────────────────────────────
    op.create_table(
        "umbral_materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("umbral_pct", sa.Integer, nullable=False, server_default=sa.text("60")),
        sa.Column("valores_aprobatorios", _JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_umbral_materia_tenant_asignacion_dictado",
        "umbral_materia",
        ["tenant_id", "asignacion_id", "dictado_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_umbral_materia_tenant_asignacion_dictado", table_name="umbral_materia")
    op.drop_table("umbral_materia")

    op.drop_index("ix_calificacion_tenant_entrada", table_name="calificacion")
    op.drop_index("ix_calificacion_tenant_dictado", table_name="calificacion")
    op.drop_table("calificacion")
