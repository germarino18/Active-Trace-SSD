"""Service for the alumno (student) module — aggregates data from existing services."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository
from app.schemas.alumno import (
    ActividadEstado,
    AlumnoDashboardResponse,
    ComunicacionDetalleRead,
    ComunicacionRecibidaRead,
    EstadoAcademicoMateria,
    MateriaDashboardItem,
    ProgramaMateriaRead,
    ProximoColoquioItem,
    ProximaFechaItem,
)
from app.schemas.auth import CurrentUser
from app.services.avisos_service import AvisoService
from app.services.coloquios.coloquio_service import ColoquioService
from app.services.fechas_academicas_service import FechasAcademicasService
from app.services.mensajeria_service import MensajeriaService


class AlumnoService:
    """Orchestrates data aggregation for the authenticated student.

    Delegates to existing services and uses repositories for data
    not covered by existing service APIs.
    """

    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        current_user: CurrentUser,
    ):
        self._db = db
        self._tenant_id = tenant_id
        self._current_user = current_user
        self._usuario_repo = BaseRepository(
            model=Usuario, session=db, tenant_id=tenant_id,
        )
        self._dictado_repo = BaseRepository(
            model=Dictado, session=db, tenant_id=tenant_id,
        )
        self._materia_repo = BaseRepository(
            model=Materia, session=db, tenant_id=tenant_id,
        )
        self._entrada_repo = BaseRepository(
            model=EntradaPadron, session=db, tenant_id=tenant_id,
        )
        self._version_repo = BaseRepository(
            model=VersionPadron, session=db, tenant_id=tenant_id,
        )

    # ── helpers ────────────────────────────────────────────────────────

    async def _resolve_usuario(self) -> Usuario | None:
        usuarios = await self._usuario_repo.find_by(
            user_id=self._current_user.user_id,
        )
        return usuarios[0] if usuarios else None

    async def _get_dictados_del_alumno(
        self, usuario: Usuario | None,
    ) -> list[Dictado]:
        if usuario is None:
            return []
        entradas = await self._entrada_repo.find_by(usuario_id=usuario.id)
        if not entradas:
            return []
        version_ids = {e.version_id for e in entradas}
        dictados = []
        for vid in version_ids:
            v = await self._version_repo.find_by_id(vid)
            if v is not None:
                d = await self._dictado_repo.find_by_id(v.dictado_id)
                if d is not None:
                    dictados.append(d)
        return dictados

    async def _get_materias_para_dictados(
        self, dictados: list[Dictado],
    ) -> dict[uuid.UUID, Materia]:
        materia_ids = {d.materia_id for d in dictados}
        materias = {}
        for mid in materia_ids:
            m = await self._materia_repo.find_by_id(mid)
            if m is not None:
                materias[m.id] = m
        return materias

    async def _get_calificaciones(
        self, dictado_id: uuid.UUID, entrada_ids: list[uuid.UUID],
    ) -> list[Calificacion]:
        repo = CalificacionRepository(session=self._db, tenant_id=self._tenant_id)
        result = []
        for eid in entrada_ids:
            result.extend(
                await repo.find_by_dictado_and_entrada(dictado_id, eid)
            )
        return result

    @staticmethod
    def _compute_nota_final(calificaciones: list[Calificacion]) -> float | None:
        notas = [
            float(c.nota_numerica)
            for c in calificaciones
            if c.nota_numerica is not None
        ]
        if not notas:
            return None
        return round(sum(notas) / len(notas), 2)

    # ── Dashboard ─────────────────────────────────────────────────────

    async def get_dashboard(self) -> AlumnoDashboardResponse:
        usuario = await self._resolve_usuario()
        return AlumnoDashboardResponse(
            materias=await self._get_materias_con_progreso(usuario),
            avisos_no_leidos=await self._count_avisos_pendientes(),
            comunicaciones_no_leidas=await self._count_mensajes_no_leidos(usuario),
            proximos_coloquios=await self._get_proximos_coloquios(usuario),
            proximas_fechas=await self._get_proximas_fechas(usuario),
        )

    async def _get_materias_con_progreso(
        self, usuario: Usuario | None,
    ) -> list[MateriaDashboardItem]:
        dictados = await self._get_dictados_del_alumno(usuario)
        if not dictados:
            return []
        materias = await self._get_materias_para_dictados(dictados)
        entradas = await self._entrada_repo.find_by(usuario_id=usuario.id)
        entrada_ids = [e.id for e in entradas]

        result = []
        for d in dictados:
            materia = materias.get(d.materia_id)
            if materia is None:
                continue
            calificaciones = await self._get_calificaciones(d.id, entrada_ids)
            total = len(calificaciones)
            aprobadas = sum(1 for c in calificaciones if c.aprobado)
            estado = "al_dia" if aprobadas >= total * 0.6 else "atrasado"
            if total == 0:
                estado = "sin_actividad"
            result.append(MateriaDashboardItem(
                id=materia.id,
                nombre=materia.nombre,
                profesor="",
                progreso={"aprobadas": aprobadas, "total": total},
                estado=estado,
            ))
        return result

    async def _count_avisos_pendientes(self) -> int:
        service = AvisoService.create(self._db, self._tenant_id)
        pendientes = await service.get_pendientes(self._current_user)
        return len(pendientes)

    async def _count_mensajes_no_leidos(
        self, usuario: Usuario | None,
    ) -> int:
        if usuario is None:
            return 0
        service = MensajeriaService(db=self._db, tenant_id=self._tenant_id)
        hilos = await service.list_hilos(usuario.id)
        return sum(1 for h in hilos if h.no_leido)

    async def _get_proximos_coloquios(
        self, usuario: Usuario | None,
    ) -> list[ProximoColoquioItem]:
        if usuario is None:
            return []
        service = ColoquioService.create(self._db, self._tenant_id)
        reserva_repo = ReservaEvaluacionRepository(
            session=self._db, tenant_id=self._tenant_id,
        )
        reservas = await reserva_repo.list_activas_by_tenant(
            alumno_id=usuario.id,
        )
        result = []
        for r in reservas:
            result.append(ProximoColoquioItem(
                id=r.evaluacion_id,
                materia_nombre="",
                fecha=r.fecha_hora.isoformat() if r.fecha_hora else "",
                cupos_restantes=0,
            ))
        return result

    async def _get_proximas_fechas(
        self, usuario: Usuario | None,
    ) -> list[ProximaFechaItem]:
        dictados = await self._get_dictados_del_alumno(usuario)
        if not dictados:
            return []
        materias = await self._get_materias_para_dictados(dictados)
        service = FechasAcademicasService.create(self._db, self._tenant_id)
        result = []
        for d in dictados:
            materia = materias.get(d.materia_id)
            try:
                fechas = await service.list_fechas(
                    dictado_id=d.id,
                    periodo=None,
                    skip=0,
                    limit=50,
                    current_user=self._current_user,
                )
            except Exception:
                continue
            for f in fechas:
                if isinstance(f.fecha, datetime) and f.fecha >= datetime.now(timezone.utc):
                    result.append(ProximaFechaItem(
                        id=f.id,
                        materia_nombre=materia.nombre if materia else "",
                        tipo=f.tipo,
                        fecha=f.fecha.isoformat(),
                        descripcion=f.titulo,
                    ))
        result.sort(key=lambda x: x.fecha)
        return result[:20]

    # ── Estado académico ──────────────────────────────────────────────

    async def get_materias(self) -> list[EstadoAcademicoMateria]:
        usuario = await self._resolve_usuario()
        dictados = await self._get_dictados_del_alumno(usuario)
        if not dictados:
            return []
        materias = await self._get_materias_para_dictados(dictados)
        entradas = await self._entrada_repo.find_by(usuario_id=usuario.id)
        entrada_ids = [e.id for e in entradas]

        result = []
        for d in dictados:
            materia = materias.get(d.materia_id)
            if materia is None:
                continue
            calificaciones = await self._get_calificaciones(d.id, entrada_ids)
            actividades = [
                ActividadEstado(
                    id=c.id if isinstance(c.id, uuid.UUID) else uuid.UUID(str(c.id)),
                    nombre=c.actividad or "",
                    nota=float(c.nota_numerica) if c.nota_numerica is not None else None,
                    estado="aprobado" if c.aprobado else "desaprobado",
                )
                for c in calificaciones
            ]
            promedio = self._compute_nota_final(calificaciones)
            result.append(EstadoAcademicoMateria(
                id=materia.id,
                nombre=materia.nombre,
                profesor="",
                actividades=actividades,
                promedio=promedio,
                condicion="regular",
            ))
        return result

    async def get_materia_detalle(
        self, materia_id: uuid.UUID,
    ) -> EstadoAcademicoMateria:
        materia = await self._materia_repo.find_by_id(materia_id)
        if materia is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(resource="Materia", id=materia_id)

        usuario = await self._resolve_usuario()
        dictados = await self._get_dictados_del_alumno(usuario)
        dictado = next((d for d in dictados if d.materia_id == materia_id), None)
        if dictado is None:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(detail="No estás inscripto en esta materia")

        entradas = await self._entrada_repo.find_by(usuario_id=usuario.id)
        entrada_ids = [e.id for e in entradas]
        calificaciones = await self._get_calificaciones(dictado.id, entrada_ids)

        actividades = [
            ActividadEstado(
                id=c.id if isinstance(c.id, uuid.UUID) else uuid.UUID(str(c.id)),
                nombre=c.actividad or "",
                nota=float(c.nota_numerica) if c.nota_numerica is not None else None,
                estado="aprobado" if c.aprobado else "desaprobado",
            )
            for c in calificaciones
        ]
        return EstadoAcademicoMateria(
            id=materia.id,
            nombre=materia.nombre,
            profesor="",
            actividades=actividades,
            promedio=self._compute_nota_final(calificaciones),
            condicion="regular",
        )

    # ── Programas ────────────────────────────────────────────────────

    async def get_programas(self) -> list[ProgramaMateriaRead]:
        usuario = await self._resolve_usuario()
        dictados = await self._get_dictados_del_alumno(usuario)
        if not dictados:
            return []
        materias = await self._get_materias_para_dictados(dictados)
        from app.services.programas_service import ProgramasService
        service = ProgramasService.create(self._db, self._tenant_id)
        result = []
        for d in dictados:
            materia = materias.get(d.materia_id)
            try:
                programa = await service.get_by_dictado(
                    d.id, current_user=self._current_user,
                )
            except Exception:
                continue
            result.append(ProgramaMateriaRead(
                id=programa.id,
                materia_nombre=materia.nombre if materia else "",
                programa_nombre=programa.titulo,
                fecha_publicacion=programa.created_at.isoformat() if hasattr(programa, 'created_at') else "",
                referencia_archivo=str(programa.referencia_archivo) if programa.referencia_archivo else None,
            ))
        return result

    # ── Fechas académicas ────────────────────────────────────────────

    async def get_fechas(self) -> list:
        """Fechas is a simple list response — dict shape is fine."""
        usuario = await self._resolve_usuario()
        dictados = await self._get_dictados_del_alumno(usuario)
        if not dictados:
            return []
        materias = await self._get_materias_para_dictados(dictados)
        service = FechasAcademicasService.create(self._db, self._tenant_id)
        result = []
        for d in dictados:
            materia = materias.get(d.materia_id)
            try:
                fechas = await service.list_fechas(
                    dictado_id=d.id,
                    periodo=None,
                    skip=0,
                    limit=100,
                    current_user=self._current_user,
                )
            except Exception:
                continue
            for f in fechas:
                result.append({
                    "id": str(f.id),
                    "materia_nombre": materia.nombre if materia else "",
                    "tipo": f.tipo,
                    "fecha": f.fecha.isoformat() if isinstance(f.fecha, datetime) else str(f.fecha),
                    "descripcion": f.titulo,
                })
        return result

    # ── Comunicaciones recibidas ─────────────────────────────────────

    async def get_comunicaciones(self) -> list[ComunicacionRecibidaRead]:
        """Return communications where this student was the recipient."""
        usuario = await self._resolve_usuario()
        if usuario is None:
            return []
        from app.repositories.mensaje_repository import MensajeRepository
        from app.models.comunicacion import Comunicacion
        repo_mensaje = MensajeRepository(session=self._db, tenant_id=self._tenant_id)
        repo_com = BaseRepository(
            model=Comunicacion, session=self._db, tenant_id=self._tenant_id,
        )
        mensajes = await repo_mensaje.find_by(alumno_id=usuario.id)
        result = []
        seen = set()
        for m in mensajes:
            if m.comunicacion_id in seen:
                continue
            seen.add(m.comunicacion_id)
            com = await repo_com.find_by_id(m.comunicacion_id)
            if com is None:
                continue
            result.append(ComunicacionRecibidaRead(
                id=com.id,
                remitente=com.remitente_nombre or "",
                materia_nombre="",
                asunto=com.asunto,
                fecha_envio=com.created_at.isoformat() if hasattr(com, 'created_at') else "",
                estado=m.status.value if hasattr(m, 'status') else "Enviado",
            ))
        return result

    async def get_comunicacion_detalle(
        self, comunicacion_id: uuid.UUID,
    ) -> ComunicacionDetalleRead:
        from app.models.comunicacion import Comunicacion
        repo = BaseRepository(
            model=Comunicacion, session=self._db, tenant_id=self._tenant_id,
        )
        com = await repo.find_by_id(comunicacion_id)
        if com is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(resource="Comunicacion", id=comunicacion_id)
        return ComunicacionDetalleRead(
            id=com.id,
            asunto=com.asunto,
            cuerpo=com.cuerpo or "",
            remitente=com.remitente_nombre or "",
            materia_nombre="",
            fecha_envio=com.created_at.isoformat() if hasattr(com, 'created_at') else "",
            estado_entrega="Enviado",
        )
