"""Create rol, permiso, rol_permiso tables with seed data

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-06-12 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── Seed data definitions ──────────────────────────────────────────────
ROLES = [
    ("ALUMNO", "Alumno", "Estudiante cursando una carrera"),
    ("TUTOR", "Tutor", "Tutor de alumnos"),
    ("PROFESOR", "Profesor", "Docente a cargo de comisiones"),
    ("COORDINADOR", "Coordinador", "Coordinador académico"),
    ("NEXO", "Nexo", "Enlace institucional (pendiente PA-25)"),
    ("ADMIN", "Admin", "Administrador del tenant"),
    ("FINANZAS", "Finanzas", "Gestión financiera y liquidaciones"),
]

PERMISOS = [
    ("estado-academico:ver", "estado-academico"),
    ("evaluacion:reservar", "evaluacion"),
    ("avisos:confirmar", "avisos"),
    ("calificaciones:importar", "calificaciones"),
    ("atrasados:ver", "atrasados"),
    ("entregas:sin-corregir", "entregas"),
    ("comunicacion:enviar", "comunicacion"),
    ("comunicacion:aprobar", "comunicacion"),
    ("encuentros:gestionar", "encuentros"),
    ("guardias:registrar", "guardias"),
    ("tareas:gestionar", "tareas"),
    ("avisos:publicar", "avisos"),
    ("equipos:gestionar", "equipos"),
    ("estructura:gestionar", "estructura"),
    ("usuarios:gestionar", "usuarios"),
    ("auditoria:ver", "auditoria"),
    ("grilla:operar", "grilla"),
    ("liquidaciones:cerrar", "liquidaciones"),
    ("facturas:gestionar", "facturas"),
    ("configurar:tenant", "configurar"),
]

# Each entry: (role_codigo, permiso_codigo, es_propio)
MATRIX = [
    # ALUMNO
    ("ALUMNO", "estado-academico:ver", False),
    ("ALUMNO", "evaluacion:reservar", False),
    ("ALUMNO", "avisos:confirmar", False),
    # TUTOR
    ("TUTOR", "avisos:confirmar", False),
    ("TUTOR", "atrasados:ver", False),
    ("TUTOR", "entregas:sin-corregir", False),
    ("TUTOR", "encuentros:gestionar", False),
    ("TUTOR", "guardias:registrar", True),
    # PROFESOR
    ("PROFESOR", "avisos:confirmar", False),
    ("PROFESOR", "calificaciones:importar", True),
    ("PROFESOR", "atrasados:ver", True),
    ("PROFESOR", "entregas:sin-corregir", True),
    ("PROFESOR", "comunicacion:enviar", True),
    ("PROFESOR", "encuentros:gestionar", True),
    ("PROFESOR", "guardias:registrar", True),
    ("PROFESOR", "tareas:gestionar", True),
    # COORDINADOR
    ("COORDINADOR", "avisos:confirmar", False),
    ("COORDINADOR", "calificaciones:importar", False),
    ("COORDINADOR", "atrasados:ver", False),
    ("COORDINADOR", "entregas:sin-corregir", False),
    ("COORDINADOR", "comunicacion:enviar", False),
    ("COORDINADOR", "comunicacion:aprobar", False),
    ("COORDINADOR", "encuentros:gestionar", False),
    ("COORDINADOR", "guardias:registrar", False),
    ("COORDINADOR", "tareas:gestionar", False),
    ("COORDINADOR", "avisos:publicar", False),
    ("COORDINADOR", "equipos:gestionar", False),
    ("COORDINADOR", "auditoria:ver", True),
    # NEXO — zero permissions
    # ADMIN
    ("ADMIN", "avisos:confirmar", False),
    ("ADMIN", "calificaciones:importar", False),
    ("ADMIN", "atrasados:ver", False),
    ("ADMIN", "entregas:sin-corregir", False),
    ("ADMIN", "comunicacion:enviar", False),
    ("ADMIN", "comunicacion:aprobar", False),
    ("ADMIN", "encuentros:gestionar", False),
    ("ADMIN", "guardias:registrar", False),
    ("ADMIN", "tareas:gestionar", False),
    ("ADMIN", "avisos:publicar", False),
    ("ADMIN", "equipos:gestionar", False),
    ("ADMIN", "estructura:gestionar", False),
    ("ADMIN", "usuarios:gestionar", False),
    ("ADMIN", "auditoria:ver", False),
    ("ADMIN", "configurar:tenant", False),
    # FINANZAS
    ("FINANZAS", "avisos:confirmar", False),
    ("FINANZAS", "auditoria:ver", False),
    ("FINANZAS", "grilla:operar", False),
    ("FINANZAS", "liquidaciones:cerrar", False),
    ("FINANZAS", "facturas:gestionar", False),
]


def _seed_for_tenant(conn, tenant_id: str):
    """Seed all permission data for a single tenant."""
    # Insert roles
    for codigo, nombre, descripcion in ROLES:
        conn.execute(
            text("""
                INSERT INTO rol (id, tenant_id, codigo, nombre, descripcion, created_at, updated_at)
                VALUES (gen_random_uuid(), :tenant_id, :codigo, :nombre, :descripcion, now(), now())
                ON CONFLICT (tenant_id, codigo) WHERE deleted_at IS NULL DO NOTHING
            """),
            {
                "tenant_id": tenant_id,
                "codigo": codigo,
                "nombre": nombre,
                "descripcion": descripcion,
            },
        )

    # Insert permissions
    for codigo, modulo in PERMISOS:
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

    # Insert rol_permiso (lookup by codigo)
    for role_codigo, permiso_codigo, es_propio in MATRIX:
        conn.execute(
            text("""
                INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at)
                SELECT gen_random_uuid(), :tenant_id, r.id, p.id, :es_propio, now(), now()
                FROM rol r, permiso p
                WHERE r.tenant_id = :tenant_id AND r.codigo = :role_codigo AND r.deleted_at IS NULL
                  AND p.tenant_id = :tenant_id AND p.codigo = :permiso_codigo AND p.deleted_at IS NULL
                ON CONFLICT (tenant_id, rol_id, permiso_id) DO NOTHING
            """),
            {
                "tenant_id": tenant_id,
                "role_codigo": role_codigo,
                "permiso_codigo": permiso_codigo,
                "es_propio": es_propio,
            },
        )


def upgrade() -> None:
    op.create_table(
        "rol",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_rol_codigo_tenant",
        "rol",
        ["tenant_id", "codigo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "permiso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("modulo", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_permiso_codigo_tenant",
        "permiso",
        ["tenant_id", "codigo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "rol_permiso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rol_id", UUID(as_uuid=True), sa.ForeignKey("rol.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permiso_id", UUID(as_uuid=True), sa.ForeignKey("permiso.id", ondelete="CASCADE"), nullable=False),
        sa.Column("es_propio", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_unique_constraint("uq_rol_permiso", "rol_permiso", ["tenant_id", "rol_id", "permiso_id"])

    # Seed data for all existing tenants
    conn = op.get_bind()
    result = conn.execute(
        text("SELECT id FROM tenant WHERE deleted_at IS NULL")
    )
    for row in result:
        _seed_for_tenant(conn, str(row[0]))


def downgrade() -> None:
    op.drop_constraint("uq_rol_permiso", "rol_permiso")
    op.drop_table("rol_permiso")
    op.drop_index("ix_permiso_codigo_tenant", table_name="permiso")
    op.drop_table("permiso")
    op.drop_index("ix_rol_codigo_tenant", table_name="rol")
    op.drop_table("rol")
