"""Create liquidacion-related tables: salario_base, salario_plus, clave_plus, materia_clave_plus, liquidacion, factura + seed permissions.

Revision ID: a6f5588d22a5
Revises: c0d1e2f3a4b5
Create Date: 2026-06-16 18:00:00.000000

NOTE: revision was changed from d0e1f2a3b4c5 (conflicted with 010) to a6f5588d22a5.

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "a6f5588d22a5"
down_revision: Union[str, Sequence[str], None] = "c0d1e2f3a4b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── salario_base ────────────────────────────────────────────────
    op.create_table(
        "salario_base",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rol", sa.String(30), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_salario_base_tenant_rol_vigencia",
        "salario_base",
        ["tenant_id", "rol"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_salario_base_tenant_desde",
        "salario_base",
        ["tenant_id", "desde"],
    )

    # ── salario_plus ────────────────────────────────────────────────
    op.create_table(
        "salario_plus",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grupo", sa.String(50), nullable=False),
        sa.Column("rol", sa.String(30), nullable=False),
        sa.Column("descripcion", sa.String(255), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_salario_plus_tenant_grupo_rol_vigencia",
        "salario_plus",
        ["tenant_id", "grupo", "rol"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_salario_plus_tenant_desde",
        "salario_plus",
        ["tenant_id", "desde"],
    )

    # ── clave_plus ──────────────────────────────────────────────────
    op.create_table(
        "clave_plus",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo", sa.String(30), nullable=False),
        sa.Column("descripcion", sa.String(255), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_clave_plus_tenant_codigo",
        "clave_plus",
        ["tenant_id", "codigo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ── materia_clave_plus ──────────────────────────────────────────
    op.create_table(
        "materia_clave_plus",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clave_plus_id", UUID(as_uuid=True), sa.ForeignKey("clave_plus.id", ondelete="CASCADE"), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_materia_clave_plus_tenant_materia",
        "materia_clave_plus",
        ["tenant_id", "materia_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_materia_clave_plus_tenant_clave",
        "materia_clave_plus",
        ["tenant_id", "clave_plus_id"],
    )

    # ── liquidacion ─────────────────────────────────────────────────
    op.create_table(
        "liquidacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("periodo", sa.String(7), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rol", sa.String(30), nullable=False),
        sa.Column("comisiones", sa.Text(), nullable=True),
        sa.Column("monto_base", sa.Numeric(12, 2), nullable=False),
        sa.Column("monto_plus", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("es_nexo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("excluido_por_factura", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Abierta'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_liquidacion_tenant_periodo_cohorte",
        "liquidacion",
        ["tenant_id", "periodo", "cohorte_id"],
    )
    op.create_index(
        "ix_liquidacion_tenant_usuario_periodo",
        "liquidacion",
        ["tenant_id", "usuario_id", "periodo"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_liquidacion_tenant_estado",
        "liquidacion",
        ["tenant_id", "estado"],
    )

    # ── factura ─────────────────────────────────────────────────────
    op.create_table(
        "factura",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("periodo", sa.String(7), nullable=False),
        sa.Column("detalle", sa.Text(), nullable=True),
        sa.Column("referencia_archivo", sa.String(500), nullable=True),
        sa.Column("tamano_kb", sa.Numeric(10, 2), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Pendiente'")),
        sa.Column("cargada_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("abonada_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_factura_tenant_usuario", "factura", ["tenant_id", "usuario_id"])
    op.create_index("ix_factura_tenant_periodo", "factura", ["tenant_id", "periodo"])
    op.create_index("ix_factura_tenant_estado", "factura", ["tenant_id", "estado"])

    # ── Seed permissions for FINANZAS role ──────────────────────────
    # Fetch FINANZAS rol_id, then create missing permissions
    conn = op.get_bind()

    # Get the FINANZAS role id
    result = conn.execute(
        sa.text("SELECT id FROM rol WHERE codigo = 'FINANZAS' LIMIT 1")
    )
    row = result.fetchone()
    if row is not None:
        finanzas_rol_id = row[0]

        # Permission definitions: (codigo, descripcion, modulo)
        new_perms = [
            ("liquidaciones:ver", "Ver liquidaciones del período", "liquidaciones"),
            ("liquidaciones:calcular", "Calcular liquidaciones del período", "liquidaciones"),
            ("liquidaciones:configurar-salarios", "Configurar grilla salarial", "liquidaciones"),
        ]

        for codigo, descripcion, modulo in new_perms:
            # Check if permission already exists
            existing = conn.execute(
                sa.text("SELECT id FROM permiso WHERE codigo = :codigo AND tenant_id IS NULL LIMIT 1"),
                {"codigo": codigo},
            ).fetchone()

            if existing is None:
                # Create permission (global, tenant_id=NULL means available to all tenants)
                conn.execute(
                    sa.text(
                        "INSERT INTO permiso (id, codigo, descripcion, modulo, created_at, updated_at) "
                        "VALUES (gen_random_uuid(), :codigo, :descripcion, :modulo, NOW(), NOW())"
                    ),
                    {"codigo": codigo, "descripcion": descripcion, "modulo": modulo},
                )
                # Get the newly created permission id
                perm_result = conn.execute(
                    sa.text("SELECT id FROM permiso WHERE codigo = :codigo AND tenant_id IS NULL LIMIT 1"),
                    {"codigo": codigo},
                )
                perm_row = perm_result.fetchone()
                if perm_row is not None:
                    perm_id = perm_row[0]
                    # Assign to FINANZAS role
                    existing_rp = conn.execute(
                        sa.text(
                            "SELECT id FROM rol_permiso WHERE rol_id = :rol_id AND permiso_id = :perm_id LIMIT 1"
                        ),
                        {"rol_id": finanzas_rol_id, "perm_id": perm_id},
                    ).fetchone()
                    if existing_rp is None:
                        conn.execute(
                            sa.text(
                                "INSERT INTO rol_permiso (id, rol_id, permiso_id, created_at, updated_at) "
                                "VALUES (gen_random_uuid(), :rol_id, :perm_id, NOW(), NOW())"
                            ),
                            {"rol_id": finanzas_rol_id, "perm_id": perm_id},
                        )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("factura")
    op.drop_table("liquidacion")
    op.drop_table("materia_clave_plus")
    op.drop_table("clave_plus")
    op.drop_table("salario_plus")
    op.drop_table("salario_base")
