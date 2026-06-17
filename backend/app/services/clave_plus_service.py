"""Service for ClavePlus and MateriaClavePlus management."""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.clave_plus_repository import ClavePlusRepository
from app.repositories.materia_clave_plus_repository import MateriaClavePlusRepository
from app.schemas.liquidaciones import (
    ClavePlusCreate,
    ClavePlusRead,
    ClavePlusUpdate,
    MateriaClavePlusCreate,
    MateriaClavePlusRead,
)
from app.core.exceptions import BusinessRuleViolation


class ClavePlusService:
    def __init__(
        self,
        clave_plus_repo: ClavePlusRepository,
        materia_clave_plus_repo: MateriaClavePlusRepository,
        session: AsyncSession,
    ):
        self._clave_repo = clave_plus_repo
        self._materia_clave_repo = materia_clave_plus_repo
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "ClavePlusService":
        return cls(
            clave_plus_repo=ClavePlusRepository(session=session, tenant_id=tenant_id),
            materia_clave_plus_repo=MateriaClavePlusRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    # ── ClavePlus ───────────────────────────────────────────────────

    async def crear_clave(self, data: ClavePlusCreate) -> ClavePlusRead:
        existing = await self._clave_repo.find_by_codigo(data.codigo)
        if existing is not None:
            raise BusinessRuleViolation(
                message=f"Ya existe una ClavePlus con código {data.codigo}",
                code="clave_plus_duplicado",
            )
        clave = await self._clave_repo.create(data.model_dump())
        return ClavePlusRead.model_validate(clave)

    async def listar_claves(self) -> list[ClavePlusRead]:
        claves = await self._clave_repo.find_all()
        return [ClavePlusRead.model_validate(c) for c in claves]

    async def obtener_clave(self, id: uuid.UUID) -> ClavePlusRead:
        from app.core.exceptions import NotFoundException
        clave = await self._clave_repo.find_by_id(id)
        if clave is None:
            raise NotFoundException(resource="ClavePlus", id=id)
        return ClavePlusRead.model_validate(clave)

    async def actualizar_clave(
        self, id: uuid.UUID, data: ClavePlusUpdate,
    ) -> ClavePlusRead:
        clave = await self._clave_repo.find_by_id(id)
        if clave is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(resource="ClavePlus", id=id)

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if "codigo" in update_data and update_data["codigo"] != clave.codigo:
            existing = await self._clave_repo.find_by_codigo(update_data["codigo"])
            if existing is not None:
                raise BusinessRuleViolation(
                    message=f"Ya existe una ClavePlus con código {update_data['codigo']}",
                    code="clave_plus_duplicado",
                )

        updated = await self._clave_repo.update(id, update_data)
        return ClavePlusRead.model_validate(updated)

    async def eliminar_clave(self, id: uuid.UUID) -> None:
        await self._clave_repo.soft_delete(id)

    # ── MateriaClavePlus ────────────────────────────────────────────

    async def crear_materia_clave(
        self, data: MateriaClavePlusCreate,
    ) -> MateriaClavePlusRead:
        has_overlap = await self._materia_clave_repo.check_solapamiento(
            materia_id=data.materia_id,
            desde=data.desde,
            hasta=data.hasta,
        )
        if has_overlap:
            raise BusinessRuleViolation(
                message="Ya existe una asignación de ClavePlus vigente para esta materia en el período solicitado",
                code="materia_clave_plus_solapamiento",
            )
        mcp = await self._materia_clave_repo.create(data.model_dump())
        return MateriaClavePlusRead.model_validate(mcp)

    async def listar_materias_clave(
        self, materia_id: uuid.UUID | None = None,
    ) -> list[MateriaClavePlusRead]:
        if materia_id:
            items = await self._materia_clave_repo.find_by_materia(materia_id)
        else:
            items = await self._materia_clave_repo.find_all()
        return [MateriaClavePlusRead.model_validate(m) for m in items]

    async def eliminar_materia_clave(self, id: uuid.UUID) -> None:
        await self._materia_clave_repo.soft_delete(id)
