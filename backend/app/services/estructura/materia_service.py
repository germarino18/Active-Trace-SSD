import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
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
            }
        )

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
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if "estado" in update_data:
            update_data["estado"] = update_data["estado"].value

        if "codigo" in update_data:
            existing = await self._repo.find_by_codigo(current_user.tenant_id, update_data["codigo"])
            if existing is not None and existing.id != materia_id:
                raise ValidationException(
                    message=f"Ya existe una materia con el código '{update_data['codigo']}'",
                    details={"codigo": update_data["codigo"]},
                )

        materia = await self._repo.update(materia_id, update_data)

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
