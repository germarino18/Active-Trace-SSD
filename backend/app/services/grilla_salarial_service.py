"""Service for grilla salarial (salary grid ABM with overlap validation)."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.schemas.liquidaciones import (
    SalarioBaseCreate,
    SalarioBaseRead,
    SalarioBaseUpdate,
    SalarioPlusCreate,
    SalarioPlusRead,
    SalarioPlusUpdate,
)
from app.core.exceptions import BusinessRuleViolation


class GrillaSalarialService:
    def __init__(
        self,
        salario_base_repo: SalarioBaseRepository,
        salario_plus_repo: SalarioPlusRepository,
        session: AsyncSession,
    ):
        self._base_repo = salario_base_repo
        self._plus_repo = salario_plus_repo
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "GrillaSalarialService":
        return cls(
            salario_base_repo=SalarioBaseRepository(session=session, tenant_id=tenant_id),
            salario_plus_repo=SalarioPlusRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    # ── SalarioBase ─────────────────────────────────────────────────

    async def crear_base(self, data: SalarioBaseCreate) -> SalarioBaseRead:
        has_overlap = await self._base_repo.check_solapamiento(
            rol=data.rol, desde=data.desde, hasta=data.hasta,
        )
        if has_overlap:
            raise BusinessRuleViolation(
                message=f"Ya existe un SalarioBase vigente para el rol {data.rol} en el período solicitado",
                code="salario_base_solapamiento",
            )
        base = await self._base_repo.create(data.model_dump())
        return SalarioBaseRead.model_validate(base)

    async def listar_bases(
        self, rol: str | None = None, vigente_en: str | None = None,
    ) -> list[SalarioBaseRead]:
        if vigente_en:
            from datetime import date
            fecha = date.fromisoformat(vigente_en)
            bases = await self._base_repo.find_vigente_en(rol or "", fecha)
            return [SalarioBaseRead.model_validate(b) for b in (bases if isinstance(bases, list) else [bases])] if bases else []
        bases = await self._base_repo.find_all_by_rol(rol=rol)
        return [SalarioBaseRead.model_validate(b) for b in bases]

    async def obtener_base(self, id: uuid.UUID) -> SalarioBaseRead:
        from app.core.exceptions import NotFoundException
        base = await self._base_repo.find_by_id(id)
        if base is None:
            raise NotFoundException(resource="SalarioBase", id=id)
        return SalarioBaseRead.model_validate(base)

    async def actualizar_base(
        self, id: uuid.UUID, data: SalarioBaseUpdate,
    ) -> SalarioBaseRead:
        base = await self._base_repo.find_by_id(id)
        if base is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(resource="SalarioBase", id=id)

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if "rol" in update_data or "desde" in update_data or "hasta" in update_data:
            has_overlap = await self._base_repo.check_solapamiento(
                rol=update_data.get("rol", base.rol),
                desde=update_data.get("desde", base.desde),
                hasta=update_data.get("hasta", base.hasta),
                exclude_id=id,
            )
            if has_overlap:
                raise BusinessRuleViolation(
                    message=f"La actualización genera solapamiento para el rol {update_data.get('rol', base.rol)}",
                    code="salario_base_solapamiento",
                )

        updated = await self._base_repo.update(id, update_data)
        return SalarioBaseRead.model_validate(updated)

    async def eliminar_base(self, id: uuid.UUID) -> None:
        await self._base_repo.soft_delete(id)

    # ── SalarioPlus ─────────────────────────────────────────────────

    async def crear_plus(self, data: SalarioPlusCreate) -> SalarioPlusRead:
        has_overlap = await self._plus_repo.check_solapamiento(
            grupo=data.grupo, rol=data.rol, desde=data.desde, hasta=data.hasta,
        )
        if has_overlap:
            raise BusinessRuleViolation(
                message=f"Ya existe un SalarioPlus vigente para el grupo {data.grupo} y rol {data.rol} en el período solicitado",
                code="salario_plus_solapamiento",
            )
        plus = await self._plus_repo.create(data.model_dump())
        return SalarioPlusRead.model_validate(plus)

    async def listar_plus(
        self, grupo: str | None = None, rol: str | None = None,
    ) -> list[SalarioPlusRead]:
        plus_list = await self._plus_repo.find_by_grupo_rol(grupo=grupo, rol=rol)
        return [SalarioPlusRead.model_validate(p) for p in plus_list]

    async def obtener_plus(self, id: uuid.UUID) -> SalarioPlusRead:
        from app.core.exceptions import NotFoundException
        plus = await self._plus_repo.find_by_id(id)
        if plus is None:
            raise NotFoundException(resource="SalarioPlus", id=id)
        return SalarioPlusRead.model_validate(plus)

    async def actualizar_plus(
        self, id: uuid.UUID, data: SalarioPlusUpdate,
    ) -> SalarioPlusRead:
        plus = await self._plus_repo.find_by_id(id)
        if plus is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(resource="SalarioPlus", id=id)

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if "grupo" in update_data or "rol" in update_data or "desde" in update_data or "hasta" in update_data:
            has_overlap = await self._plus_repo.check_solapamiento(
                grupo=update_data.get("grupo", plus.grupo),
                rol=update_data.get("rol", plus.rol),
                desde=update_data.get("desde", plus.desde),
                hasta=update_data.get("hasta", plus.hasta),
                exclude_id=id,
            )
            if has_overlap:
                raise BusinessRuleViolation(
                    message=f"La actualización genera solapamiento para el grupo {update_data.get('grupo', plus.grupo)} y rol {update_data.get('rol', plus.rol)}",
                    code="salario_plus_solapamiento",
                )

        updated = await self._plus_repo.update(id, update_data)
        return SalarioPlusRead.model_validate(updated)

    async def eliminar_plus(self, id: uuid.UUID) -> None:
        await self._plus_repo.soft_delete(id)
