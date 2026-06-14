"""Create usuario, asignacion tables; seed equipos:asignar; backfill users.roles

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-06-13 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID, VARCHAR
from sqlalchemy.sql import text

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── equipos:asignar seed (D4/D5) ─────────────────────────────────────────
_EQUIPOS_ASIGNAR_PERMISO = ("equipos:asignar", "equipos")
_EQUIPOS_ASIGNAR_ROLES = ["COORDINADOR", "ADMIN"]


def _mixin_columns() -> list[sa.Column]:
    """Common columns from BaseMixin/SoftDeleteMixin/AuditMixin."""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    ]


def _seed_equipos_asignar_for_tenant(conn, tenant_id: str) -> None:
    """Seed `equipos:asignar` permission + rol_permiso for COORDINADOR/ADMIN."""
    codigo, modulo = _EQUIPOS_ASIGNAR_PERMISO
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

    for role_codigo in _EQUIPOS_ASIGNAR_ROLES:
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


def _unseed_equipos_asignar_for_tenant(conn, tenant_id: str) -> None:
    codigo, _modulo = _EQUIPOS_ASIGNAR_PERMISO
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


def _backfill_for_tenant(conn, tenant_id: str) -> None:
    """For each alive user in the tenant, ensure a `usuario` shell and an
    `asignacion` per `users.roles[i]` (D4): NULL context, `desde =
    users.created_at::date`, `hasta = NULL`. Idempotent via unique indexes
    and ON CONFLICT DO NOTHING.
    """
    users = conn.execute(
        text("""
            SELECT id, roles, created_at
            FROM users
            WHERE tenant_id = :tenant_id AND deleted_at IS NULL
        """),
        {"tenant_id": tenant_id},
    )
    for user_id, roles, created_at in users:
        if not roles:
            continue

        # Ensure a usuario shell exists (idempotent via unique partial index).
        conn.execute(
            text("""
                INSERT INTO usuario (id, tenant_id, user_id, nombre, apellidos, facturador, estado, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :user_id, '', '', false, 'Activo', now(), now())
                ON CONFLICT (tenant_id, user_id) WHERE deleted_at IS NULL DO NOTHING
            """),
            {"tenant_id": tenant_id, "user_id": user_id},
        )

        usuario_id = conn.execute(
            text("""
                SELECT id FROM usuario
                WHERE tenant_id = :tenant_id AND user_id = :user_id AND deleted_at IS NULL
            """),
            {"tenant_id": tenant_id, "user_id": user_id},
        ).scalar()

        for rol in roles:
            conn.execute(
                text("""
                    INSERT INTO asignacion (
                        id, tenant_id, usuario_id, rol, comisiones, desde, hasta, created_at, updated_at
                    )
                    SELECT gen_random_uuid(), :tenant_id, :usuario_id, CAST(:rol AS varchar(50)), '{}'::varchar[], :desde, NULL, now(), now()
                    WHERE NOT EXISTS (
                        SELECT 1 FROM asignacion
                        WHERE tenant_id = :tenant_id AND usuario_id = :usuario_id AND rol = CAST(:rol AS varchar(50))
                          AND dictado_id IS NULL AND materia_id IS NULL
                          AND carrera_id IS NULL AND cohorte_id IS NULL
                          AND deleted_at IS NULL
                    )
                """),
                {
                    "tenant_id": tenant_id,
                    "usuario_id": usuario_id,
                    "rol": rol,
                    "desde": created_at.date(),
                },
            )


def upgrade() -> None:
    # ── usuario (E4, D1) ─────────────────────────────────────────────
    op.create_table(
        "usuario",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("apellidos", sa.String(255), nullable=False),
        sa.Column("dni", sa.String, nullable=True),
        sa.Column("cuil", sa.String, nullable=True),
        sa.Column("cbu", sa.String, nullable=True),
        sa.Column("alias_cbu", sa.String, nullable=True),
        sa.Column("banco", sa.String(255), nullable=True),
        sa.Column("regional", sa.String(100), nullable=True),
        sa.Column("legajo", sa.String(50), nullable=True),
        sa.Column("legajo_profesional", sa.String(50), nullable=True),
        sa.Column("facturador", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activo"),
        *_mixin_columns(),
    )
    op.create_index(
        "ix_usuario_user_id_tenant",
        "usuario",
        ["tenant_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ── asignacion (E5, D3) ───────────────────────────────────────────
    op.create_table(
        "asignacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rol", sa.String(50), nullable=False),
        sa.Column("dictado_id", UUID(as_uuid=True), sa.ForeignKey("dictado.id", ondelete="CASCADE"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id", ondelete="CASCADE"), nullable=True),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id", ondelete="CASCADE"), nullable=True),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id", ondelete="CASCADE"), nullable=True),
        sa.Column("comisiones", ARRAY(VARCHAR), nullable=False, server_default=sa.text("'{}'::varchar[]")),
        sa.Column("responsable_id", UUID(as_uuid=True), sa.ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True),
        sa.Column("desde", sa.Date, nullable=False),
        sa.Column("hasta", sa.Date, nullable=True),
        *_mixin_columns(),
    )
    op.create_index("ix_asignacion_usuario_tenant", "asignacion", ["tenant_id", "usuario_id"])
    op.create_index("ix_asignacion_rol_tenant", "asignacion", ["tenant_id", "rol"])

    # ── seed equipos:asignar + backfill (D4/D5) ────────────────────────
    conn = op.get_bind()
    tenant_ids = [str(row[0]) for row in conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL"))]
    for tenant_id in tenant_ids:
        _seed_equipos_asignar_for_tenant(conn, tenant_id)
        _backfill_for_tenant(conn, tenant_id)


def downgrade() -> None:
    conn = op.get_bind()
    tenant_ids = [str(row[0]) for row in conn.execute(text("SELECT id FROM tenant WHERE deleted_at IS NULL"))]
    for tenant_id in tenant_ids:
        _unseed_equipos_asignar_for_tenant(conn, tenant_id)

    op.drop_index("ix_asignacion_rol_tenant", table_name="asignacion")
    op.drop_index("ix_asignacion_usuario_tenant", table_name="asignacion")
    op.drop_table("asignacion")

    op.drop_index("ix_usuario_user_id_tenant", table_name="usuario")
    op.drop_table("usuario")
