"""Create aviso and acknowledgment_aviso tables.

Revision ID: a0b1c2d3e4f5
Revises: f0e1d2c3b4a5
Create Date: 2026-06-16 08:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "a0b1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "f0e1d2c3b4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aviso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alcance", sa.String(20), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rol_destino", sa.String(50), nullable=True),
        sa.Column("severidad", sa.String(20), nullable=False, server_default="INFO"),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column("inicio_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("requiere_ack", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_aviso_tenant_alcance_activo", "aviso", ["tenant_id", "alcance", "activo"])
    op.create_index("ix_aviso_tenant_materia", "aviso", ["tenant_id", "materia_id"])
    op.create_index("ix_aviso_tenant_cohorte", "aviso", ["tenant_id", "cohorte_id"])

    op.create_table(
        "acknowledgment_aviso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aviso_id", UUID(as_uuid=True), sa.ForeignKey("aviso.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("confirmado_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ack_aviso_aviso_usuario", "acknowledgment_aviso", ["aviso_id", "usuario_id"], unique=True, postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("ix_ack_aviso_tenant_aviso", "acknowledgment_aviso", ["tenant_id", "aviso_id"])
    op.create_index("ix_ack_aviso_tenant_usuario", "acknowledgment_aviso", ["tenant_id", "usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_ack_aviso_tenant_usuario", table_name="acknowledgment_aviso")
    op.drop_index("ix_ack_aviso_tenant_aviso", table_name="acknowledgment_aviso")
    op.drop_index("ix_ack_aviso_aviso_usuario", table_name="acknowledgment_aviso")
    op.drop_table("acknowledgment_aviso")
    op.drop_index("ix_aviso_tenant_cohorte", table_name="aviso")
    op.drop_index("ix_aviso_tenant_materia", table_name="aviso")
    op.drop_index("ix_aviso_tenant_alcance_activo", table_name="aviso")
    op.drop_table("aviso")
