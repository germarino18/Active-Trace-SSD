"""Add vigencia to dictado, create usuario_rol and evaluacion_materia tables (C-34)

Revision ID: a1b2c3d4e5f6
Revises: d1e2f3a4b5c6
Create Date: 2026-06-19 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9a8b7c6d5e4f"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Add vig_desde / vig_hasta to dictado ────────────────────────────
    with op.batch_alter_table("dictado") as batch_op:
        batch_op.add_column(
            sa.Column("vig_desde", sa.Date(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("vig_hasta", sa.Date(), nullable=True)
        )

    # ── 2. Create usuario_rol table ────────────────────────────────────────
    op.create_table(
        "usuario_rol",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rol_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("desde", sa.Date(), nullable=True),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rol_id"], ["rol.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_usuario_rol_usuario_tenant",
        "usuario_rol",
        ["tenant_id", "usuario_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ── 3. Create evaluacion_materia table ─────────────────────────────────
    op.create_table(
        "evaluacion_materia",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("instancia", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_evaluacion_materia_materia_tenant",
        "evaluacion_materia",
        ["tenant_id", "materia_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_table("evaluacion_materia")
    op.drop_table("usuario_rol")
    with op.batch_alter_table("dictado") as batch_op:
        batch_op.drop_column("vig_hasta")
        batch_op.drop_column("vig_desde")
