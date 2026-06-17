"""Service for auditoria (audit panel and metrics) queries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Date, Select, cast, func, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.audit_log import AuditLog
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.schemas.auditoria import (
    AccionesPorDiaItem,
    ComunicacionesPorDocenteItem,
    InteraccionesPorDocenteMateriaItem,
    InteraccionItem,
    LogAuditoriaItem,
    LogAuditoriaPaginado,
    UltimasAccionesItem,
    UltimasAccionesResponse,
)


# ── Constants ────────────────────────────────────────────────────────

_DEFAULT_ULTIMAS_LIMIT = 200
_MAX_ULTIMAS_LIMIT = 1000
_DEFAULT_LOG_LIMIT = 50
_MAX_LOG_LIMIT = 200


class AuditoriaService:
    """Read-only queries over AuditLog and Comunicacion for the audit panel."""

    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self._session = session
        self._tenant_id = tenant_id

    @staticmethod
    def create(session: AsyncSession, tenant_id: UUID) -> "AuditoriaService":
        return AuditoriaService(session=session, tenant_id=tenant_id)

    # ── Scope helpers ────────────────────────────────────────────────

    async def _get_supervised_actor_ids(self, user_id: UUID) -> list[UUID]:
        """Return the list of `users.id` that a COORDINADOR supervises.

        A COORDINADOR supervises users (PROFESOR, TUTOR) assigned to the
        same materias where the COORDINADOR is assigned.

        Mapping: AuditLog.actor_id → users.id → Usuario.user_id → Usuario.id → Asignacion.usuario_id
        """
        # 1) Find Usuario.id for this COORDINADOR
        coord_result = await self._session.execute(
            select(Usuario.id).where(
                Usuario.tenant_id == self._tenant_id,
                Usuario.user_id == user_id,
                Usuario.deleted_at.is_(None),
            )
        )
        coord_usuario_id = coord_result.scalar_one_or_none()
        if not coord_usuario_id:
            return []

        # 2) Find materias where this COORDINADOR is assigned
        materias_result = await self._session.execute(
            select(Asignacion.materia_id).where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.usuario_id == coord_usuario_id,
                Asignacion.rol == "COORDINADOR",
                Asignacion.deleted_at.is_(None),
            )
        )
        materia_ids = [row[0] for row in materias_result.all()]
        if not materia_ids:
            return []

        # 3) Find usuarios (PROFESOR, TUTOR) assigned to those materias
        usuarios_result = await self._session.execute(
            select(Asignacion.usuario_id).where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.materia_id.in_(materia_ids),
                Asignacion.deleted_at.is_(None),
            )
        )
        usuario_ids = {row[0] for row in usuarios_result.all()}
        if not usuario_ids:
            return []

        # 4) Map usuario.id -> user_id (users.id) for AuditLog.actor_id
        users_result = await self._session.execute(
            select(Usuario.user_id).where(
                Usuario.tenant_id == self._tenant_id,
                Usuario.id.in_(usuario_ids),
                Usuario.deleted_at.is_(None),
            )
        )
        return [row[0] for row in users_result.all()]

    async def _apply_scope_filter(
        self,
        query: Select,
        user_id: UUID,
        roles: list[str],
        actor_column: any,
    ) -> Select:
        """Apply scope (propio) filter based on user roles.

        ADMIN and FINANZAS: no filter (see all).
        COORDINADOR: only records from supervised users.
        Others: no records (should not normally reach here due to guard).
        """
        if "ADMIN" in roles or "FINANZAS" in roles:
            return query

        if "COORDINADOR" in roles:
            actor_ids = await self._get_supervised_actor_ids(user_id)
            if actor_ids:
                return query.where(actor_column.in_(actor_ids))
            return query.where(cast(1, String) == "0")  # No supervised users → no results

        # Fallback: other roles see nothing
        return query.where(cast(1, String) == "0")

    async def _resolve_nombres(
        self,
        rows: list[dict],
    ) -> list[dict]:
        """Resolve actor_nombre and materia_nombre for a list of dicts."""
        actor_ids = {r["actor_id"] for r in rows if r.get("actor_id")}
        materia_ids = {r["materia_id"] for r in rows if r.get("materia_id")}

        nombres_actor: dict[UUID, str] = {}
        if actor_ids:
            result = await self._session.execute(
                select(Usuario.user_id, Usuario.nombre).where(
                    Usuario.user_id.in_(actor_ids),
                    Usuario.tenant_id == self._tenant_id,
                    Usuario.deleted_at.is_(None),
                )
            )
            for user_id, nombre in result.all():
                nombres_actor[user_id] = nombre

        nombres_materia: dict[UUID, str] = {}
        if materia_ids:
            result = await self._session.execute(
                select(Materia.id, Materia.nombre).where(
                    Materia.id.in_(materia_ids),
                    Materia.tenant_id == self._tenant_id,
                    Materia.deleted_at.is_(None),
                )
            )
            for mid, nombre in result.all():
                nombres_materia[mid] = nombre

        for row in rows:
            row["actor_nombre"] = nombres_actor.get(row.get("actor_id"))
            row["materia_nombre"] = nombres_materia.get(row.get("materia_id"))

        return rows

    # ── Acciones por día ─────────────────────────────────────────────

    async def get_acciones_por_dia(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        usuario_id: UUID | None = None,
        materia_id: UUID | None = None,
        user_id: UUID | None = None,
        roles: list[str] | None = None,
    ) -> list[AccionesPorDiaItem]:
        query = (
            select(
                cast(AuditLog.fecha_hora, Date).label("fecha"),
                func.count(AuditLog.id).label("total"),
            )
            .where(AuditLog.tenant_id == self._tenant_id)
        )

        if fecha_desde:
            query = query.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta:
            query = query.where(AuditLog.fecha_hora <= fecha_hasta)
        if usuario_id:
            query = query.where(AuditLog.actor_id == usuario_id)
        if materia_id:
            query = query.where(AuditLog.materia_id == materia_id)

        if user_id and roles:
            query = await self._apply_scope_filter(query, user_id, roles, AuditLog.actor_id)

        query = query.group_by(cast(AuditLog.fecha_hora, Date)).order_by("fecha")

        result = await self._session.execute(query)
        return [
            AccionesPorDiaItem(fecha=str(row.fecha), total=row.total)
            for row in result.all()
        ]

    # ── Comunicaciones por docente ───────────────────────────────────

    async def get_comunicaciones_por_docente(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        user_id: UUID | None = None,
        roles: list[str] | None = None,
    ) -> list[ComunicacionesPorDocenteItem]:
        query = (
            select(
                Comunicacion.enviado_por.label("docente_id"),
                Comunicacion.materia_id,
                func.count(Comunicacion.id).filter(Comunicacion.estado == "Pendiente").label("pendiente"),
                func.count(Comunicacion.id).filter(Comunicacion.estado == "Enviando").label("enviando"),
                func.count(Comunicacion.id).filter(Comunicacion.estado == "Enviado").label("enviado"),
                func.count(Comunicacion.id).filter(Comunicacion.estado == "Error").label("error"),
                func.count(Comunicacion.id).filter(Comunicacion.estado == "Cancelado").label("cancelado"),
            )
            .where(Comunicacion.tenant_id == self._tenant_id)
        )

        if fecha_desde:
            query = query.where(Comunicacion.created_at >= fecha_desde)
        if fecha_hasta:
            query = query.where(Comunicacion.created_at <= fecha_hasta)

        if user_id and roles:
            query = await self._apply_scope_filter(query, user_id, roles, Comunicacion.enviado_por)

        query = query.group_by(Comunicacion.enviado_por, Comunicacion.materia_id)

        result = await self._session.execute(query)
        return [
            ComunicacionesPorDocenteItem(
                docente_id=row.docente_id,
                materia_id=row.materia_id,
                pendiente=row.pendiente,
                enviando=row.enviando,
                enviado=row.enviado,
                error=row.error,
                cancelado=row.cancelado,
            )
            for row in result.all()
        ]

    # ── Interacciones por docente y materia ──────────────────────────

    async def get_interacciones_por_docente_materia(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        user_id: UUID | None = None,
        roles: list[str] | None = None,
    ) -> list[InteraccionesPorDocenteMateriaItem]:
        query = (
            select(
                AuditLog.actor_id.label("docente_id"),
                AuditLog.materia_id,
                AuditLog.accion,
                func.count(AuditLog.id).label("total"),
            )
            .where(AuditLog.tenant_id == self._tenant_id)
        )

        if fecha_desde:
            query = query.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta:
            query = query.where(AuditLog.fecha_hora <= fecha_hasta)

        if user_id and roles:
            query = await self._apply_scope_filter(query, user_id, roles, AuditLog.actor_id)

        query = query.group_by(AuditLog.actor_id, AuditLog.materia_id, AuditLog.accion)

        result = await self._session.execute(query)
        rows = result.all()

        # Aggregate into nested structure
        grouped: dict[tuple[UUID, UUID], list[InteraccionItem]] = {}
        for row in rows:
            key = (row.docente_id, row.materia_id)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(InteraccionItem(accion=row.accion, total=row.total))

        return [
            InteraccionesPorDocenteMateriaItem(
                docente_id=did,
                materia_id=mid,
                interacciones=items,
            )
            for (did, mid), items in grouped.items()
        ]

    # ── Últimas acciones ─────────────────────────────────────────────

    async def get_ultimas_acciones(
        self,
        limit: int = _DEFAULT_ULTIMAS_LIMIT,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
        usuario_id: UUID | None = None,
        user_id: UUID | None = None,
        roles: list[str] | None = None,
    ) -> UltimasAccionesResponse:
        effective_limit = min(limit, _MAX_ULTIMAS_LIMIT)

        query = (
            select(
                AuditLog.id,
                AuditLog.fecha_hora,
                AuditLog.actor_id,
                AuditLog.impersonado_id,
                AuditLog.materia_id,
                AuditLog.accion,
                AuditLog.detalle,
                AuditLog.filas_afectadas,
                AuditLog.ip,
                AuditLog.user_agent,
            )
            .where(AuditLog.tenant_id == self._tenant_id)
        )

        if fecha_desde:
            query = query.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta:
            query = query.where(AuditLog.fecha_hora <= fecha_hasta)
        if materia_id:
            query = query.where(AuditLog.materia_id == materia_id)
        if usuario_id:
            query = query.where(AuditLog.actor_id == usuario_id)

        if user_id and roles:
            query = await self._apply_scope_filter(query, user_id, roles, AuditLog.actor_id)

        query = query.order_by(AuditLog.fecha_hora.desc()).limit(effective_limit)

        result = await self._session.execute(query)
        rows = [row._asdict() for row in result.all()]

        rows = await self._resolve_nombres(rows)

        items = [UltimasAccionesItem(**r) for r in rows]

        return UltimasAccionesResponse(items=items, limit=effective_limit)

    # ── Log completo de auditoría ────────────────────────────────────

    async def get_log_auditoria(
        self,
        offset: int = 0,
        limit: int = _DEFAULT_LOG_LIMIT,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
        usuario_id: UUID | None = None,
        accion: str | None = None,
        user_id: UUID | None = None,
        roles: list[str] | None = None,
    ) -> LogAuditoriaPaginado:
        effective_limit = min(limit, _MAX_LOG_LIMIT)

        # Build base filter
        base_filters = [AuditLog.tenant_id == self._tenant_id]

        if fecha_desde:
            base_filters.append(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta:
            base_filters.append(AuditLog.fecha_hora <= fecha_hasta)
        if materia_id:
            base_filters.append(AuditLog.materia_id == materia_id)
        if usuario_id:
            base_filters.append(AuditLog.actor_id == usuario_id)
        if accion:
            base_filters.append(AuditLog.accion == accion)

        # Count query
        count_query = select(func.count(AuditLog.id)).where(*base_filters)
        if user_id and roles:
            count_query = await self._apply_scope_filter(count_query, user_id, roles, AuditLog.actor_id)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        data_query = (
            select(
                AuditLog.id,
                AuditLog.fecha_hora,
                AuditLog.actor_id,
                AuditLog.impersonado_id,
                AuditLog.materia_id,
                AuditLog.accion,
                AuditLog.detalle,
                AuditLog.filas_afectadas,
                AuditLog.ip,
                AuditLog.user_agent,
            )
            .where(*base_filters)
        )

        if user_id and roles:
            data_query = await self._apply_scope_filter(data_query, user_id, roles, AuditLog.actor_id)

        data_query = data_query.order_by(AuditLog.fecha_hora.desc()).offset(offset).limit(effective_limit)

        result = await self._session.execute(data_query)
        rows = [row._asdict() for row in result.all()]

        rows = await self._resolve_nombres(rows)

        items = [LogAuditoriaItem(**r) for r in rows]

        return LogAuditoriaPaginado(
            items=items,
            total=total,
            offset=offset,
            limit=effective_limit,
        )
