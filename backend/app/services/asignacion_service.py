import datetime
import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException
from app.models.asignacion import Asignacion
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.asignacion import AsignacionCreate, AsignacionUpdate, EstadoVigencia
from app.schemas.auth import CurrentUser
from app.services.audit.audit_logger import AuditLogger

# Context fields validated against the caller's tenant (D5, regla dura #9).
_CONTEXT_FIELDS = ("dictado_id", "materia_id", "carrera_id", "cohorte_id")


class AsignacionService:
    """Reglas de negocio del CRUD de `Asignacion` (E5, D3/D5).

    Flujo Routers -> Services -> Repositories -> Models (regla dura #11).
    `usuario_id`, `responsable_id` y el contexto académico
    (`dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`) se validan contra
    el tenant del caller -- una referencia a otro tenant es indistinguible
    de "no existe" (regla dura #9). `estado_vigencia` es derivado por
    fechas, nunca almacenado (D3).
    """

    def __init__(
        self,
        asignacion_repo: AsignacionRepository,
        usuario_repo: UsuarioRepository,
        dictado_repo: DictadoRepository,
        materia_repo: MateriaRepository,
        carrera_repo: CarreraRepository,
        cohorte_repo: CohorteRepository,
        audit_repo: AuditLogRepository,
    ):
        self._repo = asignacion_repo
        self._usuario_repo = usuario_repo
        self._context_repos = {
            "dictado_id": (dictado_repo, "Dictado"),
            "materia_id": (materia_repo, "Materia"),
            "carrera_id": (carrera_repo, "Carrera"),
            "cohorte_id": (cohorte_repo, "Cohorte"),
        }
        self._audit = AuditLogger(repository=audit_repo)

    async def _validate_usuario(self, usuario_id: uuid.UUID) -> None:
        usuario = await self._usuario_repo.find_by_id(usuario_id)
        if usuario is None:
            raise NotFoundException(resource="Usuario", id=usuario_id)

    async def _validate_responsable(self, responsable_id: uuid.UUID | None) -> None:
        if responsable_id is None:
            return
        responsable = await self._usuario_repo.find_by_id(responsable_id)
        if responsable is None:
            raise NotFoundException(resource="Usuario", id=responsable_id)

    async def _validate_context(self, data: dict) -> None:
        for field, (repo, resource_name) in self._context_repos.items():
            value = data.get(field)
            if value is None:
                continue
            entity = await repo.find_by_id(value)
            if entity is None:
                raise NotFoundException(resource=resource_name, id=value)

    async def create(
        self,
        data: AsignacionCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Asignacion:
        create_data = data.model_dump()
        create_data["rol"] = create_data["rol"].value if hasattr(create_data["rol"], "value") else create_data["rol"]

        await self._validate_usuario(create_data["usuario_id"])
        await self._validate_responsable(create_data.get("responsable_id"))
        await self._validate_context(create_data)

        asignacion = await self._repo.create(create_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ASIGNACION_CREAR,
            detalle={"id": str(asignacion.id), "usuario_id": str(asignacion.usuario_id), "rol": asignacion.rol},
            filas_afectadas=1,
            request=request,
        )
        return asignacion

    async def update(
        self,
        asignacion_id: uuid.UUID,
        data: AsignacionUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Asignacion:
        update_data = data.model_dump(exclude_unset=True)
        if "rol" in update_data and update_data["rol"] is not None:
            update_data["rol"] = update_data["rol"].value

        if "responsable_id" in update_data:
            await self._validate_responsable(update_data["responsable_id"])
        await self._validate_context(update_data)

        asignacion = await self._repo.update(asignacion_id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ASIGNACION_ACTUALIZAR,
            detalle={"id": str(asignacion.id), "cambios": list(update_data.keys())},
            filas_afectadas=1,
            request=request,
        )
        return asignacion

    async def soft_delete(
        self,
        asignacion_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> Asignacion:
        asignacion = await self._repo.soft_delete(asignacion_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ASIGNACION_ELIMINAR,
            detalle={"id": str(asignacion.id)},
            filas_afectadas=1,
            request=request,
        )
        return asignacion


def estado_vigencia_for(asignacion: Asignacion) -> EstadoVigencia:
    """Derive `estado_vigencia` (Vigente|Vencida) from dates (D3).

    Vigente <=> `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`.
    """
    hoy = datetime.date.today()
    if asignacion.desde <= hoy and (asignacion.hasta is None or hoy <= asignacion.hasta):
        return EstadoVigencia.VIGENTE
    return EstadoVigencia.VENCIDA
