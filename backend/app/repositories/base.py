import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.tenancy import TenantContext
from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(
        self,
        model: type[T],
        session: AsyncSession,
        tenant_id: uuid.UUID | None = None,
    ):
        self.model = model
        self.session = session
        self._tenant_id = tenant_id
        self._include_soft_deleted = False

    def _get_effective_tenant_id(self) -> uuid.UUID | None:
        if self._tenant_id is not None:
            return self._tenant_id
        return TenantContext.get()

    def _apply_tenant_scope(self, query):
        tenant_id = self._get_effective_tenant_id()
        if tenant_id is not None:
            query = query.where(self.model.tenant_id == tenant_id)
        return query

    def _apply_soft_delete_filter(self, query):
        if hasattr(self.model, "deleted_at") and not self._include_soft_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        return query

    def include_deleted(self):
        self._include_soft_deleted = True
        return self

    async def create(self, data: dict | BaseModel) -> T:
        if isinstance(data, BaseModel):
            data = data.model_dump()
        tenant_id = self._get_effective_tenant_id()
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            data.setdefault("tenant_id", tenant_id)
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def find_by_id(self, id: uuid.UUID) -> T | None:
        query = select(self.model).where(self.model.id == id)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_all(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[T]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by(self, **filters) -> list[T]:
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        query = self._apply_soft_delete_filter(query)
        for column, value in filters.items():
            column_attr = getattr(self.model, column, None)
            if column_attr is not None:
                query = query.where(column_attr == value)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def update(self, id: uuid.UUID, data: dict | BaseModel) -> T:
        if isinstance(data, BaseModel):
            data = data.model_dump()
        instance = await self.find_by_id(id)
        if instance is None:
            raise NotFoundException(resource=self.model.__name__, id=id)
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: uuid.UUID) -> T:
        instance = await self.find_by_id(id)
        if instance is None:
            raise NotFoundException(resource=self.model.__name__, id=id)
        if hasattr(instance, "soft_delete"):
            instance.soft_delete()
        elif hasattr(instance, "deleted_at"):
            from datetime import UTC, datetime
            instance.deleted_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def hard_delete(self, id: uuid.UUID) -> None:
        instance = await self.find_by_id(id)
        if instance is None:
            raise NotFoundException(resource=self.model.__name__, id=id)
        await self.session.delete(instance)
        await self.session.flush()
