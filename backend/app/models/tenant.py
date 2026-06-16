from sqlalchemy import Boolean, Column, ForeignKey, Index, String, UUID, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr

from app.models.base import Base
from app.models.mixins import AuditMixin, BaseMixin, SoftDeleteMixin, TenantMixin


class Tenant(BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "tenant"

    @declared_attr
    def tenant_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("tenant.id", ondelete="CASCADE"),
            nullable=True,
        )

    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    settings = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    aprobacion_comunicaciones = Column(Boolean, nullable=False, server_default=text("false"))

    __table_args__ = (
        Index(
            "ix_tenant_slug",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_tenant_slug_deleted", "slug", "deleted_at"),
    )
