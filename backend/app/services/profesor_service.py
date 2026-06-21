"""ProfesorService — operaciones del panel docente (C-25).

Flujo: Routers → Services → Repositories → Models (regla dura #11).
Identidad y tenant_id SIEMPRE desde la sesión JWT (regla dura #8/#9).
"""

import datetime
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException
from app.models.actividad import Actividad
from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.comunicacion import Comunicacion
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.asignacion_repository import (
    AsignacionRepository,
    _vigente_predicate,
)
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.schemas.auth import CurrentUser
from app.services.analisis.compute import (
    compute_metricas_materia,
    resolve_umbral,
)
from app.services.audit.audit_logger import AuditLogger


class ProfesorService:
    """Operaciones del panel docente (F-C25)."""

    def __init__(self, db_session: AsyncSession, tenant_id: uuid.UUID):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self._asignacion_repo = AsignacionRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._usuario_repo = UsuarioRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._dictado_repo = DictadoRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._calificacion_repo = CalificacionRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._umbral_repo = UmbralMateriaRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._vp_repo = VersionPadronRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._ep_repo = EntradaPadronRepository(
            session=db_session, tenant_id=tenant_id
        )
        self._audit_repo = AuditLogRepository(
            session=db_session, tenant_id=tenant_id
        )

    @classmethod
    def create(cls, db_session: AsyncSession, tenant_id: uuid.UUID) -> "ProfesorService":
        return cls(db_session=db_session, tenant_id=tenant_id)

    async def _get_usuario(self, user_id: uuid.UUID) -> Usuario | None:
        """Resolve User.id → Usuario (perfil de negocio)."""
        return await self._usuario_repo.find_by_user_id(self.tenant_id, user_id)

    async def _get_dictados_profesor(self, usuario_id: uuid.UUID) -> list[Asignacion]:
        """Retorna asignaciones vigentes con rol PROFESOR para el usuario."""
        hoy = datetime.date.today()
        stmt = select(Asignacion).where(
            Asignacion.tenant_id == self.tenant_id,
            Asignacion.usuario_id == usuario_id,
            Asignacion.rol == "PROFESOR",
            Asignacion.dictado_id.isnot(None),
            Asignacion.deleted_at.is_(None),
            *_vigente_predicate(hoy),
        )
        result = await self.db_session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_dashboard(self, current_user: CurrentUser) -> dict[str, Any]:
        """Dashboard del profesor: materias asignadas + totales."""
        usuario = await self._get_usuario(current_user.user_id)
        if usuario is None:
            return {
                "materias_asignadas": [],
                "total_alumnos": 0,
                "total_encuentros": 0,
                "total_atrasados": 0,
            }

        asignaciones = await self._get_dictados_profesor(usuario.id)

        materias_asignadas = []
        total_alumnos = 0
        total_atrasados = 0

        for asig in asignaciones:
            dictado = await self._dictado_repo.find_by_id(asig.dictado_id)
            if dictado is None:
                continue

            materia = await self.db_session.get(Materia, dictado.materia_id)

            # Count alumnos in active version
            active_vp = await self._vp_repo.find_active_by_dictado(asig.dictado_id)
            n_alumnos = 0
            if active_vp:
                entradas = await self._ep_repo.find_by_version(active_vp.id)
                n_alumnos = len(entradas)
            total_alumnos += n_alumnos

            # Count atrasados — delegate to compute_metricas_materia so both
            # get_dashboard and get_metricas_dictado share one code path and
            # the boolean-aprobado rule is applied consistently (fix-regla-aprobado).
            califs = await self._calificacion_repo.find_by_dictado(asig.dictado_id)
            if califs:
                umbral_list = await self._umbral_repo.find_by_dictado(asig.dictado_id)
                umbral_materia = umbral_list[0] if umbral_list else None
                umbral = resolve_umbral(umbral_materia)
                califs_dicts = [
                    {
                        "entrada_padron_id": c.entrada_padron_id,
                        "actividad": c.actividad,
                        "nota_numerica": float(c.nota_numerica) if c.nota_numerica else None,
                        "nota_textual": c.nota_textual,
                        "aprobado": c.aprobado,
                    }
                    for c in califs
                ]
                metricas = compute_metricas_materia(califs_dicts, umbral)
                total_atrasados += metricas["atrasados"]

            materias_asignadas.append(
                {
                    "dictado_id": asig.dictado_id,
                    "materia_id": dictado.materia_id,
                    "materia_nombre": materia.nombre if materia else "",
                    "n_alumnos": n_alumnos,
                }
            )

        # Encuentros: count all instancias for the profesor's dictados
        total_encuentros = 0
        for asig in asignaciones:
            stmt = select(InstanciaEncuentro).where(
                InstanciaEncuentro.tenant_id == self.tenant_id,
                InstanciaEncuentro.dictado_id == asig.dictado_id,
            )
            r = await self.db_session.execute(stmt)
            total_encuentros += len(r.unique().scalars().all())

        return {
            "materias_asignadas": materias_asignadas,
            "total_alumnos": total_alumnos,
            "total_encuentros": total_encuentros,
            "total_atrasados": total_atrasados,
        }

    async def get_metricas_dictado(self, dictado_id: uuid.UUID) -> dict[str, Any]:
        """Métricas de un dictado vía compute_metricas_materia.

        Includes materia_nombre and cohorte_nombre resolved from the dictado's
        FK columns — tenant-scoped, read-only, no schema change required.
        """
        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        # Resolve human names for the dictado header (D2 — piggy-back on métricas)
        materia = await self.db_session.get(Materia, dictado.materia_id)
        from app.models.cohorte import Cohorte
        cohorte = await self.db_session.get(Cohorte, dictado.cohorte_id)
        materia_nombre = materia.nombre if materia else ""
        cohorte_nombre = cohorte.nombre if cohorte else ""

        umbral_list = await self._umbral_repo.find_by_dictado(dictado_id)
        umbral_materia = umbral_list[0] if umbral_list else None
        umbral = resolve_umbral(umbral_materia)

        califs = await self._calificacion_repo.find_by_dictado(dictado_id)
        califs_dicts = [
            {
                "entrada_padron_id": c.entrada_padron_id,
                "actividad": c.actividad,
                "nota_numerica": float(c.nota_numerica) if c.nota_numerica else None,
                "nota_textual": c.nota_textual,
                "aprobado": c.aprobado,
            }
            for c in califs
        ]
        metricas = compute_metricas_materia(califs_dicts, umbral)
        return {**metricas, "materia_nombre": materia_nombre, "cohorte_nombre": cohorte_nombre}

    async def get_alumnos_clasificados(
        self, dictado_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """Alumnos clasificados por estado (aprobado/atrasado/atrasado_null).

        Clasificación explícita por alumno × actividad:
        - No existe fila Calificacion para una actividad con fecha_limite vencida
          → esa actividad cuenta como "sin entrega" (atrasado_null) para ese alumno.
        - Fila presente y calificacion.aprobado == False → desaprobado.
        - Fila presente y calificacion.aprobado == True → aprobado para esa actividad.
        - faltante SIN fecha_limite => NO es atrasado_null.

        Un alumno es ATRASADO si tiene ≥1 actividad sin entrega (atrasado_null) O
        ≥1 calificacion con aprobado=False.
        """
        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        # Load actividades with fecha_limite
        hoy = datetime.date.today()
        stmt_act = select(Actividad).where(
            Actividad.tenant_id == self.tenant_id,
            Actividad.dictado_id == dictado_id,
            Actividad.deleted_at.is_(None),
        )
        r = await self.db_session.execute(stmt_act)
        actividades_obj = list(r.unique().scalars().all())

        # Build maps: actividad.nombre → actividad_id (for FK match) and vencida set
        actividad_id_by_nombre: dict[str, uuid.UUID] = {a.nombre: a.id for a in actividades_obj}
        actividades_vencidas_ids: set[uuid.UUID] = {
            a.id for a in actividades_obj if a.fecha_limite and a.fecha_limite < hoy
        }
        actividades_vencidas_nombres: set[str] = {
            a.nombre for a in actividades_obj if a.fecha_limite and a.fecha_limite < hoy
        }

        califs = await self._calificacion_repo.find_by_dictado(dictado_id)

        # Build per-alumno data indexed by (entrada_padron_id, actividad_id or nombre)
        from collections import defaultdict
        # Key: (entrada_padron_id, actividad_id) for FK rows; fallback by nombre
        alumno_califs_by_id: dict[uuid.UUID, dict[uuid.UUID, Any]] = defaultdict(dict)
        alumno_califs_by_nombre: dict[uuid.UUID, dict[str, Any]] = defaultdict(dict)
        for c in califs:
            if c.actividad_id is not None:
                alumno_califs_by_id[c.entrada_padron_id][c.actividad_id] = c
            alumno_califs_by_nombre[c.entrada_padron_id][c.actividad] = c

        # Load all alumnos from active version
        active_vp = await self._vp_repo.find_active_by_dictado(dictado_id)
        entradas = []
        if active_vp:
            entradas = await self._ep_repo.find_by_version(active_vp.id)

        result = []

        for entrada in entradas:
            desaprobadas: list[str] = []
            actividades_sin_entrega: list[str] = []

            for actividad in actividades_obj:
                act_id = actividad.id
                act_nombre = actividad.nombre
                es_vencida = act_id in actividades_vencidas_ids

                # Find the calificacion for this (entrada, actividad) — prefer FK match
                calif = alumno_califs_by_id[entrada.id].get(act_id)
                if calif is None:
                    calif = alumno_califs_by_nombre[entrada.id].get(act_nombre)

                if calif is None:
                    # No calificacion row
                    if es_vencida:
                        actividades_sin_entrega.append(act_nombre)
                    # else: actividad sin fecha_limite → neutral, no atraso
                else:
                    # Row present: use aprobado field directly
                    if not calif.aprobado:
                        desaprobadas.append(act_nombre)
                    # aprobado=True → OK

            is_atrasado = bool(desaprobadas) or bool(actividades_sin_entrega)

            if not is_atrasado:
                estado = "aprobado"
                subtipo = None
            elif bool(desaprobadas):
                estado = "atrasado"
                subtipo = "desaprobado"
            else:
                estado = "atrasado"
                subtipo = "atrasado_null"

            result.append(
                {
                    "alumno_id": entrada.id,
                    "nombre": entrada.nombre,
                    "apellido": entrada.apellidos,
                    "estado": estado,
                    "subtipo": subtipo,
                    "actividades_desaprobadas": desaprobadas,
                    "actividades_atrasado_null": actividades_sin_entrega,
                }
            )

        return result

    async def get_atrasados_cross_materia(
        self, current_user: CurrentUser
    ) -> list[dict[str, Any]]:
        """Alumnos con ≥1 actividad sin entrega en TODOS los dictados del profesor.

        Retorna: alumno (nombre/apellido/entrada_padron_id), dictado_id,
        materia_nombre, actividades_sin_entrega [].
        Tenant-scoped. Identidad desde JWT (current_user).
        """
        usuario = await self._get_usuario(current_user.user_id)
        if usuario is None:
            return []

        asignaciones = await self._get_dictados_profesor(usuario.id)
        if not asignaciones:
            return []

        result: list[dict[str, Any]] = []
        hoy = datetime.date.today()

        for asig in asignaciones:
            dictado = await self._dictado_repo.find_by_id(asig.dictado_id)
            if dictado is None:
                continue
            materia = await self.db_session.get(Materia, dictado.materia_id)
            materia_nombre = materia.nombre if materia else ""

            # Load actividades with fecha_limite vencida (only these generate sin_entrega)
            stmt_act = select(Actividad).where(
                Actividad.tenant_id == self.tenant_id,
                Actividad.dictado_id == asig.dictado_id,
                Actividad.deleted_at.is_(None),
            )
            r = await self.db_session.execute(stmt_act)
            actividades_obj = list(r.unique().scalars().all())

            actividades_vencidas = [
                a for a in actividades_obj if a.fecha_limite and a.fecha_limite < hoy
            ]
            if not actividades_vencidas:
                continue

            califs = await self._calificacion_repo.find_by_dictado(asig.dictado_id)

            # Build lookup by (entrada_padron_id, actividad_id or nombre)
            from collections import defaultdict
            califs_by_ep_act_id: dict[uuid.UUID, dict[uuid.UUID, Any]] = defaultdict(dict)
            califs_by_ep_nombre: dict[uuid.UUID, dict[str, Any]] = defaultdict(dict)
            for c in califs:
                if c.actividad_id is not None:
                    califs_by_ep_act_id[c.entrada_padron_id][c.actividad_id] = c
                califs_by_ep_nombre[c.entrada_padron_id][c.actividad] = c

            # Load padrón alumnos
            active_vp = await self._vp_repo.find_active_by_dictado(asig.dictado_id)
            if active_vp is None:
                continue
            entradas = await self._ep_repo.find_by_version(active_vp.id)

            for entrada in entradas:
                sin_entrega = []
                for actividad in actividades_vencidas:
                    calif = califs_by_ep_act_id[entrada.id].get(actividad.id)
                    if calif is None:
                        calif = califs_by_ep_nombre[entrada.id].get(actividad.nombre)
                    if calif is None:
                        sin_entrega.append(actividad.nombre)

                if sin_entrega:
                    result.append(
                        {
                            "entrada_padron_id": entrada.id,
                            "nombre": entrada.nombre,
                            "apellido": entrada.apellidos,
                            "dictado_id": asig.dictado_id,
                            "materia_nombre": materia_nombre,
                            "actividades_sin_entrega": sin_entrega,
                        }
                    )

        return result

    async def alta_alumnos_dictado_bulk(
        self,
        dictado_id: uuid.UUID,
        usuario_ids: list[uuid.UUID],
        current_user: CurrentUser,
    ) -> list[EntradaPadron]:
        """Alta de múltiples alumnos en el padrón activo del dictado.

        Calls alta_alumno_dictado for each usuario_id. Returns list of EntradaPadron.
        """
        entradas = []
        for uid in usuario_ids:
            entrada = await self.alta_alumno_dictado(
                dictado_id=dictado_id,
                alumno_data={"usuario_id": uid},
                current_user=current_user,
            )
            entradas.append(entrada)
        return entradas

    async def baja_alumnos_bulk(
        self,
        entrada_padron_ids: list[uuid.UUID],
        dictado_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> list[EntradaPadron]:
        """Soft-delete de múltiples EntradaPadron (baja masiva).

        Calificaciones PERSISTEN (no se borran — soft delete solo actualiza deleted_at).
        """
        entradas = []
        for ep_id in entrada_padron_ids:
            entrada = await self.baja_alumno_dictado(
                entrada_padron_id=ep_id,
                dictado_id=dictado_id,
                current_user=current_user,
            )
            entradas.append(entrada)
        return entradas

    async def obtener_padron_activo(
        self, dictado_id: uuid.UUID
    ) -> list[EntradaPadron]:
        """Devuelve las entradas de padrón de la versión activa del dictado."""
        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        active_vp = await self._vp_repo.find_active_by_dictado(dictado_id)
        if active_vp is None:
            return []
        return await self._ep_repo.find_by_version(active_vp.id)

    async def get_alumnos_disponibles(
        self, dictado_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """Alumnos del tenant con rol ALUMNO que NO están en el padrón activo del dictado.

        Ignora la cohorte — muestra todos los alumnos registrados en el tenant
        que no tienen ya una entrada activa en este dictado.
        """
        from app.models.user import User

        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        # Collect usuario_ids already in the active padron
        active_vp = await self._vp_repo.find_active_by_dictado(dictado_id)
        padron_user_ids: set[uuid.UUID] = set()
        if active_vp:
            entradas = await self._ep_repo.find_by_version(active_vp.id)
            for ep in entradas:
                if ep.usuario_id is not None:
                    padron_user_ids.add(ep.usuario_id)

        # All usuarios in tenant with rol ALUMNO via Asignacion vigente.
        # We do this as a subquery to keep the join on a single condition.
        hoy = datetime.date.today()
        from sqlalchemy import and_, exists, or_

        alumno_subq = (
            select(Asignacion.usuario_id)
            .where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.rol == "ALUMNO",
                Asignacion.deleted_at.is_(None),
                Asignacion.desde <= hoy,
                or_(Asignacion.hasta.is_(None), Asignacion.hasta >= hoy),
            )
            .scalar_subquery()
        )

        from app.models.user import User

        stmt = (
            select(Usuario, User)
            .join(User, User.id == Usuario.user_id)
            .where(
                Usuario.tenant_id == self.tenant_id,
                Usuario.deleted_at.is_(None),
                Usuario.id.in_(alumno_subq),
            )
        )
        r = await self.db_session.execute(stmt)
        rows = r.unique().all()

        result = []
        for usuario, user in rows:
            if usuario.id in padron_user_ids:
                continue
            result.append(
                {
                    "usuario_id": usuario.id,
                    "nombre": usuario.nombre,
                    "apellidos": usuario.apellidos,
                    "email": user.email,
                }
            )
        return result

    async def alta_alumno_dictado(
        self,
        dictado_id: uuid.UUID,
        alumno_data: dict,
        current_user: CurrentUser,
    ) -> EntradaPadron:
        """Alta individual de alumno en la versión activa del padrón.

        Flujo principal: `usuario_id` presente → resuelve nombre/apellidos/email
        desde el perfil del usuario y crea la entrada enlazada.
        Flujo fallback: nombre + apellidos libres (sin usuario_id).
        Idempotente-safe: si el usuario_id ya está en el padrón activo, lanza 409.
        """
        from fastapi import HTTPException

        # Verificar que el dictado existe y pertenece al tenant
        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        usuario_id_raw = alumno_data.get("usuario_id")
        usuario_id: uuid.UUID | None = (
            uuid.UUID(str(usuario_id_raw)) if usuario_id_raw and not isinstance(usuario_id_raw, uuid.UUID)
            else usuario_id_raw
        )

        nombre = alumno_data.get("nombre") or ""
        apellidos = alumno_data.get("apellidos") or ""
        email = alumno_data.get("email")

        if usuario_id is not None:
            # Resolve nombre/apellidos/email from existing Usuario profile
            perfil = await self._usuario_repo.find_by_id(usuario_id)
            if perfil is None:
                raise NotFoundException(resource="Usuario", id=usuario_id)

            # Resolve email from User (auth table)
            from app.models.user import User
            user_row = await self.db_session.get(User, perfil.user_id)
            nombre = perfil.nombre
            apellidos = perfil.apellidos
            email = user_row.email if user_row else email

        # Obtener o crear versión activa
        active_vp = await self._vp_repo.find_active_by_dictado(dictado_id)
        if active_vp is None:
            # Resolve usuario profile for cargado_por
            actor = await self._get_usuario(current_user.user_id)
            cargado_por = actor.id if actor else current_user.user_id
            active_vp = await self._vp_repo.create(
                {
                    "dictado_id": dictado_id,
                    "cargado_por": cargado_por,
                    "activa": True,
                }
            )

        # Idempotent-safe: reject if usuario_id already in this padron
        if usuario_id is not None:
            existing_entradas = await self._ep_repo.find_by_version(active_vp.id)
            already_in = any(ep.usuario_id == usuario_id for ep in existing_entradas)
            if already_in:
                raise HTTPException(
                    status_code=409,
                    detail="El alumno ya está en el padrón activo de este dictado",
                )

        entry_data: dict[str, Any] = {
            "version_id": active_vp.id,
            "nombre": nombre,
            "apellidos": apellidos,
            "email": email,
            "comision": alumno_data.get("comision"),
        }
        if usuario_id is not None:
            entry_data["usuario_id"] = usuario_id

        entrada = await self._ep_repo.create(entry_data)

        # Audit
        audit = AuditLogger(repository=self._audit_repo)
        from starlette.requests import Request
        # We don't have request object here — use direct create to keep it simple
        await self._audit_repo.create(
            {
                "tenant_id": self.tenant_id,
                "actor_id": current_user.user_id,
                "accion": AccionAuditoria.PADRON_ALUMNO_ALTA,
                "detalle": {
                    "dictado_id": str(dictado_id),
                    "entrada_id": str(entrada.id),
                    "nombre": alumno_data.get("nombre", ""),
                    "apellidos": alumno_data.get("apellidos", ""),
                },
                "filas_afectadas": 1,
            }
        )

        return entrada

    async def baja_alumno_dictado(
        self,
        entrada_padron_id: uuid.UUID,
        dictado_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> EntradaPadron:
        """Soft-delete de una EntradaPadron."""
        # Verify belongs to tenant (via find_by_id which scopes tenant)
        entrada = await self._ep_repo.find_by_id(entrada_padron_id)
        if entrada is None:
            raise NotFoundException(resource="EntradaPadron", id=entrada_padron_id)

        # Verify it belongs to the right dictado
        active_vp = await self._vp_repo.find_by_id(entrada.version_id)
        if active_vp is None or active_vp.dictado_id != dictado_id:
            raise NotFoundException(resource="EntradaPadron", id=entrada_padron_id)

        from datetime import UTC, datetime
        entrada.deleted_at = datetime.now(UTC)
        await self.db_session.flush()
        await self.db_session.refresh(entrada)

        await self._audit_repo.create(
            {
                "tenant_id": self.tenant_id,
                "actor_id": current_user.user_id,
                "accion": AccionAuditoria.PADRON_ALUMNO_BAJA,
                "detalle": {
                    "dictado_id": str(dictado_id),
                    "entrada_id": str(entrada_padron_id),
                },
                "filas_afectadas": 1,
            }
        )

        return entrada

    async def get_equipo_dictado(
        self,
        dictado_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> list[dict[str, Any]]:
        """Equipo docente del dictado (PROFESOR/TUTOR), excluyendo al usuario actual."""
        usuario = await self._get_usuario(current_user.user_id)
        if usuario is None:
            raise NotFoundException(resource="Usuario", id=current_user.user_id)

        # Verify professor has vigente asignacion to this dictado
        mis_asigs = await self._get_dictados_profesor(usuario.id)
        if not any(a.dictado_id == dictado_id for a in mis_asigs):
            raise NotFoundException(resource="Dictado", id=dictado_id)

        # Find all PROFESOR/TUTOR vigentes in this dictado
        hoy = datetime.date.today()
        stmt = select(Asignacion).where(
            Asignacion.tenant_id == self.tenant_id,
            Asignacion.dictado_id == dictado_id,
            Asignacion.rol.in_(["PROFESOR", "TUTOR"]),
            Asignacion.deleted_at.is_(None),
            *_vigente_predicate(hoy),
        )
        r = await self.db_session.execute(stmt)
        asignaciones = list(r.unique().scalars().all())

        result = []
        for asig in asignaciones:
            if asig.usuario_id == usuario.id:
                continue  # exclude self
            miembro = await self._usuario_repo.find_by_id(asig.usuario_id)
            result.append(
                {
                    "usuario_id": asig.usuario_id,
                    "nombre": miembro.nombre if miembro else "",
                    "apellidos": miembro.apellidos if miembro else "",
                    "rol": asig.rol,
                    "desde": asig.desde,
                    "hasta": asig.hasta,
                }
            )

        return result

    async def prepare_comunicado_atrasado_null(
        self,
        dictado_id: uuid.UUID,
        actividad_id: uuid.UUID,
        asunto_template: str,
        cuerpo_template: str,
        current_user: CurrentUser,
        request,
    ) -> dict[str, Any]:
        """Prepara y encola comunicado para alumnos con atrasado_null en la actividad."""
        from app.schemas.comunicaciones import EnvioMasivoItem, EnvioMasivoRequest
        from app.services.comunicaciones_service import ComunicacionesService

        # Validate dictado belongs to tenant
        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        # Validate actividad belongs to dictado and tenant
        stmt = select(Actividad).where(
            Actividad.id == actividad_id,
            Actividad.tenant_id == self.tenant_id,
            Actividad.dictado_id == dictado_id,
            Actividad.deleted_at.is_(None),
        )
        r = await self.db_session.execute(stmt)
        actividad = r.unique().scalar_one_or_none()
        if actividad is None:
            raise NotFoundException(resource="Actividad", id=actividad_id)

        # Get atrasado_null alumnos for this actividad
        clasificados = await self.get_alumnos_clasificados(dictado_id)
        atrasado_null = [
            a for a in clasificados
            if a["subtipo"] == "atrasado_null"
            and actividad.nombre in a["actividades_atrasado_null"]
        ]

        if not atrasado_null:
            return {"total": 0, "lote_id": None}

        # Build destinatarios — need emails from entradas
        destinatarios = []
        for alumno in atrasado_null:
            entrada = await self._ep_repo.find_by_id(alumno["alumno_id"])
            if entrada is None or not entrada.email:
                continue
            destinatarios.append(
                EnvioMasivoItem(
                    usuario_id=alumno["alumno_id"],
                    destinatario_email=entrada.email,
                    destinatario_nombre=alumno["nombre"],
                    destinatario_apellido=alumno["apellido"],
                )
            )

        if not destinatarios:
            return {"total": 0, "lote_id": None}

        envio_data = EnvioMasivoRequest(
            materia_id=dictado.materia_id,
            asunto_template=asunto_template,
            cuerpo_template=cuerpo_template,
            destinatarios=destinatarios,
        )

        com_service = ComunicacionesService.create(self.db_session, self.tenant_id)
        response = await com_service.enqueue_masivo(
            envio_data=envio_data,
            current_user=current_user,
            request=request,
        )

        return {"total": response.total, "lote_id": response.lote_id}

    async def prepare_comunicado_atrasados(
        self,
        dictado_id: uuid.UUID,
        actividad_id: uuid.UUID,
        subtipo: str,
        asunto_template: str,
        cuerpo_template: str,
        current_user: CurrentUser,
        request,
    ) -> dict[str, Any]:
        """Prepara y encola comunicado para alumnos con `subtipo` en la actividad.

        subtipo: 'desaprobado' | 'atrasado_null'
        Reutiliza el mismo pipeline que prepare_comunicado_atrasado_null.
        """
        from app.schemas.comunicaciones import EnvioMasivoItem, EnvioMasivoRequest
        from app.services.comunicaciones_service import ComunicacionesService

        # Validate dictado belongs to tenant
        dictado = await self._dictado_repo.find_by_id(dictado_id)
        if dictado is None:
            raise NotFoundException(resource="Dictado", id=dictado_id)

        # Validate actividad belongs to dictado and tenant
        stmt = select(Actividad).where(
            Actividad.id == actividad_id,
            Actividad.tenant_id == self.tenant_id,
            Actividad.dictado_id == dictado_id,
            Actividad.deleted_at.is_(None),
        )
        r = await self.db_session.execute(stmt)
        actividad = r.unique().scalar_one_or_none()
        if actividad is None:
            raise NotFoundException(resource="Actividad", id=actividad_id)

        # Get all classified alumnos and filter by subtipo
        clasificados = await self.get_alumnos_clasificados(dictado_id)

        if subtipo == "atrasado_null":
            targets = [
                a for a in clasificados
                if a["subtipo"] == "atrasado_null"
                and actividad.nombre in a["actividades_atrasado_null"]
            ]
        elif subtipo == "desaprobado":
            targets = [
                a for a in clasificados
                if a["subtipo"] == "desaprobado"
                and actividad.nombre in a["actividades_desaprobadas"]
            ]
        else:
            targets = []

        if not targets:
            return {"total": 0, "lote_id": None}

        # Build destinatarios from entradas
        destinatarios = []
        for alumno in targets:
            entrada = await self._ep_repo.find_by_id(alumno["alumno_id"])
            if entrada is None or not entrada.email:
                continue
            destinatarios.append(
                EnvioMasivoItem(
                    usuario_id=alumno["alumno_id"],
                    destinatario_email=entrada.email,
                    destinatario_nombre=alumno["nombre"],
                    destinatario_apellido=alumno["apellido"],
                )
            )

        if not destinatarios:
            return {"total": 0, "lote_id": None}

        envio_data = EnvioMasivoRequest(
            materia_id=dictado.materia_id,
            asunto_template=asunto_template,
            cuerpo_template=cuerpo_template,
            destinatarios=destinatarios,
        )

        com_service = ComunicacionesService.create(self.db_session, self.tenant_id)
        response = await com_service.enqueue_masivo(
            envio_data=envio_data,
            current_user=current_user,
            request=request,
        )

        return {"total": response.total, "lote_id": response.lote_id}

    # ── §10 Comunicado flexible ───────────────────────────────────────────────

    async def _resolve_entrada_email(
        self, entrada_padron_id: uuid.UUID
    ) -> tuple["EntradaPadron | None", str | None]:
        """Helper: resolve EntradaPadron and return (entrada, email_or_None).

        Shared by prepare_comunicado_flexible and (optionally) future refactors
        of the existing prepare_comunicado_* methods.

        Returns (None, None) if the entrada does not exist or belongs to a
        different tenant (the EP repo is already tenant-scoped).
        """
        entrada = await self._ep_repo.find_by_id(entrada_padron_id)
        if entrada is None:
            return None, None
        email = entrada.email if entrada.email else None
        return entrada, email

    async def _get_vigente_dictado_ids(self, usuario_id: uuid.UUID) -> set[uuid.UUID]:
        """Return the set of dictado_ids from vigente PROFESOR asignaciones."""
        asigs = await self._get_dictados_profesor(usuario_id)
        return {a.dictado_id for a in asigs}

    async def prepare_comunicado_flexible(
        self,
        actividad_id: uuid.UUID | None,
        asunto_template: str,
        cuerpo_template: str,
        destinatarios: list[dict],
        current_user,
        request,
    ) -> dict:
        """Encola comunicados a destinatarios explícitos con actividad opcional.

        Implementa D1–D5 del design doc:
        - D1: acepta lista explícita de destinatarios (individual o masivo).
        - D2: agrupa por materia y llama `enqueue_masivo` UNA vez por materia.
        - D4: si actividad_id es None, usa solo las 4 variables template base.
        - D5: NUNCA llama `update_estado` — delega 100% en `enqueue_masivo`.

        Governance CRÍTICO: nunca saltear el gate de aprobación del tenant.
        Identity: current_user (JWT). Tenant-scoped. Audited.

        Args:
            actividad_id: UUID de la actividad (opcional — None = omitir).
            asunto_template: template del asunto (min 1 char).
            cuerpo_template: template del cuerpo (min 1 char).
            destinatarios: list of {entrada_padron_id, dictado_id} dicts.
            current_user: CurrentUser desde la sesión JWT.
            request: Starlette Request para la auditoría.

        Returns:
            {"total": int, "lote_id": uuid | None, "lotes": [uuid, ...]}
        """
        from collections import defaultdict

        from app.schemas.comunicaciones import EnvioMasivoItem, EnvioMasivoRequest
        from app.services.comunicaciones_service import ComunicacionesService

        # Resolve actor usuario for PROFESOR vigente dictado validation
        usuario = await self._get_usuario(current_user.user_id)
        vigente_dictado_ids: set[uuid.UUID] = set()
        if usuario is not None:
            vigente_dictado_ids = await self._get_vigente_dictado_ids(usuario.id)

        # Optionally validate actividad_id belongs to the tenant
        actividad_nombre: str | None = None
        if actividad_id is not None:
            stmt = select(Actividad).where(
                Actividad.id == actividad_id,
                Actividad.tenant_id == self.tenant_id,
                Actividad.deleted_at.is_(None),
            )
            r = await self.db_session.execute(stmt)
            actividad_obj = r.unique().scalar_one_or_none()
            if actividad_obj is None:
                raise NotFoundException(resource="Actividad", id=actividad_id)
            actividad_nombre = actividad_obj.nombre

        # Group validated destinatarios by materia_id (D2)
        # For each destinatario: validate tenant + professor scope, resolve email
        materia_groups: dict[uuid.UUID, list[EnvioMasivoItem]] = defaultdict(list)

        for dest in destinatarios:
            ep_id: uuid.UUID = dest["entrada_padron_id"]
            dictado_id_raw: uuid.UUID = dest["dictado_id"]

            # Validate dictado belongs to tenant
            dictado = await self._dictado_repo.find_by_id(dictado_id_raw)
            if dictado is None:
                continue  # silently discard — not in tenant

            # Validate dictado is among the profesor's vigente dictados (D scope guard)
            if vigente_dictado_ids and dictado_id_raw not in vigente_dictado_ids:
                continue  # silently discard — not the professor's dictado

            # If actividad provided, verify it belongs to this dictado
            if actividad_id is not None and actividad_nombre:
                # Check the actividad is in this dictado
                stmt = select(Actividad).where(
                    Actividad.id == actividad_id,
                    Actividad.dictado_id == dictado_id_raw,
                    Actividad.tenant_id == self.tenant_id,
                    Actividad.deleted_at.is_(None),
                )
                r = await self.db_session.execute(stmt)
                act_in_dictado = r.unique().scalar_one_or_none()
                if act_in_dictado is None:
                    continue  # actividad not in this dictado — skip

            # Resolve entrada and email
            entrada, email = await self._resolve_entrada_email(ep_id)
            if entrada is None or not email:
                continue  # silently exclude (no email or not found)

            # Build EnvioMasivoItem
            item = EnvioMasivoItem(
                usuario_id=entrada.id,
                destinatario_email=email,
                destinatario_nombre=entrada.nombre,
                destinatario_apellido=entrada.apellidos,
            )
            materia_groups[dictado.materia_id].append(item)

        if not materia_groups:
            return {"total": 0, "lote_id": None, "lotes": []}

        # Call enqueue_masivo once per materia (D2)
        com_service = ComunicacionesService.create(self.db_session, self.tenant_id)
        total = 0
        lotes: list[uuid.UUID] = []

        for materia_id, items in materia_groups.items():
            envio_data = EnvioMasivoRequest(
                materia_id=materia_id,
                asunto_template=asunto_template,
                cuerpo_template=cuerpo_template,
                destinatarios=items,
            )
            response = await com_service.enqueue_masivo(
                envio_data=envio_data,
                current_user=current_user,
                request=request,
            )
            total += response.total
            lotes.append(response.lote_id)

        # Auditoría adicional del envío flexible (D5: additive, not replacing enqueue_masivo audit)
        await self._audit_repo.create(
            {
                "tenant_id": self.tenant_id,
                "actor_id": current_user.user_id,
                "accion": AccionAuditoria.COMUNICACION_ENVIAR,
                "detalle": {
                    "tipo": "comunicado_flexible",
                    "actividad_id": str(actividad_id) if actividad_id else None,
                    "total": total,
                    "n_lotes": len(lotes),
                    "lotes": [str(lid) for lid in lotes],
                },
                "filas_afectadas": total,
            }
        )

        # lote_id backward compat: first lote if exactly one, else None
        lote_id: uuid.UUID | None = lotes[0] if len(lotes) == 1 else None

        return {
            "total": total,
            "lote_id": lote_id,
            "lotes": [str(lid) for lid in lotes],
        }

    async def edit_calificacion(
        self,
        calificacion_id: uuid.UUID,
        data: dict,
        current_user: CurrentUser,
        request,
    ) -> Calificacion:
        """Edita una calificación individual, audita el cambio."""
        from app.core.exceptions import NotFoundException

        # Use scoped repository (tenant check automatic)
        stmt = select(Calificacion).where(
            Calificacion.id == calificacion_id,
            Calificacion.tenant_id == self.tenant_id,
        )
        r = await self.db_session.execute(stmt)
        calificacion = r.unique().scalar_one_or_none()
        if calificacion is None:
            raise NotFoundException(resource="Calificacion", id=calificacion_id)

        allowed_fields = {"nota_numerica", "nota_textual", "aprobado"}
        for field, value in data.items():
            if field in allowed_fields:
                setattr(calificacion, field, value)

        await self.db_session.flush()
        await self.db_session.refresh(calificacion)

        # Serialize data for JSON (Decimal → float, UUID → str)
        serializable_data = {}
        for k, v in data.items():
            if hasattr(v, "__float__"):
                serializable_data[k] = float(v)
            else:
                serializable_data[k] = str(v) if not isinstance(v, (bool, int, type(None))) else v

        await self._audit_repo.create(
            {
                "tenant_id": self.tenant_id,
                "actor_id": current_user.user_id,
                "accion": AccionAuditoria.CALIFICACION_EDITAR,
                "detalle": {
                    "calificacion_id": str(calificacion_id),
                    "cambios": serializable_data,
                },
                "filas_afectadas": 1,
            }
        )

        return calificacion
