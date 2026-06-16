"""Create programa_materia and fecha_academica tables.

Revision ID: c0d1e2f3a4b5
Revises: b1c2d3e4f5a6
Create Date: 2026-06-16 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "c0d1e2f3a4b5"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "programa_materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("referencia_archivo", sa.String(), nullable=False),
        sa.Column("cargado_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_programa_materia_tenant_dictado",
        "programa_materia",
        ["tenant_id", "dictado_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "fecha_academica",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("periodo", sa.String(20), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_fecha_academica_tenant_dictado", "fecha_academica", ["tenant_id", "dictado_id"])
    op.create_index("ix_fecha_academica_dictado_periodo", "fecha_academica", ["dictado_id", "periodo"])
    op.create_unique_constraint(
        "uq_fecha_tenant_dictado_tipo_numero",
        "fecha_academica",
        ["tenant_id", "dictado_id", "tipo", "numero"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_fecha_tenant_dictado_tipo_numero", table_name="fecha_academica")
    op.drop_index("ix_fecha_academica_dictado_periodo", table_name="fecha_academica")
    op.drop_index("ix_fecha_academica_tenant_dictado", table_name="fecha_academica")
    op.drop_table("fecha_academica")
    op.drop_index("ix_programa_materia_tenant_dictado", table_name="programa_materia")
    op.drop_table("programa_materia")
