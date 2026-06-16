import uuid
from datetime import date, timedelta
from string import Template

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.encuentro_repository import (
    InstanciaEncuentroRepository,
    SlotEncuentroRepository,
)
from app.schemas.auth import CurrentUser
from app.schemas.encuentros import (
    BloqueHTMLResponse,
    InstanciaEncuentroCreate,
    InstanciaEncuentroRead,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
    SlotEncuentroRead,
    SlotEncuentroUpdate,
)
from app.services.audit.audit_logger import AuditLogger

_MAX_SEMANAS = 52
_TRANSICIONES_VALIDAS: dict[str, list[str]] = {
    "Programado": ["Realizado", "Cancelado"],
    "Realizado": [],
    "Cancelado": [],
}

_BLOQUE_HTML_TEMPLATE = Template("""<table class="encuentros">
<thead>
<tr>
<th>Fecha</th><th>Hora</th><th>Título</th><th>Enlace</th><th>Grabación</th>
</tr>
</thead>
<tbody>
$filas
</tbody>
</table>""")

_FILA_HTML_TEMPLATE = Template(
    "<tr><td>$fecha</td><td>$hora</td><td>$titulo</td>"
    "<td>$meet_link</td><td>$video_link</td></tr>"
)


class EncuentrosService:
    def __init__(
        self,
        slot_repo: SlotEncuentroRepository,
        instancia_repo: InstanciaEncuentroRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._slot_repo = slot_repo
        self._instancia_repo = instancia_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> "EncuentrosService":
        return cls(
            slot_repo=SlotEncuentroRepository(session=session, tenant_id=tenant_id),
            instancia_repo=InstanciaEncuentroRepository(
                session=session, tenant_id=tenant_id
            ),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def crear_slot(
        self,
        data: SlotEncuentroCreate,
        *,
        current_user: CurrentUser,
        request,
    ) -> SlotEncuentroRead:
        """Create a recurrent slot and generate all instances upfront (D1)."""
        if data.cant_semanas > _MAX_SEMANAS:
            raise ValidationException(
                message=f"cant_semanas no puede superar {_MAX_SEMANAS}",
                details={"max": _MAX_SEMANAS, "received": data.cant_semanas},
            )
        if data.cant_semanas == 0 and data.fecha_unica is None:
            raise ValidationException(
                message="Si cant_semanas es 0, fecha_unica es obligatoria",
                details={"cant_semanas": 0, "fecha_unica": None},
            )

        # Create the slot
        slot = await self._slot_repo.create(data.model_dump())

        # Generate instances upfront
        instancias_data = self._generar_instancias(slot, data)
        if instancias_data:
            await self._instancia_repo.bulk_create(instancias_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ENCUENTRO_CREAR,
            detalle={
                "slot_id": str(slot.id),
                "dictado_id": str(data.dictado_id),
                "cant_semanas": data.cant_semanas,
                "instancias_generadas": len(instancias_data),
            },
            filas_afectadas=len(instancias_data),
            request=request,
        )

        return SlotEncuentroRead.model_validate(slot)

    def _generar_instancias(
        self, slot: SlotEncuentro, data: SlotEncuentroCreate
    ) -> list[dict]:
        """Generate instance data from a slot config (upfront generation, D1)."""
        instancias: list[dict] = []

        if data.cant_semanas > 0:
            for i in range(data.cant_semanas):
                instancia_fecha = data.fecha_inicio + timedelta(weeks=i)
                instancias.append(
                    {
                        "slot_id": slot.id,
                        "dictado_id": data.dictado_id,
                        "asignacion_id": data.asignacion_id,
                        "fecha": instancia_fecha,
                        "hora": data.hora,
                        "titulo": data.titulo,
                        "estado": "Programado",
                        "meet_url": data.meet_url,
                        "tenant_id": slot.tenant_id,
                    }
                )
        elif data.fecha_unica is not None:
            instancias.append(
                {
                    "slot_id": slot.id,
                    "dictado_id": data.dictado_id,
                    "asignacion_id": data.asignacion_id,
                    "fecha": data.fecha_unica,
                    "hora": data.hora,
                    "titulo": data.titulo,
                    "estado": "Programado",
                    "meet_url": data.meet_url,
                    "tenant_id": slot.tenant_id,
                }
            )

        return instancias

    async def editar_instancia(
        self,
        instancia_id: uuid.UUID,
        data: InstanciaEncuentroUpdate,
        *,
        current_user: CurrentUser,
        request,
    ) -> InstanciaEncuentroRead:
        """Edit an encounter instance with state transition validation."""
        instancia = await self._instancia_repo.find_by_id(instancia_id)
        if instancia is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(
                resource="InstanciaEncuentro", id=instancia_id
            )

        update_data: dict = {}

        if data.estado is not None:
            self._validar_transicion(instancia.estado, data.estado)
            update_data["estado"] = data.estado

        if data.meet_url is not None:
            update_data["meet_url"] = data.meet_url
        if data.video_url is not None:
            update_data["video_url"] = data.video_url
        if data.comentario is not None:
            update_data["comentario"] = data.comentario

        if not update_data:
            return InstanciaEncuentroRead.model_validate(instancia)

        updated = await self._instancia_repo.update(instancia_id, update_data)

        accion = AccionAuditoria.ENCUENTRO_EDITAR
        if data.estado == "Cancelado":
            accion = AccionAuditoria.ENCUENTRO_CANCELAR

        await self._audit.log(
            current_user=current_user,
            accion=accion,
            detalle={
                "instancia_id": str(instancia_id),
                "slot_id": str(instancia.slot_id) if instancia.slot_id else None,
                "cambios": update_data,
            },
            filas_afectadas=1,
            request=request,
        )

        return InstanciaEncuentroRead.model_validate(updated)

    def _validar_transicion(self, estado_actual: str, estado_nuevo: str) -> None:
        """Validate encounter instance state transitions (D1 design)."""
        permitidos = _TRANSICIONES_VALIDAS.get(estado_actual, [])
        if estado_nuevo not in permitidos:
            raise ValidationException(
                message=f"Transición inválida: {estado_actual} → {estado_nuevo}",
                details={
                    "estado_actual": estado_actual,
                    "estado_nuevo": estado_nuevo,
                    "transiciones_permitidas": permitidos,
                },
            )

    async def listar_instancias(
        self,
        *,
        dictado_id: uuid.UUID | None = None,
        estado: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InstanciaEncuentroRead]:
        """List instances with optional filters (scoped by tenant)."""
        instancias = await self._instancia_repo.list_by_tenant(
            dictado_id=dictado_id,
            estado=estado,
            skip=skip,
            limit=limit,
        )
        return [InstanciaEncuentroRead.model_validate(i) for i in instancias]

    async def obtener_instancia(
        self, instancia_id: uuid.UUID
    ) -> InstanciaEncuentroRead:
        """Get a single instance by ID."""
        instancia = await self._instancia_repo.find_by_id(instancia_id)
        if instancia is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(
                resource="InstanciaEncuentro", id=instancia_id
            )
        return InstanciaEncuentroRead.model_validate(instancia)

    async def obtener_slot(
        self, slot_id: uuid.UUID
    ) -> SlotEncuentroRead:
        """Get a single slot by ID."""
        slot = await self._slot_repo.find_by_id(slot_id)
        if slot is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(resource="SlotEncuentro", id=slot_id)
        return SlotEncuentroRead.model_validate(slot)

    async def actualizar_slot(
        self,
        slot_id: uuid.UUID,
        data: SlotEncuentroUpdate,
    ) -> SlotEncuentroRead:
        """Update a slot (only metadata, not instance generation)."""
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            slot = await self._slot_repo.find_by_id(slot_id)
            if slot is None:
                from app.core.exceptions import NotFoundException
                raise NotFoundException(resource="SlotEncuentro", id=slot_id)
            return SlotEncuentroRead.model_validate(slot)
        updated = await self._slot_repo.update(slot_id, update_data)
        return SlotEncuentroRead.model_validate(updated)

    async def eliminar_slot(
        self, slot_id: uuid.UUID
    ) -> None:
        """Soft delete a slot."""
        await self._slot_repo.soft_delete(slot_id)

    async def generar_bloque_html(
        self, dictado_id: uuid.UUID
    ) -> BloqueHTMLResponse:
        """Generate HTML block for LMS (D5, F6.4)."""
        instancias = await self._instancia_repo.list_by_dictado(dictado_id)
        instancias_activas = [
            i for i in instancias if i.estado in ("Programado", "Realizado")
        ]
        instancias_ordenadas = sorted(instancias_activas, key=lambda i: i.fecha)

        filas_html = []
        for inst in instancias_ordenadas:
            meet = (
                f'<a href="{inst.meet_url}">Enlace</a>'
                if inst.meet_url else "—"
            )
            video = (
                f'<a href="{inst.video_url}">Grabación</a>'
                if inst.video_url else "—"
            )
            filas_html.append(
                _FILA_HTML_TEMPLATE.safe_substitute(
                    fecha=inst.fecha.isoformat(),
                    hora=inst.hora.strftime("%H:%M"),
                    titulo=inst.titulo,
                    meet_link=meet,
                    video_link=video,
                )
            )

        html = _BLOQUE_HTML_TEMPLATE.safe_substitute(
            filas="\n".join(filas_html)
        ) if filas_html else "<p>No hay encuentros programados.</p>"

        return BloqueHTMLResponse(
            html=html,
            dictado_id=dictado_id,
            total_encuentros=len(instancias_ordenadas),
        )
