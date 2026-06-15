import datetime
import uuid

from sqlalchemy import or_, select

from app.models.asignacion import Asignacion
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


def _vigente_predicate(hoy: datetime.date | None = None):
    """Vigencia-by-date predicate, reusable across queries (D3).

    Vigente <=> `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`.
    `estado_vigencia` is never stored; this predicate is the single source
    of truth for "vigente" in repository queries.
    """
    if hoy is None:
        hoy = datetime.date.today()
    return [
        Asignacion.desde <= hoy,
        or_(Asignacion.hasta.is_(None), Asignacion.hasta >= hoy),
    ]


class AsignacionRepository(BaseRepository[Asignacion]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=Asignacion, session=session, tenant_id=tenant_id)

    async def find_roles_vigentes(
        self, tenant_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> set[str]:
        """DISTINCT `rol` of alive, Vigente asignaciones (D3).

        Vigente <=> `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`.
        `estado_vigencia` is never stored; it is computed here from dates.
        """
        query = select(Asignacion.rol).where(
            Asignacion.tenant_id == tenant_id,
            Asignacion.usuario_id == usuario_id,
            Asignacion.deleted_at.is_(None),
            *_vigente_predicate(),
        )
        result = await self.session.execute(query)
        return {row[0] for row in result}

    async def find_mis_equipos_vigentes(
        self, tenant_id: uuid.UUID, usuario_id: uuid.UUID, filtros: dict | None = None
    ) -> list[Asignacion]:
        """Asignaciones vivas y VIGENTES del usuario, scoped a tenant (F4.2,
        D3 [SEC]).

        `usuario_id`/`tenant_id` MUST venir de la sesión (regla dura #8);
        este método no valida eso -- es responsabilidad del caller
        (EquipoService.mis_equipos). Acepta filtros opcionales por
        `materia_id`, `carrera_id`, `cohorte_id`, `rol`.
        """
        filtros = filtros or {}
        query = select(Asignacion).where(
            Asignacion.tenant_id == tenant_id,
            Asignacion.usuario_id == usuario_id,
            Asignacion.deleted_at.is_(None),
            *_vigente_predicate(),
        )
        for field in ("materia_id", "carrera_id", "cohorte_id", "rol"):
            value = filtros.get(field)
            if value is not None:
                query = query.where(getattr(Asignacion, field) == value)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_by_filtros(self, tenant_id: uuid.UUID, filtros: dict | None = None) -> list[Asignacion]:
        """Listado de asignaciones vivas del tenant (F4.3), excluye
        soft-deleted. Acepta filtros opcionales por `materia_id`,
        `carrera_id`, `cohorte_id`, `usuario_id`, `rol`, `responsable_id`.
        """
        filtros = filtros or {}
        query = select(Asignacion).where(
            Asignacion.tenant_id == tenant_id,
            Asignacion.deleted_at.is_(None),
        )
        for field in ("materia_id", "carrera_id", "cohorte_id", "usuario_id", "rol", "responsable_id"):
            value = filtros.get(field)
            if value is not None:
                query = query.where(getattr(Asignacion, field) == value)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def find_equipo(
        self,
        tenant_id: uuid.UUID,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        solo_vigentes: bool = False,
    ) -> list[Asignacion]:
        """Asignaciones vivas de un equipo (tripleta materia x carrera x
        cohorte, D2), scoped a tenant (D4). Si `solo_vigentes=True`, excluye
        las Vencidas (D3) -- usado por clonado (RN-12) y export."""
        query = select(Asignacion).where(
            Asignacion.tenant_id == tenant_id,
            Asignacion.materia_id == materia_id,
            Asignacion.carrera_id == carrera_id,
            Asignacion.cohorte_id == cohorte_id,
            Asignacion.deleted_at.is_(None),
        )
        if solo_vigentes:
            query = query.where(*_vigente_predicate())
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def create_many(self, rows: list[dict]) -> list[Asignacion]:
        """Alta en lote, grabando `tenant_id` de la sesión en cada fila (D4).

        Usado por asignación masiva (F4.4) y clonado (F4.5/RN-12). Una sola
        operación de flush -- el caller (router/service) decide cuándo
        commitear (D6, una sola transacción).
        """
        tenant_id = self._get_effective_tenant_id()
        instances = []
        for data in rows:
            row_data = dict(data)
            if tenant_id is not None:
                row_data.setdefault("tenant_id", tenant_id)
            instance = Asignacion(**row_data)
            self.session.add(instance)
            instances.append(instance)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def update_vigencia_equipo(
        self,
        tenant_id: uuid.UUID,
        contexto: dict,
        desde: datetime.date | None,
        hasta: datetime.date | None,
    ) -> int:
        """Actualiza `desde`/`hasta` de todas las asignaciones vivas del
        equipo (tripleta materia x carrera x cohorte), scoped a tenant (F4.6,
        D4). Sólo escribe los campos no-`None` provistos. Devuelve el número
        de filas afectadas (0 si el equipo no existe o pertenece a otro
        tenant)."""
        rows = await self.find_equipo(
            tenant_id, contexto["materia_id"], contexto["carrera_id"], contexto["cohorte_id"]
        )
        for row in rows:
            if desde is not None:
                row.desde = desde
            if hasta is not None:
                row.hasta = hasta
        if rows:
            await self.session.flush()
        return len(rows)

    async def buscar_docentes(self, tenant_id: uuid.UUID, query: str) -> list[Usuario]:
        """Autocompletado de docentes (F4.4, RN-30): `ILIKE` sobre
        `nombre`/`apellidos` de `Usuario` (E4), scoped a tenant y vivos
        (`deleted_at IS NULL`)."""
        pattern = f"%{query}%"
        stmt = select(Usuario).where(
            Usuario.tenant_id == tenant_id,
            Usuario.deleted_at.is_(None),
            or_(Usuario.nombre.ilike(pattern), Usuario.apellidos.ilike(pattern)),
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
