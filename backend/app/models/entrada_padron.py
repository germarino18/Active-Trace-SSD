from sqlalchemy import Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.crypto import EncryptedString
from app.models.base import Base
from app.models.mixins import BaseMixin, TenantMixin


class EntradaPadron(BaseMixin, TenantMixin, Base):
    __tablename__ = "entrada_padron"

    version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("version_padron.id", ondelete="CASCADE"),
        nullable=False,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=True,
    )
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    email = Column(EncryptedString, nullable=True)
    comision = Column(String(100), nullable=True)
    regional = Column(String(100), nullable=True)

    __table_args__ = (
        Index(
            "ix_entrada_padron_tenant_version",
            "tenant_id",
            "version_id",
        ),
    )
