import uuid
from collections import defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.acciones_auditoria import AccionAuditoria
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.services.analisis.compute import (
    compute_alumno_atrasado,
    compute_metricas_materia,
    compute_nota_final,
    compute_ranking_aprobadas,
    detect_tps_sin_corregir,
    resolve_umbral,
)


class AnalisisService:
    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id
        self.calificacion_repo = CalificacionRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.umbral_repo = UmbralMateriaRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.ep_repo = EntradaPadronRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.dictado_repo = DictadoRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.vp_repo = VersionPadronRepository(
            session=db_session, tenant_id=tenant_id
        )

    async def _log_audit(
        self, accion: str, materia_id: uuid.UUID | None = None,
    ) -> None:
        repo = AuditLogRepository(
            session=self.db_session, tenant_id=self.tenant_id
        )
        await repo.create({
            "actor_id": self.current_user_id,
            "accion": accion,
            "materia_id": materia_id,
            "detalle": None,
            "filas_afectadas": None,
            "ip": None,
            "user_agent": None,
        })

    async def _get_entrada_map(
        self, dictado_id: uuid.UUID,
    ) -> dict[uuid.UUID, dict[str, Any]]:
        version = await self.vp_repo.find_active_by_dictado(dictado_id)
        if version is None:
            return {}
        entradas = await self.ep_repo.find_by_version(version.id)
        return {
            e.id: {
                "nombre": e.nombre,
                "apellidos": e.apellidos,
                "comision": e.comision,
                "regional": e.regional,
            }
            for e in entradas
        }

    def _enrich_calificaciones(
        self,
        calificaciones: list,
        entrada_map: dict[uuid.UUID, dict],
    ) -> list[dict]:
        result = []
        for c in calificaciones:
            info = entrada_map.get(c.entrada_padron_id, {})
            result.append({
                "entrada_padron_id": c.entrada_padron_id,
                "dictado_id": c.dictado_id,
                "actividad": c.actividad,
                "nota_numerica": float(c.nota_numerica) if c.nota_numerica is not None else None,
                "nota_textual": c.nota_textual,
                "aprobado": c.aprobado,
                "nombre": info.get("nombre", ""),
                "apellidos": info.get("apellidos", ""),
                "comision": info.get("comision"),
            })
        return result

    async def get_alumnos_atrasados(
        self, dictado_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        califs = await self.calificacion_repo.find_by_dictado(dictado_id)
        entrada_map = await self._get_entrada_map(dictado_id)
        enriched = self._enrich_calificaciones(califs, entrada_map)

        umbrales = await self.umbral_repo.find_by_dictado(dictado_id)
        umbral = resolve_umbral(umbrales[0] if umbrales else None)

        actividades = list({c["actividad"] for c in enriched})
        alumnos = defaultdict(list)
        for c in enriched:
            alumnos[c["entrada_padron_id"]].append(c)

        result = []
        for ep_id, califs_alumno in alumnos.items():
            info = entrada_map.get(ep_id, {})
            atrasado, faltantes, desaprobadas = compute_alumno_atrasado(
                califs_alumno, actividades, umbral,
            )
            if atrasado:
                result.append({
                    "alumno_id": ep_id,
                    "alumno_nombre": info.get("nombre", ""),
                    "alumno_apellido": info.get("apellidos", ""),
                    "comision": info.get("comision"),
                    "actividades_faltantes": faltantes,
                    "actividades_desaprobadas": desaprobadas,
                })

        await self._log_audit(
            AccionAuditoria.ANALISIS_ATRASADOS_CONSULTA,
            materia_id=dictado_id,
        )
        return result

    async def get_ranking_aprobadas(
        self, dictado_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        califs = await self.calificacion_repo.find_by_dictado(dictado_id)
        entrada_map = await self._get_entrada_map(dictado_id)
        enriched = self._enrich_calificaciones(califs, entrada_map)
        result = compute_ranking_aprobadas(enriched)

        await self._log_audit(
            AccionAuditoria.ANALISIS_RANKING_CONSULTA,
            materia_id=dictado_id,
        )
        return result

    async def get_reporte_materia(
        self, dictado_id: uuid.UUID,
    ) -> dict[str, Any]:
        califs = await self.calificacion_repo.find_by_dictado(dictado_id)
        entrada_map = await self._get_entrada_map(dictado_id)
        enriched = self._enrich_calificaciones(califs, entrada_map)

        umbrales = await self.umbral_repo.find_by_dictado(dictado_id)
        umbral = resolve_umbral(umbrales[0] if umbrales else None)

        result = compute_metricas_materia(enriched, umbral)

        await self._log_audit(
            AccionAuditoria.ANALISIS_REPORTE_CONSULTA,
            materia_id=dictado_id,
        )
        return result

    async def get_notas_finales(
        self, dictado_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        califs = await self.calificacion_repo.find_by_dictado(dictado_id)
        entrada_map = await self._get_entrada_map(dictado_id)
        enriched = self._enrich_calificaciones(califs, entrada_map)

        alumnos = defaultdict(list)
        for c in enriched:
            alumnos[c["entrada_padron_id"]].append(c)

        result = []
        for ep_id, califs_alumno in alumnos.items():
            info = entrada_map.get(ep_id, {})
            nota = compute_nota_final(califs_alumno)
            result.append({
                "alumno_id": ep_id,
                "alumno_nombre": info.get("nombre", ""),
                "alumno_apellido": info.get("apellidos", ""),
                "nota_final": nota,
                "actividades_consideradas": sum(
                    1 for c in califs_alumno if c.get("nota_numerica") is not None
                ),
            })

        await self._log_audit(
            AccionAuditoria.ANALISIS_NOTAS_CONSULTA,
            materia_id=dictado_id,
        )
        return result

    async def get_tps_sin_corregir(
        self,
        dictado_id: uuid.UUID,
        finalizaciones: list[dict],
    ) -> list[dict[str, Any]]:
        if not finalizaciones:
            raise ValueError(
                "Se requiere importar reporte de finalización LMS primero"
            )

        califs = await self.calificacion_repo.find_by_dictado(dictado_id)
        entrada_map = await self._get_entrada_map(dictado_id)
        enriched = self._enrich_calificaciones(califs, entrada_map)

        pendientes = detect_tps_sin_corregir(finalizaciones, enriched, es_textual=True)

        result = []
        for p in pendientes:
            info = entrada_map.get(p["alumno_id"], {})
            result.append({
                "alumno_id": p["alumno_id"],
                "alumno_nombre": info.get("nombre", ""),
                "alumno_apellido": info.get("apellidos", ""),
                "actividad": p["actividad"],
                "fecha_finalizacion": p["fecha_finalizacion"],
                "dictado_id": dictado_id,
                "comision": info.get("comision"),
            })

        await self._log_audit(
            AccionAuditoria.ANALISIS_TPS_CONSULTA,
            materia_id=dictado_id,
        )
        return result

    async def get_monitor_general(
        self,
        dictado_id: uuid.UUID | None = None,
        comision: str | None = None,
        q: str | None = None,
        estado: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]:
        califs = await self.calificacion_repo.find_all()
        if dictado_id:
            califs = [c for c in califs if c.dictado_id == dictado_id]

        dictado_ids = {c.dictado_id for c in califs}
        entrada_map = {}
        for did in dictado_ids:
            entrada_map.update(await self._get_entrada_map(did))

        enriched = self._enrich_calificaciones(califs, entrada_map)

        if q:
            q_lower = q.lower()
            enriched = [
                c for c in enriched
                if q_lower in c.get("nombre", "").lower()
                or q_lower in c.get("apellidos", "").lower()
            ]

        if comision:
            enriched = [c for c in enriched if c.get("comision") == comision]

        alumnos = defaultdict(list)
        for c in enriched:
            alumnos[c["entrada_padron_id"]].append(c)

        items = []
        for ep_id, califs_alumno in alumnos.items():
            info = entrada_map.get(ep_id, {})
            umbrales = []
            for did in {c["dictado_id"] for c in califs_alumno}:
                u = await self.umbral_repo.find_by_dictado(did)
                if u:
                    umbrales.append(u[0])
            umbral = resolve_umbral(umbrales[0] if umbrales else None)

            actividades = list({c["actividad"] for c in califs_alumno})
            atrasado, faltantes, _ = compute_alumno_atrasado(
                califs_alumno, actividades, umbral,
            )
            aprobadas = sum(1 for c in califs_alumno if c["aprobado"])
            desaprobadas = sum(1 for c in califs_alumno if not c["aprobado"])

            if estado == "atrasado" and not atrasado:
                continue
            if estado == "aprobado" and atrasado:
                continue

            items.append({
                "alumno_id": ep_id,
                "alumno_nombre": info.get("nombre", ""),
                "alumno_apellido": info.get("apellidos", ""),
                "comision": info.get("comision"),
                "actividades_totales": len(actividades),
                "actividades_aprobadas": aprobadas,
                "actividades_desaprobadas": desaprobadas,
                "actividades_faltantes": len(faltantes),
                "estado": "atrasado" if atrasado else "aprobado",
            })

        total_count = len(items)
        paginated = items[offset:offset + limit]

        await self._log_audit(
            AccionAuditoria.ANALISIS_MONITOR_CONSULTA,
        )
        return {
            "items": paginated,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
        }
