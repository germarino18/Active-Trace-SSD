import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ForbiddenException, ValidationException
from app.models.evaluacion import Evaluacion
from app.models.usuario import Usuario
from app.repositories.alumno_convocado_repository import AlumnoConvocadoRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.reserva_evaluacion_repository import (
    ReservaEvaluacionRepository,
)
from app.schemas.auth import CurrentUser
from app.schemas.coloquios import (
    AgendaReservaRead,
    ReservaEvaluacionRead,
)
from app.services.audit.audit_logger import AuditLogger


class ReservaService:
    """Service for reservation management (reservar, cancelar, listar agenda)."""

    def __init__(
        self,
        evaluacion_repo: EvaluacionRepository,
        reserva_repo: ReservaEvaluacionRepository,
        alumno_convocado_repo: AlumnoConvocadoRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._evaluacion_repo = evaluacion_repo
        self._reserva_repo = reserva_repo
        self._alumno_convocado_repo = alumno_convocado_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> "ReservaService":
        return cls(
            evaluacion_repo=EvaluacionRepository(
                session=session, tenant_id=tenant_id
            ),
            reserva_repo=ReservaEvaluacionRepository(
                session=session, tenant_id=tenant_id
            ),
            alumno_convocado_repo=AlumnoConvocadoRepository(
                session=session, tenant_id=tenant_id
            ),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def reservar(
        self,
        evaluacion_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request,
    ) -> ReservaEvaluacionRead:
        """Reserve a turno in a convocatoria (with cupo control)."""
        evaluacion = await self._evaluacion_repo.find_by_id(evaluacion_id)
        if evaluacion is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(
                resource="Evaluacion", id=evaluacion_id
            )

        if evaluacion.estado != "Activa":
            raise ValidationException(
                message="La convocatoria no está activa",
                details={
                    "evaluacion_id": str(evaluacion_id),
                    "estado": evaluacion.estado,
                },
            )

        # Verificar que el alumno esté convocado
        usuario_row = (
            await self._session.execute(
                select(Usuario.id).where(Usuario.user_id == current_user.user_id)
            )
        ).scalar_one_or_none()
        if usuario_row is None:
            raise ForbiddenException(
                action="El perfil de usuario no existe"
            )
        alumno_id = usuario_row
        convocado = await self._alumno_convocado_repo.exists(
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
        )
        if not convocado:
            raise ForbiddenException(
                action="El alumno no está habilitado para esta convocatoria"
            )

        # Verificar cupo con FOR UPDATE
        # Lock the evaluacion row to prevent race conditions
        lock_query = (
            select(Evaluacion)
            .where(Evaluacion.id == evaluacion_id)
            .with_for_update()
        )
        await self._session.execute(lock_query)

        activas = await self._reserva_repo.count_activas_by_evaluacion(
            evaluacion_id
        )
        if activas >= evaluacion.cupo_maximo:
            raise ValidationException(
                message="Cupo agotado",
                details={
                    "evaluacion_id": str(evaluacion_id),
                    "cupo_maximo": evaluacion.cupo_maximo,
                    "reservas_activas": activas,
                },
            )

        # Verificar que no tenga ya una reserva activa
        existing = await self._reserva_repo.find_by(
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
        )
        if any(r.estado == "Activa" for r in existing):
            raise ValidationException(
                message="Ya tienes una reserva activa en esta convocatoria",
                details={"evaluacion_id": str(evaluacion_id)},
            )

        reserva = await self._reserva_repo.create(
            {
                "evaluacion_id": evaluacion_id,
                "alumno_id": alumno_id,
                "estado": "Activa",
            }
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COLOQUIO_RESERVAR,
            detalle={
                "evaluacion_id": str(evaluacion_id),
                "alumno_id": str(alumno_id),
                "reserva_id": str(reserva.id),
            },
            filas_afectadas=1,
            request=request,
        )

        return ReservaEvaluacionRead.model_validate(reserva)

    async def cancelar_reserva(
        self,
        reserva_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request,
    ) -> ReservaEvaluacionRead:
        """Cancel a reservation (only by owner or coloquios:gestionar)."""
        reserva = await self._reserva_repo.find_by_id(reserva_id)
        if reserva is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(
                resource="ReservaEvaluacion", id=reserva_id
            )

        evaluacion = await self._evaluacion_repo.find_by_id(
            reserva.evaluacion_id
        )
        if evaluacion is not None and evaluacion.estado == "Cerrada":
            raise ValidationException(
                message="No se puede cancelar una reserva en una convocatoria cerrada",
                details={"evaluacion_id": str(reserva.evaluacion_id)},
            )

        # Only the owner or a user with gestionar permission can cancel
        usuario_row = (
            await self._session.execute(
                select(Usuario.id).where(Usuario.user_id == current_user.user_id)
            )
        ).scalar_one_or_none()
        usuario_id = usuario_row
        is_owner = reserva.alumno_id == usuario_id
        has_gestionar = any(
            perm in (current_user.roles or [])
            for perm in ["COORDINADOR", "ADMIN"]
        )

        if not is_owner and not has_gestionar:
            raise ForbiddenException(action="No puedes cancelar esta reserva")

        if reserva.estado != "Activa":
            return ReservaEvaluacionRead.model_validate(reserva)  # idempotent

        updated = await self._reserva_repo.cancelar(reserva_id)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COLOQUIO_CANCELAR_RESERVA,
            detalle={
                "reserva_id": str(reserva_id),
                "evaluacion_id": str(reserva.evaluacion_id),
                "alumno_id": str(reserva.alumno_id),
            },
            filas_afectadas=1,
            request=request,
        )

        return ReservaEvaluacionRead.model_validate(updated)

    async def listar_agenda(
        self,
        *,
        evaluacion_id: uuid.UUID | None = None,
        alumno_id: uuid.UUID | None = None,
        dictado_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AgendaReservaRead]:
        """List active reservations for agenda view."""
        from sqlalchemy import select as sql_select
        from app.models.evaluacion import Evaluacion as EvalModel
        from app.models.dictado import Dictado
        from app.models.materia import Materia
        from app.models.usuario import Usuario
        from app.models.reserva_evaluacion import ReservaEvaluacion as ResModel

        query = (
            sql_select(
                ResModel.id,
                ResModel.evaluacion_id,
                ResModel.alumno_id,
                Usuario.nombre,
                Usuario.apellidos,
                Usuario.legajo,
                EvalModel.instancia,
                EvalModel.dictado_id,
                Materia.nombre,
                ResModel.fecha_hora,
                ResModel.estado,
            )
            .select_from(ResModel)
            .join(EvalModel, ResModel.evaluacion_id == EvalModel.id)
            .join(Dictado, EvalModel.dictado_id == Dictado.id)
            .join(Materia, Dictado.materia_id == Materia.id)
            .join(Usuario, ResModel.alumno_id == Usuario.id)
            .where(ResModel.estado == "Activa")
        )

        tenant_id = self._reserva_repo._get_effective_tenant_id()
        if tenant_id is not None:
            query = query.where(EvalModel.tenant_id == tenant_id)

        filters = []
        if evaluacion_id is not None:
            filters.append(ResModel.evaluacion_id == evaluacion_id)
        if alumno_id is not None:
            filters.append(ResModel.alumno_id == alumno_id)
        if dictado_id is not None:
            filters.append(EvalModel.dictado_id == dictado_id)

        for f in filters:
            query = query.where(f)

        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)
        rows = result.all()

        return [
            AgendaReservaRead(
                id=row.id,
                evaluacion_id=row.evaluacion_id,
                alumno_id=row.alumno_id,
                alumno_nombre=f"{row.nombre} {row.apellidos}",
                alumno_legajo=row.legajo,
                evaluacion_instancia=row.instancia,
                dictado_id=row.dictado_id,
                materia_nombre=row.materia_nombre,
                fecha_hora=row.fecha_hora,
                estado=row.estado,
            )
            for row in rows
        ]
