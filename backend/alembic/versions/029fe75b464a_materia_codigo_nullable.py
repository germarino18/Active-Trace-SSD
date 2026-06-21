"""materia_codigo_nullable

Make materia.codigo nullable since it's optional in the schema.

Revision ID: 029fe75b464a
Revises: b1167f8b32f8
Create Date: 2026-06-19 22:56:53.587620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '029fe75b464a'
down_revision: Union[str, Sequence[str], None] = 'b1167f8b32f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('materia', 'codigo', existing_type=sa.String(50), nullable=True)


def downgrade() -> None:
    op.alter_column('materia', 'codigo', existing_type=sa.String(50), nullable=False)
