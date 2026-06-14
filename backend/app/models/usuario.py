from sqlalchemy import Boolean, Column, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID

from app.core.crypto import EncryptedString
from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Usuario(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    """Perfil de negocio de una persona (E4), 1:1 con la identidad de auth.

    `users` (C-02/C-03) sigue siendo solo-auth: `email`, `password_hash`,
    `roles` (deprecado, ver Asignacion). `Usuario` agrega los datos de
    negocio y la PII cifrada (D1). El vínculo 1:1 es `user_id` (FK ->
    users.id, UNIQUE, ondelete=CASCADE).

    `email` NO se duplica acá: vive solo en `users.email` (D1). `legajo` y
    `legajo_profesional` son atributos de negocio opcionales, nunca
    credencial ni selector de sesión (regla dura #14).
    """

    __tablename__ = "usuario"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    dni = Column(EncryptedString, nullable=True)
    cuil = Column(EncryptedString, nullable=True)
    cbu = Column(EncryptedString, nullable=True)
    alias_cbu = Column(EncryptedString, nullable=True)
    banco = Column(String(255), nullable=True)
    regional = Column(String(100), nullable=True)
    legajo = Column(String(50), nullable=True)
    legajo_profesional = Column(String(50), nullable=True)
    facturador = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    estado = Column(String(20), nullable=False, default="Activo", server_default="Activo")

    __table_args__ = (
        Index(
            "ix_usuario_user_id_tenant",
            "tenant_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
