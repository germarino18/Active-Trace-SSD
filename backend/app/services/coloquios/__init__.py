"""Coloquios service module.

Servicios para la gestión de convocatorias de coloquio, reservas y resultados.
Sigue el mismo patrón que encuentros (C-13): factory method `create(cls, session, tenant_id)`.
"""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.evaluacion import Evaluacion
from app.repositories.alumno_convocado_repository import AlumnoConvocadoRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.reserva_evaluacion_repository import (
    ReservaEvaluacionRepository,
)
from app.repositories.resultado_evaluacion_repository import (
    ResultadoEvaluacionRepository,
)
from app.schemas.auth import CurrentUser
from app.schemas.coloquios import (
    AlumnoConvocadoRead,
    ConvocatoriaColoquioRead,
    EvaluacionCreate,
    EvaluacionRead,
    EvaluacionUpdate,
    FechaConCupoRead,
    MetricasColoquiosRead,
    RegistroAcademicoRead,
)
from app.services.audit.audit_logger import AuditLogger


class ColoquioService:
    """Service for managing evaluacion convocatorias (ABM, import, metricas)."""

    def __init__(
        self,
        evaluacion_repo: EvaluacionRepository,
        alumno_convocado_repo: AlumnoConvocadoRepository,
        resultado_repo: ResultadoEvaluacionRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._evaluacion_repo = evaluacion_repo
        self._alumno_convocado_repo = alumno_convocado_repo
        self._resultado_repo = resultado_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> "ColoquioService":
        return cls(
            evaluacion_repo=EvaluacionRepository(
                session=session, tenant_id=tenant_id
            ),
            alumno_convocado_repo=AlumnoConvocadoRepository(
                session=session, tenant_id=tenant_id
            ),
            resultado_repo=ResultadoEvaluacionRepository(
                session=session, tenant_id=tenant_id
            ),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def crear_evaluacion(
        self,
        data: EvaluacionCreate,
        *,
        current_user: CurrentUser,
        request,
    ) -> EvaluacionRead:
        """Create a new evaluacion convocatoria."""
        evaluacion = await self._evaluacion_repo.create(data.model_dump())

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COLOQUIO_CREAR,
            detalle={
                "evaluacion_id": str(evaluacion.id),
                "dictado_id": str(data.dictado_id),
                "tipo": data.tipo,
                "instancia": data.instancia,
                "cupo_maximo": data.cupo_maximo,
            },
            filas_afectadas=1,
            request=request,
        )

        return EvaluacionRead.model_validate(evaluacion)

    async def actualizar_evaluacion(
        self,
        evaluacion_id: uuid.UUID,
        data: EvaluacionUpdate,
        *,
        current_user: CurrentUser,
        request,
    ) -> EvaluacionRead:
        """Update a evaluacion (only if Activa)."""
        evaluacion = await self._evaluacion_repo.find_by_id(evaluacion_id)
        if evaluacion is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(resource="Evaluacion", id=evaluacion_id)

        if evaluacion.estado != "Activa":
            raise ValidationException(
                message="Solo se puede editar una convocatoria activa",
                details={"evaluacion_id": str(evaluacion_id), "estado": evaluacion.estado},
            )

        update_data = data.model_dump(exclude_none=True)

        # Validate that new cupo >= current active reservations
        if "cupo_maximo" in update_data:
            from app.repositories.reserva_evaluacion_repository import (
                ReservaEvaluacionRepository,
            )

            reserva_repo = ReservaEvaluacionRepository(
                session=self._session, tenant_id=evaluacion.tenant_id
            )
            activas = await reserva_repo.count_activas_by_evaluacion(evaluacion_id)
            if update_data["cupo_maximo"] < activas:
                raise ValidationException(
                    message="El nuevo cupo no puede ser menor a las reservas activas",
                    details={
                        "cupo_maximo": update_data["cupo_maximo"],
                        "reservas_activas": activas,
                    },
                )

        if not update_data:
            return EvaluacionRead.model_validate(evaluacion)

        updated = await self._evaluacion_repo.update(evaluacion_id, update_data)
        return EvaluacionRead.model_validate(updated)

    async def cerrar_evaluacion(
        self,
        evaluacion_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request,
    ) -> EvaluacionRead:
        """Close a convocatoria (estado -> Cerrada)."""
        evaluacion = await self._evaluacion_repo.find_by_id(evaluacion_id)
        if evaluacion is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(resource="Evaluacion", id=evaluacion_id)

        if evaluacion.estado == "Cerrada":
            return EvaluacionRead.model_validate(evaluacion)  # idempotent

        updated = await self._evaluacion_repo.update(
            evaluacion_id, {"estado": "Cerrada"}
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COLOQUIO_CERRAR,
            detalle={
                "evaluacion_id": str(evaluacion_id),
                "dictado_id": str(evaluacion.dictado_id),
            },
            filas_afectadas=1,
            request=request,
        )

        return EvaluacionRead.model_validate(updated)

    async def importar_alumnos(
        self,
        evaluacion_id: uuid.UUID,
        alumno_ids: list[uuid.UUID],
        *,
        current_user: CurrentUser,
        request,
    ) -> int:
        """Import alumnos to a convocatoria (idempotent)."""
        evaluacion = await self._evaluacion_repo.find_by_id(evaluacion_id)
        if evaluacion is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(resource="Evaluacion", id=evaluacion_id)

        if evaluacion.estado != "Activa":
            raise ValidationException(
                message="Solo se pueden importar alumnos a una convocatoria activa",
                details={"evaluacion_id": str(evaluacion_id), "estado": evaluacion.estado},
            )

        count = await self._alumno_convocado_repo.bulk_import(
            evaluacion_id=evaluacion_id,
            alumno_ids=alumno_ids,
            tenant_id=evaluacion.tenant_id,
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.COLOQUIO_IMPORTAR_ALUMNOS,
            detalle={
                "evaluacion_id": str(evaluacion_id),
                "alumnos_solicitados": len(alumno_ids),
                "alumnos_nuevos": count,
            },
            filas_afectadas=count,
            request=request,
        )

        return count

    async def listar_evaluaciones(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        estado: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EvaluacionRead]:
        """List evaluaciones with optional filters."""
        evaluaciones = await self._evaluacion_repo.list_by_tenant(
            dictado_id=dictado_id,
            estado=estado,
            skip=skip,
            limit=limit,
        )
        return [EvaluacionRead.model_validate(e) for e in evaluaciones]

    async def listar_convocatorias_alumno(
        self, alumno_id: uuid.UUID
    ) -> list[ConvocatoriaColoquioRead]:
        """List active convocatorias for an ALUMNO, shaped for self-service UI.

        Returns convocatorias where the alumno is convocado + evaluacion Activa,
        with materia_nombre, computed fecha_limite, and a single virtual slot
        with remaining capacity.
        """
        from datetime import timedelta, timezone

        from sqlalchemy import func as sa_func, select

        from app.models.alumno_convocado import AlumnoConvocado
        from app.models.dictado import Dictado
        from app.models.materia import Materia
        from app.models.reserva_evaluacion import ReservaEvaluacion
        from app.models.usuario import Usuario

        # Resolve user_id (auth) → usuario_id (domain profile)
        usuario_row = (
            await self._session.execute(
                select(Usuario.id).where(Usuario.user_id == alumno_id)
            )
        ).scalar_one_or_none()
        if usuario_row is None:
            return []
        usuario_id = usuario_row

        # Query evaluaciones (Activas) where alumno is convocado
        query = (
            select(
                Evaluacion.id,
                Evaluacion.cupo_maximo,
                Evaluacion.created_at,
                Evaluacion.dias_disponibles,
                Materia.nombre.label("materia_nombre"),
            )
            .select_from(Evaluacion)
            .join(AlumnoConvocado, AlumnoConvocado.evaluacion_id == Evaluacion.id)
            .join(Dictado, Evaluacion.dictado_id == Dictado.id)
            .join(Materia, Dictado.materia_id == Materia.id)
            .where(Evaluacion.estado == "Activa")
            .where(AlumnoConvocado.alumno_id == usuario_id)
        )
        tenant_id = self._evaluacion_repo._get_effective_tenant_id()
        if tenant_id is not None:
            query = query.where(Evaluacion.tenant_id == tenant_id)

        result = await self._session.execute(query)
        rows = result.all()

        if not rows:
            return []

        # Count active reservations per evaluacion (one query)
        evaluacion_ids = [r.id for r in rows]
        reservas_query = (
            select(
                ReservaEvaluacion.evaluacion_id,
                sa_func.count(ReservaEvaluacion.id).label("count"),
            )
            .where(
                ReservaEvaluacion.evaluacion_id.in_(evaluacion_ids),
                ReservaEvaluacion.estado == "Activa",
            )
            .group_by(ReservaEvaluacion.evaluacion_id)
        )
        reservas_result = await self._session.execute(reservas_query)
        reservas_counts = {r.evaluacion_id: r.count for r in reservas_result.all()}

        now = datetime.now(timezone.utc)
        convocatorias: list[ConvocatoriaColoquioRead] = []
        for row in rows:
            cupos_restantes = max(
                0, row.cupo_maximo - reservas_counts.get(row.id, 0)
            )
            fecha_limite = row.created_at + timedelta(days=row.dias_disponibles)

            # Single virtual slot: the evaluacion itself is the "available window"
            slot_date = min(
                row.created_at + timedelta(days=1),
                fecha_limite,
            )

            convocatorias.append(
                ConvocatoriaColoquioRead(
                    id=row.id,
                    materia_nombre=row.materia_nombre,
                    fechas=[
                        FechaConCupoRead(
                            fecha_id=row.id,
                            fecha=slot_date,
                            cupos_restantes=cupos_restantes,
                        )
                    ],
                    fecha_limite=fecha_limite,
                )
            )

        return convocatorias

    async def obtener_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> EvaluacionRead:
        """Get a single evaluacion by ID."""
        evaluacion = await self._evaluacion_repo.find_by_id(evaluacion_id)
        if evaluacion is None:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(resource="Evaluacion", id=evaluacion_id)
        return EvaluacionRead.model_validate(evaluacion)

    async def metricas(
        self,
    ) -> MetricasColoquiosRead:
        """Get panel metrics."""
        metrics = await self._evaluacion_repo.count_metricas()
        return MetricasColoquiosRead(**metrics)

    async def registro_academico(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        evaluacion_id: uuid.UUID | None = None,
        alumno_id: uuid.UUID | None = None,
    ) -> list[RegistroAcademicoRead]:
        """Get consolidated academic record of coloquio results."""
        from sqlalchemy import select
        from app.models.evaluacion import Evaluacion
        from app.models.dictado import Dictado
        from app.models.materia import Materia
        from app.models.usuario import Usuario
        from app.models.reserva_evaluacion import ReservaEvaluacion
        from app.models.resultado_evaluacion import ResultadoEvaluacion

        query = (
            select(
                ResultadoEvaluacion.alumno_id,
                Usuario.nombre.label("alumno_nombre"),
                Usuario.apellidos,
                Usuario.legajo,
                Evaluacion.id.label("evaluacion_id"),
                Evaluacion.instancia,
                Evaluacion.tipo,
                Dictado.id.label("dictado_id"),
                Materia.nombre.label("materia_nombre"),
                ResultadoEvaluacion.nota_final,
                ReservaEvaluacion.fecha_hora,
            )
            .select_from(ResultadoEvaluacion)
            .join(Evaluacion, ResultadoEvaluacion.evaluacion_id == Evaluacion.id)
            .join(Dictado, Evaluacion.dictado_id == Dictado.id)
            .join(Materia, Dictado.materia_id == Materia.id)
            .join(
                Usuario,
                ResultadoEvaluacion.alumno_id == Usuario.id,
            )
            .outerjoin(
                ReservaEvaluacion,
                (ReservaEvaluacion.evaluacion_id == ResultadoEvaluacion.evaluacion_id)
                & (ReservaEvaluacion.alumno_id == ResultadoEvaluacion.alumno_id),
                full=False,
            )
        )

        # Apply tenant scope via evaluacion
        from app.repositories.base import BaseRepository
        # We can't directly reuse evaluacion_repo's scope, so we build manually
        evaluacion_alias = Evaluacion
        tenant_id = self._evaluacion_repo._get_effective_tenant_id()
        if tenant_id is not None:
            query = query.where(Evaluacion.tenant_id == tenant_id)

        filters = []
        if dictado_id is not None:
            filters.append(Evaluacion.dictado_id == dictado_id)
        if evaluacion_id is not None:
            filters.append(Evaluacion.id == evaluacion_id)
        if alumno_id is not None:
            filters.append(ResultadoEvaluacion.alumno_id == alumno_id)

        for f in filters:
            query = query.where(f)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            RegistroAcademicoRead(
                alumno_id=row.alumno_id,
                alumno_nombre=f"{row.alumno_nombre} {row.apellidos}",
                alumno_legajo=row.legajo,
                evaluacion_id=row.evaluacion_id,
                evaluacion_instancia=row.instancia,
                dictado_id=row.dictado_id,
                materia_nombre=row.materia_nombre,
                tipo=row.tipo,
                nota_final=row.nota_final,
                fecha_reserva=row.fecha_hora,
            )
            for row in rows
        ]
