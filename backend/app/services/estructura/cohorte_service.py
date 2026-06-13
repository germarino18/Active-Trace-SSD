import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException, ValidationException
from app.models.cohorte import Cohorte
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import CohorteCreate, CohorteUpdate
from app.services.audit.audit_logger import AuditLogger


class CohorteService:
    """Reglas de negocio de Cohorte (E2).

    Unicidad `(tenant_id, carrera_id, nombre)` entre cohortes vivas (D4).
    D5: una carrera Inactiva no admite cohortes abiertas (`vig_hasta`
    nulo).
    """

    def __init__(
        self,
        cohorte_repo: CohorteRepository,
        carrera_repo: CarreraRepository,
        audit_repo: AuditLogRepository,
    ):
        self._repo = cohorte_repo
        self._carrera_repo = carrera_repo
        self._audit = AuditLogger(repository=audit_repo)

    async def _check_carrera_activa_for_open_cohorte(
        self, carrera_id: uuid.UUID, vig_hasta
    ) -> None:
        if vig_hasta is not None:
            return  # cohorte cerrada: no aplica la regla D5
        carrera = await self._carrera_repo.find_by_id(carrera_id)
        if carrera is None:
            raise NotFoundException(resource="Carrera", id=carrera_id)
        if carrera.estado != "Activa":
            raise ValidationException(
                message="La carrera está inactiva: no admite cohortes abiertas",
                details={"carrera_id": str(carrera_id)},
            )

    async def create(
        self,
        data: CohorteCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Cohorte:
        existing = await self._repo.find_by_nombre(
            current_user.tenant_id, data.carrera_id, data.nombre
        )
        if existing is not None:
            raise ValidationException(
                message=f"Ya existe una cohorte '{data.nombre}' para esta carrera",
                details={"carrera_id": str(data.carrera_id), "nombre": data.nombre},
            )

        await self._check_carrera_activa_for_open_cohorte(data.carrera_id, data.vig_hasta)

        cohorte = await self._repo.create(
            {
                "carrera_id": data.carrera_id,
                "nombre": data.nombre,
                "anio": data.anio,
                "vig_desde": data.vig_desde,
                "vig_hasta": data.vig_hasta,
                "estado": "Activa",
            }
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COHORTE_CREAR,
            detalle={"id": str(cohorte.id), "carrera_id": str(cohorte.carrera_id), "nombre": cohorte.nombre},
            filas_afectadas=1,
            request=request,
        )
        return cohorte

    async def update(
        self,
        cohorte_id: uuid.UUID,
        data: CohorteUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Cohorte:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if "estado" in update_data:
            update_data["estado"] = update_data["estado"].value

        cohorte = await self._repo.find_by_id(cohorte_id)
        if cohorte is None:
            raise NotFoundException(resource="Cohorte", id=cohorte_id)

        if "nombre" in update_data:
            existing = await self._repo.find_by_nombre(
                current_user.tenant_id, cohorte.carrera_id, update_data["nombre"]
            )
            if existing is not None and existing.id != cohorte_id:
                raise ValidationException(
                    message=f"Ya existe una cohorte '{update_data['nombre']}' para esta carrera",
                    details={"carrera_id": str(cohorte.carrera_id), "nombre": update_data["nombre"]},
                )

        vig_hasta = update_data.get("vig_hasta", cohorte.vig_hasta)
        await self._check_carrera_activa_for_open_cohorte(cohorte.carrera_id, vig_hasta)

        cohorte = await self._repo.update(cohorte_id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COHORTE_ACTUALIZAR,
            detalle={"id": str(cohorte.id), "cambios": {k: str(v) for k, v in update_data.items()}},
            filas_afectadas=1,
            request=request,
        )
        return cohorte

    async def soft_delete(
        self,
        cohorte_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Cohorte:
        cohorte = await self._repo.soft_delete(cohorte_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COHORTE_ELIMINAR,
            detalle={"id": str(cohorte.id)},
            filas_afectadas=1,
            request=request,
        )
        return cohorte
