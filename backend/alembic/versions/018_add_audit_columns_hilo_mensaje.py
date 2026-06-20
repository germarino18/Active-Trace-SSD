"""Add created_by_id and updated_by_id to hilo_conversacion and mensaje.

These columns were missing from migration 017 (AuditMixin columns).

Revision ID: a2b3c4d5e6f7
Revises: d1e2f3a4b5c6
Create Date: 2026-06-19 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # hilo_conversacion
    op.add_column(
        "hilo_conversacion",
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "hilo_conversacion",
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )

    # mensaje
    op.add_column(
        "mensaje",
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "mensaje",
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("mensaje", "updated_by_id")
    op.drop_column("mensaje", "created_by_id")
    op.drop_column("hilo_conversacion", "updated_by_id")
    op.drop_column("hilo_conversacion", "created_by_id")
