import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.carrera import Carrera
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import CarreraCreate, CarreraUpdate
from app.services.audit.audit_logger import AuditLogger


class CarreraService:
    """Reglas de negocio de Carrera (E1).

    Unicidad `(tenant_id, codigo)` entre carreras vivas (D4), validada
    aquí antes del insert; el índice único parcial en DB es la red de
    seguridad. Mutaciones se auditan vía `AuditLogger`.
    """

    def __init__(self, carrera_repo: CarreraRepository, audit_repo: AuditLogRepository):
        self._repo = carrera_repo
        self._audit = AuditLogger(repository=audit_repo)

    async def create(
        self,
        data: CarreraCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Carrera:
        existing = await self._repo.find_by_codigo(current_user.tenant_id, data.codigo)
        if existing is not None:
            raise ValidationException(
                message=f"Ya existe una carrera con el código '{data.codigo}'",
                details={"codigo": data.codigo},
            )

        carrera = await self._repo.create(
            {
                "codigo": data.codigo,
                "nombre": data.nombre,
                "estado": "Activa",
            }
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.CARRERA_CREAR,
            detalle={"id": str(carrera.id), "codigo": carrera.codigo},
            filas_afectadas=1,
            request=request,
        )
        return carrera

    async def update(
        self,
        carrera_id: uuid.UUID,
        data: CarreraUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Carrera:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if "estado" in update_data:
            update_data["estado"] = update_data["estado"].value

        if "codigo" in update_data:
            existing = await self._repo.find_by_codigo(current_user.tenant_id, update_data["codigo"])
            if existing is not None and existing.id != carrera_id:
                raise ValidationException(
                    message=f"Ya existe una carrera con el código '{update_data['codigo']}'",
                    details={"codigo": update_data["codigo"]},
                )

        carrera = await self._repo.update(carrera_id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.CARRERA_ACTUALIZAR,
            detalle={"id": str(carrera.id), "cambios": update_data},
            filas_afectadas=1,
            request=request,
        )
        return carrera

    async def soft_delete(
        self,
        carrera_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Carrera:
        carrera = await self._repo.soft_delete(carrera_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.CARRERA_ELIMINAR,
            detalle={"id": str(carrera.id)},
            filas_afectadas=1,
            request=request,
        )
        return carrera
