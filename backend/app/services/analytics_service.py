"""Service for analytics queries — atrasados, distribucion, prediccion, dashboard."""

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import Date, Select, cast, func, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.dictado import Dictado
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.version_padron import VersionPadron
from app.schemas.analytics import (
    AtrasadosPorCohorteItem,
    DashboardResponse,
    DistribucionNotasItem,
    PrediccionAbandonoItem,
)


class AnalyticsService:
    """Analytics queries over academic data for the analytics dashboard."""

    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self._session = session
        self._tenant_id = tenant_id

    @staticmethod
    def create(session: AsyncSession, tenant_id: UUID) -> "AnalyticsService":
        return AnalyticsService(session=session, tenant_id=tenant_id)

    async def _get_cohorte_alumnos(
        self,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
    ) -> dict[str, list[UUID]]:
        """Return dict of cohorte_nombre -> list of entrada_padron_ids."""
        query = (
            select(
                Cohorte.nombre.label("cohorte_nombre"),
                EntradaPadron.id.label("entrada_id"),
            )
            .select_from(EntradaPadron)
            .join(VersionPadron, VersionPadron.id == EntradaPadron.version_id)
            .join(Dictado, Dictado.id == VersionPadron.dictado_id)
            .join(Cohorte, Cohorte.id == Dictado.cohorte_id)
            .where(EntradaPadron.tenant_id == self._tenant_id)
            .where(VersionPadron.activa.is_(True))
            .where(Dictado.deleted_at.is_(None))
            .where(Cohorte.deleted_at.is_(None))
        )

        if carrera_id:
            query = query.where(Dictado.carrera_id == carrera_id)
        if cohorte_id:
            query = query.where(Dictado.cohorte_id == cohorte_id)

        result = await self._session.execute(query)
        grouped: dict[str, list[UUID]] = {}
        for row in result.all():
            grouped.setdefault(row.cohorte_nombre, []).append(row.entrada_id)
        return grouped

    async def get_atrasados_por_cohorte(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
    ) -> list[AtrasadosPorCohorteItem]:
        """Get atrasados grouped by cohorte.

        Simplified implementation: uses latest import data since
        Calificacion does not have a per-grade date column.
        """
        cohorte_alumnos = await self._get_cohorte_alumnos(
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
        )
        if not cohorte_alumnos:
            return []

        all_entrada_ids = [
            eid for ids in cohorte_alumnos.values() for eid in ids
        ]

        # Find atrasados: students with at least one failed subject
        failed_query = (
            select(
                Calificacion.entrada_padron_id,
                Dictado.cohorte_id,
            )
            .select_from(Calificacion)
            .join(Dictado, Dictado.id == Calificacion.dictado_id)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.entrada_padron_id.in_(all_entrada_ids))
            .where(Calificacion.aprobado.is_(False))
            .where(Dictado.deleted_at.is_(None))
            .distinct()
        )

        result = await self._session.execute(failed_query)
        atrasados_por_cohorte_raw: dict[UUID, set[UUID]] = {}
        for row in result.all():
            atrasados_por_cohorte_raw.setdefault(row.cohorte_id, set()).add(
                row.entrada_padron_id
            )

        # Map cohorte_id -> nombre
        cohorte_result = await self._session.execute(
            select(Cohorte.id, Cohorte.nombre).where(
                Cohorte.tenant_id == self._tenant_id,
                Cohorte.deleted_at.is_(None),
            )
        )
        cohorte_map: dict[UUID, str] = dict(cohorte_result.all())

        today = date.today()
        fecha_str = today.isoformat()

        items: list[AtrasadosPorCohorteItem] = []
        for cohorte_nombre, entrada_ids in sorted(cohorte_alumnos.items()):
            # Find cohorte_id for this cohorte_nombre
            cid = next(
                (cid for cid, name in cohorte_map.items() if name == cohorte_nombre),
                None,
            )
            total_alumnos = len(entrada_ids)
            total_atrasados = len(atrasados_por_cohorte_raw.get(cid, set()))
            porcentaje = (
                round((total_atrasados / total_alumnos) * 100, 1)
                if total_alumnos > 0
                else 0.0
            )
            items.append(
                AtrasadosPorCohorteItem(
                    fecha=fecha_str,
                    cohorte=cohorte_nombre,
                    total_atrasados=total_atrasados,
                    total_alumnos=total_alumnos,
                    porcentaje=porcentaje,
                )
            )

        items.sort(key=lambda x: (x.fecha, x.cohorte))
        return items

    async def get_distribucion_notas(
        self,
        dictado_id: UUID | None = None,
        materia_id: UUID | None = None,
        cohorte_id: UUID | None = None,
    ) -> list[DistribucionNotasItem]:
        """Get grade distribution histogram in 4 buckets."""
        query = (
            select(Calificacion.nota_numerica)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.nota_numerica.isnot(None))
        )

        if dictado_id:
            query = query.where(Calificacion.dictado_id == dictado_id)
        if materia_id:
            query = query.join(
                Dictado, Dictado.id == Calificacion.dictado_id
            ).where(Dictado.materia_id == materia_id)
        if cohorte_id:
            query = query.join(
                Dictado, Dictado.id == Calificacion.dictado_id
            ).where(Dictado.cohorte_id == cohorte_id)

        result = await self._session.execute(query)
        notas = [row[0] for row in result.all()]

        buckets = {
            "0-25%": 0,
            "26-50%": 0,
            "51-75%": 0,
            "76-100%": 0,
        }

        for nota in notas:
            pct = float(nota) * 10  # Convert 0-10 scale to percentage
            if pct <= 25:
                buckets["0-25%"] += 1
            elif pct <= 50:
                buckets["26-50%"] += 1
            elif pct <= 75:
                buckets["51-75%"] += 1
            else:
                buckets["76-100%"] += 1

        return [
            DistribucionNotasItem(rango=rango, cantidad=cantidad)
            for rango, cantidad in buckets.items()
        ]

    async def get_prediccion_abandono(
        self,
        cohorte_id: UUID | None = None,
        materia_id: UUID | None = None,
        riesgo: str | None = None,
        umbral: float = 60.0,
    ) -> list[PrediccionAbandonoItem]:
        """Predict dropout risk for students."""
        query = (
            select(
                EntradaPadron.id.label("alumno_id"),
                EntradaPadron.nombre.label("alumno_nombre"),
                EntradaPadron.apellidos,
                Materia.nombre.label("materia_nombre"),
                func.avg(Calificacion.nota_numerica).label("promedio"),
                func.count(Calificacion.id).filter(
                    Calificacion.aprobado.is_(False)
                ).label("atrasos"),
            )
            .select_from(Calificacion)
            .join(EntradaPadron, EntradaPadron.id == Calificacion.entrada_padron_id)
            .join(Dictado, Dictado.id == Calificacion.dictado_id)
            .join(Materia, Materia.id == Dictado.materia_id)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.nota_numerica.isnot(None))
            .where(EntradaPadron.tenant_id == self._tenant_id)
            .where(Dictado.deleted_at.is_(None))
            .group_by(
                EntradaPadron.id,
                EntradaPadron.nombre,
                EntradaPadron.apellidos,
                Materia.nombre,
            )
        )

        if cohorte_id:
            query = query.where(Dictado.cohorte_id == cohorte_id)
        if materia_id:
            query = query.where(Dictado.materia_id == materia_id)

        result = await self._session.execute(query)
        rows = result.all()

        items: list[PrediccionAbandonoItem] = []
        for row in rows:
            promedio = float(row.promedio) * 10  # Convert to percentage
            # Clasificar riesgo
            if row.atrasos >= 3 and promedio < umbral:
                nivel = "alto"
            elif row.atrasos >= 1 or promedio < umbral:
                nivel = "medio"
            else:
                nivel = "bajo"

            if riesgo and nivel != riesgo:
                continue

            items.append(
                PrediccionAbandonoItem(
                    alumno_id=row.alumno_id,
                    alumno_nombre=f"{row.alumno_nombre} {row.apellidos}".strip(),
                    materia=row.materia_nombre,
                    promedio=round(promedio, 1),
                    atrasos=row.atrasos,
                    riesgo=nivel,
                )
            )

        items.sort(key=lambda x: (
            {"alto": 0, "medio": 1, "bajo": 2}.get(x.riesgo, 3),
            x.promedio,
        ))
        return items

    async def get_dashboard(self) -> DashboardResponse:
        """Get consolidated KPIs for the analytics dashboard."""
        # Total alumnos (active EntradaPadron)
        total_alumnos_result = await self._session.execute(
            select(func.count(EntradaPadron.id.distinct())).where(
                EntradaPadron.tenant_id == self._tenant_id,
            )
        )
        total_alumnos = total_alumnos_result.scalar_one()

        # Total atrasados actual
        atrasados_result = await self._session.execute(
            select(func.count(Calificacion.entrada_padron_id.distinct())).where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.aprobado.is_(False),
            )
        )
        total_atrasados_actual = atrasados_result.scalar_one()

        # Promedio general
        promedio_result = await self._session.execute(
            select(func.avg(Calificacion.nota_numerica)).where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.nota_numerica.isnot(None),
            )
        )
        promedio_raw = promedio_result.scalar_one()
        promedio_general = round(float(promedio_raw) * 10, 1) if promedio_raw else 0.0

        # Prediccion counts
        prediccion = await self.get_prediccion_abandono()
        bajo = sum(1 for p in prediccion if p.riesgo == "bajo")
        medio = sum(1 for p in prediccion if p.riesgo == "medio")
        alto = sum(1 for p in prediccion if p.riesgo == "alto")

        # Tendencia del último mes (simplified: one data point)
        hace_un_mes = date.today() - timedelta(days=30)
        tendencia_result = await self._session.execute(
            select(
                cast(Calificacion.importado_at, Date).label("fecha"),
                func.count(Calificacion.entrada_padron_id.distinct()).label("total"),
            ).where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.aprobado.is_(False),
                Calificacion.importado_at >= hace_un_mes,
            ).group_by(cast(Calificacion.importado_at, Date))
            .order_by("fecha")
        )
        tendencia = [
            {"fecha": str(row.fecha), "total": row.total}
            for row in tendencia_result.all()
        ]

        # Total materias activas
        materias_result = await self._session.execute(
            select(func.count(Materia.id.distinct())).where(
                Materia.tenant_id == self._tenant_id,
                Materia.deleted_at.is_(None),
                Materia.estado == "Activa",
            )
        )
        total_materias = materias_result.scalar_one()

        return DashboardResponse(
            total_alumnos=total_alumnos,
            total_atrasados_actual=total_atrasados_actual,
            promedio_general=promedio_general,
            alumnos_en_riesgo={"bajo": bajo, "medio": medio, "alto": alto},
            tendencia_atrasados_ultimo_mes=tendencia,
            total_materias=total_materias,
        )
