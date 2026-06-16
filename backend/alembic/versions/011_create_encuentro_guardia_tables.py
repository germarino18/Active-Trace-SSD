"""Create slot_encuentro, instancia_encuentro, guardia tables.

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-06-15 23:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── slot_encuentro ─────────────────────────────────────────────────
    op.create_table(
        "slot_encuentro",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignacion.id", ondelete="SET NULL"), nullable=True),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("dia_semana", sa.String(20), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("cant_semanas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fecha_unica", sa.Date(), nullable=True),
        sa.Column("meet_url", sa.String(500), nullable=True),
        sa.Column("vig_desde", sa.Date(), nullable=False),
        sa.Column("vig_hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_slot_encuentro_tenant_dictado", "slot_encuentro", ["tenant_id", "dictado_id"])
    op.create_index("ix_slot_encuentro_tenant_asignacion", "slot_encuentro", ["tenant_id", "asignacion_id"])

    # ── instancia_encuentro ────────────────────────────────────────────
    op.create_table(
        "instancia_encuentro",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slot_id", UUID(as_uuid=True), sa.ForeignKey("slot_encuentro.id", ondelete="SET NULL"), nullable=True),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignacion.id", ondelete="SET NULL"), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Programado"),
        sa.Column("meet_url", sa.String(500), nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_instancia_tenant_dictado", "instancia_encuentro", ["tenant_id", "dictado_id"])
    op.create_index("ix_instancia_tenant_slot", "instancia_encuentro", ["tenant_id", "slot_id"])
    op.create_index("ix_instancia_tenant_estado", "instancia_encuentro", ["tenant_id", "estado"])

    # ── guardia ────────────────────────────────────────────────────────
    op.create_table(
        "guardia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dia", sa.String(20), nullable=False),
        sa.Column("horario", sa.String(50), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Pendiente"),
        sa.Column("comentarios", sa.Text(), nullable=True),
        sa.Column("creada_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_guardia_tenant_dictado", "guardia", ["tenant_id", "dictado_id"])
    op.create_index("ix_guardia_tenant_asignacion", "guardia", ["tenant_id", "asignacion_id"])
    op.create_index("ix_guardia_tenant_estado", "guardia", ["tenant_id", "estado"])


def downgrade() -> None:
    op.drop_index("ix_guardia_tenant_estado", table_name="guardia")
    op.drop_index("ix_guardia_tenant_asignacion", table_name="guardia")
    op.drop_index("ix_guardia_tenant_dictado", table_name="guardia")
    op.drop_table("guardia")
    op.drop_index("ix_instancia_tenant_estado", table_name="instancia_encuentro")
    op.drop_index("ix_instancia_tenant_slot", table_name="instancia_encuentro")
    op.drop_index("ix_instancia_tenant_dictado", table_name="instancia_encuentro")
    op.drop_table("instancia_encuentro")
    op.drop_index("ix_slot_encuentro_tenant_asignacion", table_name="slot_encuentro")
    op.drop_index("ix_slot_encuentro_tenant_dictado", table_name="slot_encuentro")
    op.drop_table("slot_encuentro")
