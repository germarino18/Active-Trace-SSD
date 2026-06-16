import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.repositories.alumno_convocado_repository import AlumnoConvocadoRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.resultado_evaluacion_repository import (
    ResultadoEvaluacionRepository,
)
from app.schemas.auth import CurrentUser
from app.schemas.coloquios import (
    ResultadoEvaluacionCreate,
    ResultadoEvaluacionRead,
)
from app.services.audit.audit_logger import AuditLogger


class ResultadoService:
    """Service for coloquio result management (registrar, consultar)."""

    def __init__(
        self,
        evaluacion_repo: EvaluacionRepository,
        resultado_repo: ResultadoEvaluacionRepository,
        alumno_convocado_repo: AlumnoConvocadoRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._evaluacion_repo = evaluacion_repo
        self._resultado_repo = resultado_repo
        self._alumno_convocado_repo = alumno_convocado_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> "ResultadoService":
        return cls(
            evaluacion_repo=EvaluacionRepository(
                session=session, tenant_id=tenant_id
            ),
            resultado_repo=ResultadoEvaluacionRepository(
                session=session, tenant_id=tenant_id
            ),
            alumno_convocado_repo=AlumnoConvocadoRepository(
                session=session, tenant_id=tenant_id
            ),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def registrar_resultado(
        self,
        data: ResultadoEvaluacionCreate,
        *,
        current_user: CurrentUser,
        request,
    ) -> ResultadoEvaluacionRead:
        """Register a coloquio result (immutable once created)."""
        evaluacion = await self._evaluacion_repo.find_by_id(data.evaluacion_id)
        if evaluacion is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(
                resource="Evaluacion", id=data.evaluacion_id
            )

        # Verify alumno is convocado
        convocado = await self._alumno_convocado_repo.exists(
            evaluacion_id=data.evaluacion_id,
            alumno_id=data.alumno_id,
        )
        if not convocado:
            raise ValidationException(
                message="El alumno no está convocado a esta evaluación",
                details={
                    "evaluacion_id": str(data.evaluacion_id),
                    "alumno_id": str(data.alumno_id),
                },
            )

        # Check unique result
        existing = await self._resultado_repo.get_by_evaluacion_alumno(
            data.evaluacion_id, data.alumno_id
        )
        if existing is not None:
            raise ValidationException(
                message="El alumno ya tiene un resultado registrado en esta evaluación",
                details={
                    "evaluacion_id": str(data.evaluacion_id),
                    "alumno_id": str(data.alumno_id),
                    "resultado_id": str(existing.id),
                },
            )

        resultado = await self._resultado_repo.create(
            {
                "evaluacion_id": data.evaluacion_id,
                "alumno_id": data.alumno_id,
                "nota_final": data.nota_final,
            }
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COLOQUIO_REGISTRAR_RESULTADO,
            detalle={
                "evaluacion_id": str(data.evaluacion_id),
                "alumno_id": str(data.alumno_id),
                "resultado_id": str(resultado.id),
                "nota_final": data.nota_final,
            },
            filas_afectadas=1,
            request=request,
        )

        return ResultadoEvaluacionRead.model_validate(resultado)
