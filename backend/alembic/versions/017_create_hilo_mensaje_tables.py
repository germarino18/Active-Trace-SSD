"""Create hilo_conversacion, hilo_participante, mensaje tables for C-20.

Revision ID: d1e2f3a4b5c6
Revises: 16aeacd08188
Create Date: 2026-06-17 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "16aeacd08188"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hilo_conversacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asunto", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "hilo_participante",
        sa.Column("hilo_id", UUID(as_uuid=True), sa.ForeignKey("hilo_conversacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ultima_visto", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("hilo_id", "usuario_id"),
    )
    op.create_index("ix_hilo_participante_usuario", "hilo_participante", ["usuario_id"])

    op.create_table(
        "mensaje",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hilo_id", UUID(as_uuid=True), sa.ForeignKey("hilo_conversacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("remitente_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contenido", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_mensaje_hilo_created", "mensaje", ["hilo_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_mensaje_hilo_created", table_name="mensaje")
    op.drop_table("mensaje")
    op.drop_index("ix_hilo_participante_usuario", table_name="hilo_participante")
    op.drop_table("hilo_participante")
    op.drop_table("hilo_conversacion")
