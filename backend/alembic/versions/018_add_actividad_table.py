"""Add actividad table and actividad_id FK to calificacion (C-25).

Revision ID: 018_add_actividad_table
Revises: d1e2f3a4b5c6
Create Date: 2026-06-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "018_add_actividad_table"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create actividad table
    op.create_table(
        "actividad",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "dictado_id",
            UUID(as_uuid=True),
            sa.ForeignKey("dictado.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("fecha_limite", sa.Date, nullable=True),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_by_id",
            UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "updated_by_id",
            UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_actividad_tenant_dictado",
        "actividad",
        ["tenant_id", "dictado_id"],
    )

    # 2. Add actividad_id column to calificacion (nullable FK)
    op.add_column(
        "calificacion",
        sa.Column(
            "actividad_id",
            UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_calificacion_actividad_id",
        "calificacion",
        "actividad",
        ["actividad_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_calificacion_tenant_actividad",
        "calificacion",
        ["tenant_id", "actividad_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_calificacion_tenant_actividad", table_name="calificacion")
    op.drop_constraint(
        "fk_calificacion_actividad_id", "calificacion", type_="foreignkey"
    )
    op.drop_column("calificacion", "actividad_id")

    op.drop_index("ix_actividad_tenant_dictado", table_name="actividad")
    op.drop_table("actividad")
