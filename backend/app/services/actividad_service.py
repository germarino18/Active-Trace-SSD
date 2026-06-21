"""ActividadService — gestión de actividades evaluables de un dictado (C-25).

Flujo: Routers → Services → Repositories → Models (regla dura #11).
Identidad y tenant_id SIEMPRE desde la sesión (regla dura #8/#9).
Soft delete siempre (regla dura #13).
"""

import csv
import io
import uuid

from fastapi import HTTPException

from app.core.exceptions import NotFoundException
from app.models.actividad import Actividad
from app.repositories.actividad_repository import ActividadRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.schemas.actividades import ActividadCreate, ActividadUpdate


class ActividadService:
    def __init__(self, session, tenant_id: uuid.UUID):
        self._repo = ActividadRepository(session=session, tenant_id=tenant_id)
        self._session = session
        self._tenant_id = tenant_id
        self._vp_repo = VersionPadronRepository(session=session, tenant_id=tenant_id)
        self._ep_repo = EntradaPadronRepository(session=session, tenant_id=tenant_id)
        self._calif_repo = CalificacionRepository(session=session, tenant_id=tenant_id)

    @classmethod
    def create(cls, session, tenant_id: uuid.UUID) -> "ActividadService":
        return cls(session=session, tenant_id=tenant_id)

    async def crear(
        self,
        dictado_id: uuid.UUID,
        data: ActividadCreate,
    ) -> Actividad:
        """Crea una nueva Actividad en el dictado."""
        return await self._repo.create(
            {
                "dictado_id": dictado_id,
                "nombre": data.nombre,
                "tipo": data.tipo,
                "fecha_limite": data.fecha_limite,
            }
        )

    async def listar(self, dictado_id: uuid.UUID) -> list[Actividad]:
        """Lista todas las Actividades vivas del dictado."""
        return await self._repo.find_by_dictado(dictado_id)

    async def editar(
        self,
        actividad_id: uuid.UUID,
        data: ActividadUpdate,
    ) -> Actividad:
        """Edita campos de una Actividad existente."""
        existing = await self._repo.find_by_id(actividad_id)
        if existing is None:
            raise NotFoundException(resource="Actividad", id=actividad_id)

        update_data: dict = {}
        if data.nombre is not None:
            update_data["nombre"] = data.nombre
        if data.tipo is not None:
            update_data["tipo"] = data.tipo
        if data.fecha_limite is not None:
            update_data["fecha_limite"] = data.fecha_limite
        elif data.model_fields_set and "fecha_limite" in data.model_fields_set:
            # explicitly set to None
            update_data["fecha_limite"] = None

        if not update_data:
            return existing

        return await self._repo.update(actividad_id, update_data)

    async def eliminar(self, actividad_id: uuid.UUID) -> Actividad:
        """Soft-delete de una Actividad."""
        existing = await self._repo.find_by_id(actividad_id)
        if existing is None:
            raise NotFoundException(resource="Actividad", id=actividad_id)
        return await self._repo.soft_delete(actividad_id)

    async def _get_actividad_and_entradas(
        self, actividad_id: uuid.UUID
    ) -> tuple[Actividad, list]:
        """Resolve actividad (tenant-scoped) and the padrón entries of its dictado.

        Raises HTTP 404 if actividad not found in this tenant.
        """
        actividad = await self._repo.find_by_id(actividad_id)
        if actividad is None:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        active_vp = await self._vp_repo.find_active_by_dictado(actividad.dictado_id)
        entradas: list = []
        if active_vp is not None:
            entradas = await self._ep_repo.find_by_version(active_vp.id)

        return actividad, entradas

    async def generar_plantilla_csv(self, actividad_id: uuid.UUID) -> str:
        """Genera una plantilla CSV con los alumnos del padrón activo.

        Columns: entrada_padron_id, usuario_id, nombre, apellido, nota, aprobado.
        Pre-fills nota/aprobado from the alumno's existing Calificacion for this
        actividad (match by entrada_padron_id + actividad_id, fallback by
        actividad nombre). Empty if no calificacion yet.
        """
        from sqlalchemy import select as sa_select
        from app.models.calificacion import Calificacion

        actividad, entradas = await self._get_actividad_and_entradas(actividad_id)

        # Load all calificaciones for this dictado, indexed by entrada_padron_id
        # Prefer match by actividad_id FK; fallback to actividad name match
        q = sa_select(Calificacion).where(
            Calificacion.tenant_id == self._tenant_id,
            Calificacion.dictado_id == actividad.dictado_id,
        )
        result = await self._session.execute(q)
        all_califs = list(result.unique().scalars().all())

        # Build lookup: entrada_padron_id → calificacion (by actividad_id first)
        calif_by_ep: dict[uuid.UUID, Calificacion] = {}
        for c in all_califs:
            if c.actividad_id == actividad_id:
                calif_by_ep[c.entrada_padron_id] = c

        # Fallback: match by nombre if not already matched by actividad_id
        for c in all_califs:
            if c.entrada_padron_id not in calif_by_ep and c.actividad == actividad.nombre:
                calif_by_ep[c.entrada_padron_id] = c

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["entrada_padron_id", "usuario_id", "nombre", "apellido", "nota", "aprobado"]
        )
        for ep in entradas:
            calif = calif_by_ep.get(ep.id)
            nota_val = ""
            aprobado_val = ""
            if calif is not None:
                nota_val = str(float(calif.nota_numerica)) if calif.nota_numerica is not None else (calif.nota_textual or "")
                aprobado_val = "true" if calif.aprobado else "false"
            writer.writerow(
                [
                    str(ep.id),
                    str(ep.usuario_id) if ep.usuario_id else "",
                    ep.nombre or "",
                    ep.apellidos or "",
                    nota_val,
                    aprobado_val,
                ]
            )

        output.seek(0)
        return output.getvalue()

    async def registrar_calificacion(
        self,
        actividad_id: uuid.UUID,
        entrada_padron_id: uuid.UUID,
        nota_numerica: float | None,
        nota_textual: str | None,
        aprobado: bool,
        actor_user_id: uuid.UUID,
    ) -> "Calificacion":
        """Upsert una Calificacion individual para (entrada_padron_id, actividad_id).

        Valida que la entrada pertenezca al dictado de la actividad (tenant auto-scoped).
        Registra origen='Manual'. Auditable mediante el caller.
        """
        from fastapi import HTTPException
        from app.core.exceptions import NotFoundException

        actividad = await self._repo.find_by_id(actividad_id)
        if actividad is None:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        # Validate entrada belongs to this tenant and this dictado
        entrada = await self._ep_repo.find_by_id(entrada_padron_id)
        if entrada is None:
            raise HTTPException(status_code=404, detail="EntradaPadron no encontrada")

        # Check the entrada's version belongs to actividad's dictado
        active_vp = await self._vp_repo.find_active_by_dictado(actividad.dictado_id)
        if active_vp is None or entrada.version_id != active_vp.id:
            # Also accept any version of this dictado (not just active)
            from sqlalchemy import select as sa_select
            from app.models.version_padron import VersionPadron
            q = sa_select(VersionPadron).where(
                VersionPadron.tenant_id == self._tenant_id,
                VersionPadron.dictado_id == actividad.dictado_id,
            )
            r = await self._session.execute(q)
            versions = list(r.unique().scalars().all())
            version_ids = {v.id for v in versions}
            if entrada.version_id not in version_ids:
                raise HTTPException(
                    status_code=422,
                    detail="La entrada de padrón no pertenece al dictado de esta actividad",
                )

        return await self._calif_repo.upsert_for_actividad(
            entrada_padron_id=entrada_padron_id,
            dictado_id=actividad.dictado_id,
            actividad_id=actividad_id,
            actividad_nombre=actividad.nombre,
            nota_numerica=nota_numerica,
            nota_textual=nota_textual,
            aprobado=aprobado,
            origen="Manual",
        )

    async def importar_calificaciones_csv(
        self, actividad_id: uuid.UUID, file_content: bytes
    ) -> dict:
        """Parsea un CSV y upserta Calificaciones vinculadas a la actividad.

        CSV columns: entrada_padron_id, usuario_id, nombre, apellido, nota, aprobado.
        Identifica cada row por `entrada_padron_id` (UUID); ignora usuario_id.
        Upsert: si ya existe Calificacion para (entrada_padron_id, actividad_id) →
        actualiza; si no → crea.
        """
        actividad, _entradas = await self._get_actividad_and_entradas(actividad_id)

        text_content = file_content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text_content))
        if reader.fieldnames is None:
            raise HTTPException(status_code=422, detail="CSV vacío o sin encabezados")

        required_cols = {"entrada_padron_id", "nota", "aprobado"}
        missing = required_cols - set(str(f).strip() for f in reader.fieldnames)
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Columnas faltantes en CSV: {', '.join(sorted(missing))}",
            )

        created = 0
        updated = 0
        errors: list[str] = []

        for i, row in enumerate(reader, start=2):  # row 1 = header
            raw_eid = (row.get("entrada_padron_id") or "").strip()
            raw_nota = (row.get("nota") or "").strip()
            raw_aprobado = (row.get("aprobado") or "").strip()

            if not raw_eid:
                # Skip blank rows silently
                continue

            try:
                entrada_padron_id = uuid.UUID(raw_eid)
            except ValueError:
                errors.append(f"Fila {i}: entrada_padron_id inválido '{raw_eid}'")
                continue

            # Verify the entrada belongs to the actividad's dictado (tenant auto-scoped)
            entrada = await self._ep_repo.find_by_id(entrada_padron_id)
            if entrada is None:
                errors.append(f"Fila {i}: entrada_padron_id '{raw_eid}' no encontrado en el padrón")
                continue

            # Parse nota_numerica
            nota_numerica: float | None = None
            if raw_nota:
                try:
                    nota_numerica = float(raw_nota.replace(",", "."))
                except ValueError:
                    errors.append(f"Fila {i}: nota inválida '{raw_nota}'")
                    continue

            # Parse aprobado
            aprobado_val = raw_aprobado.lower()
            if aprobado_val in ("true", "1", "si", "sí", "s", "yes", "y"):
                aprobado = True
            elif aprobado_val in ("false", "0", "no", "n"):
                aprobado = False
            elif nota_numerica is not None:
                aprobado = nota_numerica >= 60.0
            else:
                aprobado = False

            # Determine if this is an update or create
            from sqlalchemy import select
            from app.models.calificacion import Calificacion

            q = select(Calificacion).where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.entrada_padron_id == entrada_padron_id,
                Calificacion.actividad_id == actividad_id,
            )
            r = await self._session.execute(q)
            is_update = r.unique().scalar_one_or_none() is not None

            await self._calif_repo.upsert_for_actividad(
                entrada_padron_id=entrada_padron_id,
                dictado_id=actividad.dictado_id,
                actividad_id=actividad_id,
                actividad_nombre=actividad.nombre,
                nota_numerica=nota_numerica,
                nota_textual=None,
                aprobado=aprobado,
            )

            if is_update:
                updated += 1
            else:
                created += 1

        return {
            "created": created,
            "updated": updated,
            "errors": errors,
            "total": created + updated,
        }
