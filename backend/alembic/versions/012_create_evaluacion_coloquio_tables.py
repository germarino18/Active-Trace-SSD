"""Create evaluacion, reserva_evaluacion, resultado_evaluacion, alumno_convocado tables.

Revision ID: f0e1d2c3b4a5
Revises: e1f2a3b4c5d6
Create Date: 2026-06-16 07:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "f0e1d2c3b4a5"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── evaluacion ──────────────────────────────────────────────────────
    op.create_table(
        "evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("instancia", sa.String(255), nullable=False),
        sa.Column("dias_disponibles", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("cupo_maximo", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activa"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_evaluacion_tenant_dictado", "evaluacion", ["tenant_id", "dictado_id"])
    op.create_index("ix_evaluacion_tenant_estado", "evaluacion", ["tenant_id", "estado"])

    # ── reserva_evaluacion ───────────────────────────────────────────────
    op.create_table(
        "reserva_evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activa"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_reserva_evaluacion_tenant_evaluacion", "reserva_evaluacion", ["tenant_id", "evaluacion_id"])
    op.create_index("ix_reserva_evaluacion_tenant_alumno", "reserva_evaluacion", ["tenant_id", "alumno_id"])
    op.create_unique_constraint("uq_reserva_evaluacion_alumno_activa", "reserva_evaluacion", ["evaluacion_id", "alumno_id"])

    # ── resultado_evaluacion ────────────────────────────────────────────
    op.create_table(
        "resultado_evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nota_final", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_resultado_evaluacion_tenant_evaluacion", "resultado_evaluacion", ["tenant_id", "evaluacion_id"])
    op.create_index("ix_resultado_evaluacion_tenant_alumno", "resultado_evaluacion", ["tenant_id", "alumno_id"])
    op.create_unique_constraint("uq_resultado_evaluacion_alumno", "resultado_evaluacion", ["evaluacion_id", "alumno_id"])

    # ── alumno_convocado ───────────────────────────────────────────────
    op.create_table(
        "alumno_convocado",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_alumno_convocado_tenant_evaluacion", "alumno_convocado", ["tenant_id", "evaluacion_id"])
    op.create_index("ix_alumno_convocado_tenant_alumno", "alumno_convocado", ["tenant_id", "alumno_id"])
    op.create_unique_constraint("uq_alumno_convocado_evaluacion_alumno", "alumno_convocado", ["evaluacion_id", "alumno_id"])


def downgrade() -> None:
    op.drop_constraint("uq_alumno_convocado_evaluacion_alumno", "alumno_convocado")
    op.drop_index("ix_alumno_convocado_tenant_alumno", table_name="alumno_convocado")
    op.drop_index("ix_alumno_convocado_tenant_evaluacion", table_name="alumno_convocado")
    op.drop_table("alumno_convocado")
    op.drop_constraint("uq_resultado_evaluacion_alumno", "resultado_evaluacion")
    op.drop_index("ix_resultado_evaluacion_tenant_alumno", table_name="resultado_evaluacion")
    op.drop_index("ix_resultado_evaluacion_tenant_evaluacion", table_name="resultado_evaluacion")
    op.drop_table("resultado_evaluacion")
    op.drop_constraint("uq_reserva_evaluacion_alumno_activa", "reserva_evaluacion")
    op.drop_index("ix_reserva_evaluacion_tenant_alumno", table_name="reserva_evaluacion")
    op.drop_index("ix_reserva_evaluacion_tenant_evaluacion", table_name="reserva_evaluacion")
    op.drop_table("reserva_evaluacion")
    op.drop_index("ix_evaluacion_tenant_estado", table_name="evaluacion")
    op.drop_index("ix_evaluacion_tenant_dictado", table_name="evaluacion")
    op.drop_table("evaluacion")
