"""Add deleted_at column to entrada_padron for soft-delete support.

Revision ID: 019_add_deleted_at_entrada_padron
Revises: 018_add_actividad_table
Create Date: 2026-06-20 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019_add_deleted_at_ep"
down_revision: Union[str, Sequence[str], None] = "018_add_actividad_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "entrada_padron",
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_entrada_padron_deleted_at",
        "entrada_padron",
        ["deleted_at"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_entrada_padron_deleted_at", table_name="entrada_padron")
    op.drop_column("entrada_padron", "deleted_at")
