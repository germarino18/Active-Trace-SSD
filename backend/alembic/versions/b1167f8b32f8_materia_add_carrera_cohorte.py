"""materia_add_carrera_cohorte

Add carrera_id and cohorte_id to materia table.

Revision ID: b1167f8b32f8
Revises: 9a8b7c6d5e4f
Create Date: 2026-06-19 22:47:21.394486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b1167f8b32f8'
down_revision: Union[str, Sequence[str], None] = '9a8b7c6d5e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add carrera_id and cohorte_id to materia
    op.add_column('materia', sa.Column('carrera_id', postgresql.UUID(), nullable=True))
    op.add_column('materia', sa.Column('cohorte_id', postgresql.UUID(), nullable=True))
    op.create_index('ix_materia_carrera', 'materia', ['carrera_id'], unique=False)
    op.create_index('ix_materia_cohorte', 'materia', ['cohorte_id'], unique=False)
    op.create_foreign_key('fk_materia_carrera', 'materia', 'carrera', ['carrera_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_materia_cohorte', 'materia', 'cohorte', ['cohorte_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_materia_carrera', 'materia', type_='foreignkey')
    op.drop_constraint('fk_materia_cohorte', 'materia', type_='foreignkey')
    op.drop_index('ix_materia_carrera', table_name='materia')
    op.drop_index('ix_materia_cohorte', table_name='materia')
    op.drop_column('materia', 'carrera_id')
    op.drop_column('materia', 'cohorte_id')
