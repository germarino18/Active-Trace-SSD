"""Create tarea and comentario_tarea tables.

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-06-16 09:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a0b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tarea",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id", ondelete="SET NULL"), nullable=True),
        sa.Column("asignado_a", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asignado_por", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE"),
        sa.Column("descripcion", sa.Text, nullable=False),
        sa.Column("contexto_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tarea_tenant_asignado_estado", "tarea", ["tenant_id", "asignado_a", "estado"])
    op.create_index("ix_tarea_tenant_estado_materia", "tarea", ["tenant_id", "estado", "materia_id"])

    op.create_table(
        "comentario_tarea",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tarea_id", UUID(as_uuid=True), sa.ForeignKey("tarea.id", ondelete="CASCADE"), nullable=False),
        sa.Column("autor_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("texto", sa.Text, nullable=False),
        sa.Column("creado_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_comentario_tarea_tarea_creado", "comentario_tarea", ["tarea_id", "creado_at"])


def downgrade() -> None:
    op.drop_index("ix_comentario_tarea_tarea_creado", table_name="comentario_tarea")
    op.drop_table("comentario_tarea")
    op.drop_index("ix_tarea_tenant_estado_materia", table_name="tarea")
    op.drop_index("ix_tarea_tenant_asignado_estado", table_name="tarea")
    op.drop_table("tarea")
