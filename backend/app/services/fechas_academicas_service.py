import uuid
from collections import defaultdict

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException, ValidationException
from app.models.fecha_academica import TipoFechaAcademica
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.schemas.auth import CurrentUser
from app.schemas.fechas_academicas import (
    FechaAcademicaCreate,
    FechaAcademicaRead,
    FechaAcademicaUpdate,
    LmsContentFragment,
)
from app.services.audit.audit_logger import AuditLogger

_ORDERED_TIPOS = [
    TipoFechaAcademica.PARCIAL,
    TipoFechaAcademica.TP,
    TipoFechaAcademica.COLOQUIO,
    TipoFechaAcademica.RECUPERATORIO,
]


class FechasAcademicasService:
    def __init__(
        self,
        repo: FechaAcademicaRepository,
        audit_repo: AuditLogRepository,
    ):
        self._repo = repo
        self._audit = AuditLogger(repository=audit_repo)

    @classmethod
    def create(cls, db, tenant_id: uuid.UUID) -> "FechasAcademicasService":
        return cls(
            repo=FechaAcademicaRepository(session=db, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
        )

    async def create_fecha(
        self,
        data: FechaAcademicaCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> FechaAcademicaRead:
        if await self._repo.exists_by_dictado_tipo_numero(
            data.dictado_id, data.tipo, data.numero
        ):
            raise ValidationException(
                message="Ya existe una fecha académica con este tipo y número para el dictado",
                details={
                    "dictado_id": str(data.dictado_id),
                    "tipo": data.tipo,
                    "numero": data.numero,
                },
            )

        fecha = await self._repo.create(data.model_dump())

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.FECHA_ACADEMICA_CREAR,
            detalle={
                "id": str(fecha.id),
                "dictado_id": str(fecha.dictado_id),
                "tipo": fecha.tipo,
                "numero": fecha.numero,
                "periodo": fecha.periodo,
            },
            filas_afectadas=1,
            request=request,
        )
        return FechaAcademicaRead(
            id=fecha.id,
            dictado_id=fecha.dictado_id,
            tipo=fecha.tipo,
            numero=fecha.numero,
            periodo=fecha.periodo,
            fecha=fecha.fecha,
            titulo=fecha.titulo,
            created_at=fecha.created_at,
            updated_at=fecha.updated_at,
        )

    async def update_fecha(
        self,
        id: uuid.UUID,
        data: FechaAcademicaUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> FechaAcademicaRead:
        fecha = await self._repo.find_by_id(id)
        if fecha is None:
            raise NotFoundException(resource="FechaAcademica", id=id)

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:
            fecha = await self._repo.update(id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.FECHA_ACADEMICA_ACTUALIZAR,
            detalle={"id": str(id), "cambios": update_data},
            filas_afectadas=1,
            request=request,
        )
        return FechaAcademicaRead(
            id=fecha.id,
            dictado_id=fecha.dictado_id,
            tipo=fecha.tipo,
            numero=fecha.numero,
            periodo=fecha.periodo,
            fecha=fecha.fecha,
            titulo=fecha.titulo,
            created_at=fecha.created_at,
            updated_at=fecha.updated_at,
        )

    async def get_fecha(self, id: uuid.UUID, current_user: CurrentUser) -> FechaAcademicaRead:
        fecha = await self._repo.find_by_id(id)
        if fecha is None:
            raise NotFoundException(resource="FechaAcademica", id=id)
        return FechaAcademicaRead(
            id=fecha.id,
            dictado_id=fecha.dictado_id,
            tipo=fecha.tipo,
            numero=fecha.numero,
            periodo=fecha.periodo,
            fecha=fecha.fecha,
            titulo=fecha.titulo,
            created_at=fecha.created_at,
            updated_at=fecha.updated_at,
        )

    async def list_fechas(
        self,
        dictado_id: uuid.UUID,
        periodo: str | None,
        skip: int,
        limit: int,
        current_user: CurrentUser,
    ) -> list[FechaAcademicaRead]:
        fechas = await self._repo.find_by_dictado_periodo(
            dictado_id, periodo, skip=skip, limit=limit
        )
        return [
            FechaAcademicaRead(
                id=f.id,
                dictado_id=f.dictado_id,
                tipo=f.tipo,
                numero=f.numero,
                periodo=f.periodo,
                fecha=f.fecha,
                titulo=f.titulo,
                created_at=f.created_at,
                updated_at=f.updated_at,
            )
            for f in fechas
        ]

    async def list_calendar(
        self,
        dictado_id: uuid.UUID,
        periodo: str | None,
        current_user: CurrentUser,
    ) -> dict[str, list[FechaAcademicaRead]]:
        fechas = await self._repo.find_calendar(dictado_id, periodo)
        grouped: dict[str, list[FechaAcademicaRead]] = defaultdict(list)
        for f in fechas:
            key = f.fecha.strftime("%Y-%m")
            grouped[key].append(
                FechaAcademicaRead(
                    id=f.id,
                    dictado_id=f.dictado_id,
                    tipo=f.tipo,
                    numero=f.numero,
                    periodo=f.periodo,
                    fecha=f.fecha,
                    titulo=f.titulo,
                    created_at=f.created_at,
                    updated_at=f.updated_at,
                )
            )
        return dict(grouped)

    async def generate_lms_fragment(
        self,
        dictado_id: uuid.UUID,
        periodo: str | None,
        current_user: CurrentUser,
    ) -> LmsContentFragment:
        fechas = await self._repo.find_calendar(dictado_id, periodo)
        if not fechas:
            return LmsContentFragment(
                contenido="No hay fechas académicas cargadas para este período."
            )

        fechas.sort(key=lambda f: f.fecha)

        lines: list[str] = ["# Cronograma de Evaluaciones", ""]
        for tipo in _ORDERED_TIPOS:
            tipo_fechas = [f for f in fechas if f.tipo == tipo.value]
            if not tipo_fechas:
                continue
            lines.append(f"## {tipo.value}")
            for f in tipo_fechas:
                date_str = f.fecha.strftime("%d/%m/%Y")
                lines.append(f"- **{f.titulo}** ({f.tipo} {f.numero}) — {date_str}")
            lines.append("")

        return LmsContentFragment(contenido="\n".join(lines).strip())

    async def delete_fecha(
        self,
        id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ):
        fecha = await self._repo.find_by_id(id)
        if fecha is None:
            raise NotFoundException(resource="FechaAcademica", id=id)

        await self._repo.soft_delete(id)
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.FECHA_ACADEMICA_ELIMINAR,
            detalle={"id": str(id)},
            filas_afectadas=1,
            request=request,
        )
