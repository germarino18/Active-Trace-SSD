import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException, ValidationException
from app.models.dictado import Dictado
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import DictadoCreate, DictadoUpdate
from app.services.audit.audit_logger import AuditLogger


class DictadoService:
    """Reglas de negocio de Dictado (ADR-006, entidad raiz — D1).

    - Unicidad de terna `(tenant_id, materia_id, carrera_id, cohorte_id)`
      entre dictados vivos (D4).
    - D2: `Dictado.carrera_id` MUST coincidir con `Cohorte.carrera_id` de
      la cohorte referida, validado en Service.
    - D5: no se crea un dictado sobre materia, carrera o cohorte
      Inactiva.
    """

    def __init__(
        self,
        dictado_repo: DictadoRepository,
        materia_repo: MateriaRepository,
        carrera_repo: CarreraRepository,
        cohorte_repo: CohorteRepository,
        audit_repo: AuditLogRepository,
    ):
        self._repo = dictado_repo
        self._materia_repo = materia_repo
        self._carrera_repo = carrera_repo
        self._cohorte_repo = cohorte_repo
        self._audit = AuditLogger(repository=audit_repo)

    async def _validate_referenced_entities(
        self, materia_id: uuid.UUID, carrera_id: uuid.UUID, cohorte_id: uuid.UUID
    ) -> None:
        materia = await self._materia_repo.find_by_id(materia_id)
        if materia is None:
            raise NotFoundException(resource="Materia", id=materia_id)

        carrera = await self._carrera_repo.find_by_id(carrera_id)
        if carrera is None:
            raise NotFoundException(resource="Carrera", id=carrera_id)

        cohorte = await self._cohorte_repo.find_by_id(cohorte_id)
        if cohorte is None:
            raise NotFoundException(resource="Cohorte", id=cohorte_id)

        # D2: consistencia carrera <-> cohorte, validada en Service.
        if cohorte.carrera_id != carrera_id:
            raise ValidationException(
                message="La carrera del dictado no coincide con la carrera de la cohorte referida",
                details={"carrera_id": str(carrera_id), "cohorte_carrera_id": str(cohorte.carrera_id)},
            )

        # D5: no se crea un dictado sobre materia/carrera/cohorte inactiva.
        if materia.estado != "Activa":
            raise ValidationException(
                message="No se puede crear un dictado sobre una materia inactiva",
                details={"materia_id": str(materia_id)},
            )
        if carrera.estado != "Activa":
            raise ValidationException(
                message="No se puede crear un dictado sobre una carrera inactiva",
                details={"carrera_id": str(carrera_id)},
            )
        if cohorte.estado != "Activa":
            raise ValidationException(
                message="No se puede crear un dictado sobre una cohorte inactiva",
                details={"cohorte_id": str(cohorte_id)},
            )

    async def create(
        self,
        data: DictadoCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Dictado:
        existing = await self._repo.find_by_terna(
            current_user.tenant_id, data.materia_id, data.carrera_id, data.cohorte_id
        )
        if existing is not None:
            raise ValidationException(
                message="Ya existe un dictado con esta combinación de materia, carrera y cohorte",
                details={
                    "materia_id": str(data.materia_id),
                    "carrera_id": str(data.carrera_id),
                    "cohorte_id": str(data.cohorte_id),
                },
            )

        await self._validate_referenced_entities(data.materia_id, data.carrera_id, data.cohorte_id)

        dictado = await self._repo.create(
            {
                "materia_id": data.materia_id,
                "carrera_id": data.carrera_id,
                "cohorte_id": data.cohorte_id,
                "estado": "Activo",
            }
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.DICTADO_CREAR,
            detalle={
                "id": str(dictado.id),
                "materia_id": str(dictado.materia_id),
                "carrera_id": str(dictado.carrera_id),
                "cohorte_id": str(dictado.cohorte_id),
            },
            filas_afectadas=1,
            request=request,
        )
        return dictado

    async def update(
        self,
        dictado_id: uuid.UUID,
        data: DictadoUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Dictado:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if "estado" in update_data:
            update_data["estado"] = update_data["estado"].value

        dictado = await self._repo.update(dictado_id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.DICTADO_ACTUALIZAR,
            detalle={"id": str(dictado.id), "cambios": update_data},
            filas_afectadas=1,
            request=request,
        )
        return dictado

    async def soft_delete(
        self,
        dictado_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Dictado:
        dictado = await self._repo.soft_delete(dictado_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.DICTADO_ELIMINAR,
            detalle={"id": str(dictado.id)},
            filas_afectadas=1,
            request=request,
        )
        return dictado
