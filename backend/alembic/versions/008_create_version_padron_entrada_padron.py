"""Create version_padron, entrada_padron tables; seed padron permissions.

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-06-15 19:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── padron permissions seed ───────────────────────────────────────────
_PADRON_PERMISOS = [
    ("padron:importar", "padron"),
    ("padron:vaciar", "padron"),
    ("padron:ver", "padron"),
]
_PADRON_ROLES = ["COORDINADOR", "ADMIN"]


def _seed_padron_permisos_for_tenant(conn, tenant_id: str) -> None:
    for codigo, modulo in _PADRON_PERMISOS:
        conn.execute(
            text("""
                INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :descripcion, :modulo, now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
            """),
            {
                "tenant_id": tenant_id,
                "codigo": codigo,
                "nombre": codigo,
                "descripcion": None,
                "modulo": modulo,
            },
        )

    for role_codigo in _PADRON_ROLES:
        for codigo, _modulo in _PADRON_PERMISOS:
            conn.execute(
                text("""
                    INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at)
                    SELECT gen_random_uuid(), :tenant_id, r.id, p.id, false, now(), now()
                    FROM rol r, permiso p
                    WHERE r.tenant_id = :tenant_id AND r.codigo = :role_codigo AND r.deleted_at IS NULL
                      AND p.tenant_id = :tenant_id AND p.codigo = :permiso_codigo AND p.deleted_at IS NULL
                    ON CONFLICT (tenant_id, rol_id, permiso_id) DO NOTHING
                """),
                {
                    "tenant_id": tenant_id,
                    "role_codigo": role_codigo,
                    "permiso_codigo": codigo,
                },
            )


def _unseed_padron_permisos_for_tenant(conn, tenant_id: str) -> None:
    for codigo, _modulo in _PADRON_PERMISOS:
        conn.execute(
            text("""
                DELETE FROM rol_permiso
                WHERE tenant_id = :tenant_id
                  AND permiso_id IN (
                      SELECT id FROM permiso WHERE tenant_id = :tenant_id AND codigo = :codigo
                  )
            """),
            {"tenant_id": tenant_id, "codigo": codigo},
        )
        conn.execute(
            text("""
                DELETE FROM permiso WHERE tenant_id = :tenant_id AND codigo = :codigo
            """),
            {"tenant_id": tenant_id, "codigo": codigo},
        )


def upgrade() -> None:
    # ── version_padron ─────────────────────────────────────────────────
    op.create_table(
        "version_padron",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cargado_por", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cargado_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("activa", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_version_padron_tenant_dictado",
        "version_padron",
        ["tenant_id", "dictado_id"],
    )
    op.create_index(
        "ix_version_padron_dictado_activa",
        "version_padron",
        ["tenant_id", "dictado_id"],
        unique=True,
        postgresql_where=sa.text("activa = true"),
    )

    # ── entrada_padron ─────────────────────────────────────────────────
    op.create_table(
        "entrada_padron",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", UUID(as_uuid=True), sa.ForeignKey("version_padron.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("apellidos", sa.String(255), nullable=False),
        sa.Column("email", sa.String, nullable=True),
        sa.Column("comision", sa.String(100), nullable=True),
        sa.Column("regional", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_entrada_padron_tenant_version",
        "entrada_padron",
        ["tenant_id", "version_id"],
    )

    # ── seed padron permissions ────────────────────────────────────────
    conn = op.get_bind()
    tenant_ids = [str(row[0]) for row in conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL"))]
    for tenant_id in tenant_ids:
        _seed_padron_permisos_for_tenant(conn, tenant_id)


def downgrade() -> None:
    conn = op.get_bind()
    tenant_ids = [str(row[0]) for row in conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL"))]
    for tenant_id in tenant_ids:
        _unseed_padron_permisos_for_tenant(conn, tenant_id)

    op.drop_index("ix_entrada_padron_tenant_version", table_name="entrada_padron")
    op.drop_table("entrada_padron")

    op.drop_index("ix_version_padron_dictado_activa", table_name="version_padron")
    op.drop_index("ix_version_padron_tenant_dictado", table_name="version_padron")
    op.drop_table("version_padron")
