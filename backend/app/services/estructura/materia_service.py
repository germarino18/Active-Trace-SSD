import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException, ValidationException
from app.models.materia import Materia
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.materia_repository import MateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.estructura import MateriaCreate, MateriaUpdate
from app.services.audit.audit_logger import AuditLogger


class MateriaService:
    """Reglas de negocio de Materia (E3, ADR-006).

    Catálogo único del tenant: unicidad `(tenant_id, codigo)` entre
    materias vivas (D4). Mutaciones se auditan vía `AuditLogger`.
    """

    def __init__(self, materia_repo: MateriaRepository, audit_repo: AuditLogRepository):
        self._repo = materia_repo
        self._audit = AuditLogger(repository=audit_repo)

    async def create(
        self,
        data: MateriaCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Materia:
        if data.codigo:
            existing = await self._repo.find_by_codigo(current_user.tenant_id, data.codigo)
            if existing is not None:
                raise ValidationException(
                    message=f"Ya existe una materia con el código '{data.codigo}'",
                    details={"codigo": data.codigo},
                )

        materia = await self._repo.create(
            {
                "codigo": data.codigo,
                "nombre": data.nombre,
                "estado": "Activa",
                "carrera_id": data.carrera_id,
                "cohorte_id": data.cohorte_id,
            }
        )

        # Re-fetch with relationships eagerly loaded for the response
        materia = await self._repo.get_with_relations(materia.id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.MATERIA_CREAR,
            detalle={"id": str(materia.id), "codigo": materia.codigo},
            filas_afectadas=1,
            request=request,
        )
        return materia

    async def update(
        self,
        materia_id: uuid.UUID,
        data: MateriaUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Materia:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        # estado is already serialized as string with mode='json'

        if "codigo" in update_data:
            existing = await self._repo.find_by_codigo(current_user.tenant_id, update_data["codigo"])
            if existing is not None and existing.id != materia_id:
                raise ValidationException(
                    message=f"Ya existe una materia con el código '{update_data['codigo']}'",
                    details={"codigo": update_data["codigo"]},
                )

        materia = await self._repo.update(materia_id, update_data)

        # Re-fetch with relationships eagerly loaded for the response
        materia = await self._repo.get_with_relations(materia.id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.MATERIA_ACTUALIZAR,
            detalle={"id": str(materia.id), "cambios": update_data},
            filas_afectadas=1,
            request=request,
        )
        return materia

    async def soft_delete(
        self,
        materia_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Materia:
        materia = await self._repo.soft_delete(materia_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.MATERIA_ELIMINAR,
            detalle={"id": str(materia.id)},
            filas_afectadas=1,
            request=request,
        )
        return materia

    async def toggle_estado(
        self,
        materia_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Materia:
        materia = await self._repo.find_by_id(materia_id)
        if materia is None:
            raise NotFoundException(resource="Materia", id=materia_id)

        nuevo_estado = "Inactiva" if materia.estado == "Activa" else "Activa"
        materia = await self._repo.update(materia_id, {"estado": nuevo_estado})
        materia = await self._repo.get_with_relations(materia.id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.MATERIA_CAMBIAR_ESTADO,
            detalle={
                "id": str(materia.id),
                "estado_anterior": materia.estado,
                "estado_nuevo": nuevo_estado,
            },
            filas_afectadas=1,
            request=request,
        )
        return materia
