from sqlalchemy import ARRAY, Boolean, Column, DateTime, Index, String, Text, VARCHAR, text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class User(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "users"

    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    roles = Column(ARRAY(VARCHAR), nullable=False, server_default=text("'{}'::varchar[]"))
    totp_secret = Column(Text, nullable=True)
    totp_enabled_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "ix_users_email_tenant",
            "tenant_id",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
