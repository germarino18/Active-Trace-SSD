import csv
import io
import uuid

from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException
from app.models.dictado import Dictado
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.guardia_repository import GuardiaRepository
from app.schemas.auth import CurrentUser
from app.schemas.guardias import GuardiaCreate, GuardiaRead, GuardiaUpdate
from app.services.audit.audit_logger import AuditLogger


class GuardiasService:
    def __init__(
        self,
        guardia_repo: GuardiaRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._repo = guardia_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> "GuardiasService":
        return cls(
            guardia_repo=GuardiaRepository(session=session, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def registrar(
        self,
        data: GuardiaCreate,
        *,
        current_user: CurrentUser,
        request,
    ) -> GuardiaRead:
        """Register a new guardia."""
        guardia = await self._repo.create(data.model_dump())

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.GUARDIA_REGISTRAR,
            detalle={
                "guardia_id": str(guardia.id),
                "dictado_id": str(data.dictado_id),
                "asignacion_id": str(data.asignacion_id),
            },
            filas_afectadas=1,
            request=request,
        )

        return GuardiaRead.model_validate(guardia)

    async def editar(
        self,
        guardia_id: uuid.UUID,
        data: GuardiaUpdate,
        *,
        current_user: CurrentUser,
        request,
    ) -> GuardiaRead:
        """Edit a guardia (estado, comentarios)."""
        guardia = await self._repo.find_by_id(guardia_id)
        if guardia is None:
            raise NotFoundException(resource="Guardia", id=guardia_id)

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return GuardiaRead.model_validate(guardia)

        updated = await self._repo.update(guardia_id, update_data)
        return GuardiaRead.model_validate(updated)

    async def listar(
        self,
        *,
        asignacion_id: uuid.UUID | None = None,
        dictado_id: uuid.UUID | None = None,
        estado: str | None = None,
        dia: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[GuardiaRead]:
        """List guardias with optional filters."""
        guardias = await self._repo.list_by_tenant(
            dictado_id=dictado_id,
            asignacion_id=asignacion_id,
            estado=estado,
            dia=dia,
            skip=skip,
            limit=limit,
        )
        return [GuardiaRead.model_validate(g) for g in guardias]

    async def obtener(self, guardia_id: uuid.UUID) -> GuardiaRead:
        """Get a single guardia by ID."""
        guardia = await self._repo.find_by_id(guardia_id)
        if guardia is None:
            raise NotFoundException(resource="Guardia", id=guardia_id)
        return GuardiaRead.model_validate(guardia)

    async def exportar_csv(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> StreamingResponse:
        """Export guardias to CSV (D6, F6.6)."""
        guardias = await self._repo.list_for_export(
            dictado_id=dictado_id,
            asignacion_id=asignacion_id,
            estado=estado,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Día", "Horario", "Materia", "Docente", "Estado", "Comentarios"])

        for g in guardias:
            materia_nombre = await self._resolver_nombre_materia(g.dictado_id)
            docente_nombre = await self._resolver_nombre_docente(g.asignacion_id)
            writer.writerow([
                g.dia,
                g.horario,
                materia_nombre,
                docente_nombre,
                g.estado,
                g.comentarios or "",
            ])

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=guardias.csv"
            },
        )

    async def _resolver_nombre_materia(self, dictado_id: uuid.UUID) -> str:
        """Resolve materia name from dictado_id via JOIN."""
        from app.models.materia import Materia

        query = (
            select(Materia.nombre)
            .select_from(Dictado)
            .join(Materia, Dictado.materia_id == Materia.id)
            .where(Dictado.id == dictado_id)
        )
        result = await self._session.execute(query)
        row = result.scalar_one_or_none()
        return row or "—"

    async def _resolver_nombre_docente(self, asignacion_id: uuid.UUID) -> str:
        """Resolve docente name from asignacion_id via JOIN."""
        from app.models.asignacion import Asignacion

        query = (
            select(Usuario.nombre, Usuario.apellidos)
            .select_from(Asignacion)
            .join(Usuario, Asignacion.usuario_id == Usuario.id)
            .where(Asignacion.id == asignacion_id)
        )
        result = await self._session.execute(query)
        row = result.one_or_none()
        if row:
            return f"{row[0]} {row[1]}".strip()
        return "—"
