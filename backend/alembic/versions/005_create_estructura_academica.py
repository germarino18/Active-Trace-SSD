"""Create estructura academica tables: carrera, materia, cohorte, dictado

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-13 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _mixin_columns() -> list[sa.Column]:
    """Common columns from BaseMixin/SoftDeleteMixin/AuditMixin."""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    ]


def upgrade() -> None:
    # ── carrera (E1) ─────────────────────────────────────────────────
    op.create_table(
        "carrera",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activa"),
        *_mixin_columns(),
    )
    op.create_index(
        "ix_carrera_codigo_tenant",
        "carrera",
        ["tenant_id", "codigo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ── materia (E3, ADR-006) ────────────────────────────────────────
    op.create_table(
        "materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activa"),
        *_mixin_columns(),
    )
    op.create_index(
        "ix_materia_codigo_tenant",
        "materia",
        ["tenant_id", "codigo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ── cohorte (E2) ─────────────────────────────────────────────────
    op.create_table(
        "cohorte",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("anio", sa.Integer, nullable=True),
        sa.Column("vig_desde", sa.Date, nullable=True),
        sa.Column("vig_hasta", sa.Date, nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activa"),
        *_mixin_columns(),
    )
    op.create_index(
        "ix_cohorte_nombre_tenant",
        "cohorte",
        ["tenant_id", "carrera_id", "nombre"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ── dictado (ADR-006, D1: entidad raiz) ───────────────────────────
    op.create_table(
        "dictado",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id", ondelete="CASCADE"), nullable=False),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id", ondelete="CASCADE"), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activo"),
        *_mixin_columns(),
    )
    op.create_index(
        "ix_dictado_terna_tenant",
        "dictado",
        ["tenant_id", "materia_id", "carrera_id", "cohorte_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_dictado_terna_tenant", table_name="dictado")
    op.drop_table("dictado")

    op.drop_index("ix_cohorte_nombre_tenant", table_name="cohorte")
    op.drop_table("cohorte")

    op.drop_index("ix_materia_codigo_tenant", table_name="materia")
    op.drop_table("materia")

    op.drop_index("ix_carrera_codigo_tenant", table_name="carrera")
    op.drop_table("carrera")
