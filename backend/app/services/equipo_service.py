"""Reglas de negocio de operaciones de equipo docente (C-08, D9).

Un "equipo" es el conjunto de asignaciones vivas que comparten la tripleta
de contexto `(materia_id, carrera_id, cohorte_id)` dentro de un tenant (D2).
Flujo Routers -> Services -> Repositories -> Models (regla dura #11).
Identidad y `tenant_id` SIEMPRE desde `current_user` (sesión JWT), nunca de
un parámetro (regla dura #8/#9, D3/D4 [SEC]). `estado_vigencia` es derivado
por fechas (D3, reusa `estado_vigencia_for`), nunca almacenado.
"""

import uuid

from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException
from app.models.asignacion import Asignacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.asignacion import EstadoVigencia
from app.schemas.auth import CurrentUser
from app.schemas.equipo import (
    AsignacionMasivaCreate,
    AsignacionMasivaResultado,
    ClonarEquipoCreate,
    DocenteResponse,
    EquipoExportItem,
    EquipoFiltros,
    MisEquiposFiltros,
    VigenciaEquipoUpdate,
)
from app.services.asignacion_service import estado_vigencia_for
from app.services.audit.audit_logger import AuditLogger

# Context fields validated against the caller's tenant (D4 [SEC], regla dura #9).
_CONTEXT_FIELDS = ("materia_id", "carrera_id", "cohorte_id")


class EquipoMisEquiposItem:
    """Vista de una fila de "mis-equipos" con `estado_vigencia` derivado (D3).

    No es un Pydantic BaseModel (la respuesta HTTP se serializa en el
    router de group 4); acá es un value object simple para que el service
    no dependa del esquema de respuesta del router.
    """

    def __init__(self, asignacion: Asignacion, estado_vigencia: EstadoVigencia):
        self.id = asignacion.id
        self.usuario_id = asignacion.usuario_id
        self.rol = asignacion.rol
        self.materia_id = asignacion.materia_id
        self.carrera_id = asignacion.carrera_id
        self.cohorte_id = asignacion.cohorte_id
        self.dictado_id = asignacion.dictado_id
        self.comisiones = asignacion.comisiones
        self.responsable_id = asignacion.responsable_id
        self.desde = asignacion.desde
        self.hasta = asignacion.hasta
        self.estado_vigencia = estado_vigencia.value


class EquipoService:
    """Operaciones de equipo (F4.2-F4.7) sobre `Asignacion` (D1/D9).

    El service no toca la sesión SQL salvo vía repository. Las operaciones
    de bloque (masiva, clonado, vigencia) son transaccionales: este service
    NO commitea -- el router hace un único `await db.commit()` (D6). Cada
    operación de bloque emite UN `ASIGNACION_MODIFICAR` (D7); lecturas
    (mis-equipos, listado, export) no auditan.
    """

    def __init__(
        self,
        asignacion_repo: AsignacionRepository,
        usuario_repo: UsuarioRepository,
        materia_repo: MateriaRepository,
        carrera_repo: CarreraRepository,
        cohorte_repo: CohorteRepository,
        audit_repo: AuditLogRepository,
    ):
        self._repo = asignacion_repo
        self._usuario_repo = usuario_repo
        self._context_repos = {
            "materia_id": (materia_repo, "Materia"),
            "carrera_id": (carrera_repo, "Carrera"),
            "cohorte_id": (cohorte_repo, "Cohorte"),
        }
        self._audit = AuditLogger(repository=audit_repo)

    async def mis_equipos(
        self, current_user: CurrentUser, filtros: MisEquiposFiltros | None = None
    ) -> list[EquipoMisEquiposItem]:
        """Asignaciones VIGENTES del docente autenticado (F4.2, D3 [SEC]).

        `usuario_id`/`tenant_id` se derivan EXCLUSIVAMENTE de
        `current_user` (regla dura #8) -- nunca de un parámetro. Por
        defecto sólo vigentes; admite filtros opcionales (materia, rol,
        carrera, cohorte).
        """
        usuario = await self._usuario_repo.find_by_user_id(current_user.tenant_id, current_user.user_id)
        if usuario is None:
            return []

        filtro_dict: dict = {}
        if filtros is not None:
            for field in ("materia_id", "carrera_id", "cohorte_id"):
                value = getattr(filtros, field, None)
                if value is not None:
                    filtro_dict[field] = value
            if filtros.rol is not None:
                filtro_dict["rol"] = filtros.rol.value

        rows = await self._repo.find_mis_equipos_vigentes(
            current_user.tenant_id, usuario.id, filtros=filtro_dict
        )

        items = [EquipoMisEquiposItem(row, estado_vigencia_for(row)) for row in rows]

        if filtros is not None and filtros.estado is not None:
            items = [item for item in items if item.estado_vigencia == filtros.estado.value]

        return items

    async def listar_equipos(
        self, tenant_id: uuid.UUID, filtros: EquipoFiltros | None = None
    ) -> list[Asignacion]:
        """Listado filtrable de asignaciones vivas del tenant (F4.3).

        Passthrough delgado a `AsignacionRepository.find_by_filtros` --
        mantiene el acceso a datos fuera del router (regla dura #11).
        `tenant_id` viene de la sesión del caller (D4 [SEC]).
        """
        filtro_dict: dict = {}
        if filtros is not None:
            for field in ("materia_id", "carrera_id", "cohorte_id", "usuario_id", "responsable_id"):
                value = getattr(filtros, field, None)
                if value is not None:
                    filtro_dict[field] = value
            if filtros.rol is not None:
                filtro_dict["rol"] = filtros.rol.value

        return await self._repo.find_by_filtros(tenant_id, filtros=filtro_dict)

    async def buscar_docentes(self, tenant_id: uuid.UUID, query: str) -> list[DocenteResponse]:
        """Autocompletado de docentes (F4.4, RN-30).

        Passthrough delgado a `AsignacionRepository.buscar_docentes` --
        mantiene el acceso a datos fuera del router (regla dura #11).
        """
        usuarios = await self._repo.buscar_docentes(tenant_id, query)
        return [
            DocenteResponse(usuario_id=usuario.id, nombre=usuario.nombre, apellidos=usuario.apellidos)
            for usuario in usuarios
        ]

    @staticmethod
    async def _ensure_exists(repo, resource_name: str, entity_id: uuid.UUID) -> None:
        """Buscar `entity_id` por `repo.find_by_id` (ya scoped al tenant del
        caller, D4 [SEC]) -- ajeno/inexistente => `NotFoundException`
        (regla dura #9). Helper compartido por `_validate_context`,
        `_validate_usuarios` y `_validate_cohortes`."""
        entity = await repo.find_by_id(entity_id)
        if entity is None:
            raise NotFoundException(resource=resource_name, id=entity_id)

    async def _validate_context(self, tenant_id: uuid.UUID, contexto: dict) -> None:
        """Valida materia/carrera/cohorte contra el tenant del caller (D4
        [SEC], regla dura #9): una referencia ajena es indistinguible de
        "no existe" -> `NotFoundException`."""
        for field, (repo, resource_name) in self._context_repos.items():
            value = contexto.get(field)
            if value is None:
                continue
            await self._ensure_exists(repo, resource_name, value)

    async def _validate_usuarios(self, usuario_ids: list[uuid.UUID]) -> None:
        """Valida que cada `usuario_id` (perfil `Usuario`, E4) pertenezca al
        tenant del caller (D4 [SEC]) -- ajeno => `NotFoundException`."""
        for usuario_id in usuario_ids:
            await self._ensure_exists(self._usuario_repo, "Usuario", usuario_id)

    async def _validate_cohortes(self, cohorte_ids: list[uuid.UUID]) -> None:
        """Valida que cada `cohorte_id` (origen/destino del clonado, F4.5)
        pertenezca al tenant del caller (D4 [SEC]) -- ajeno =>
        `NotFoundException`."""
        cohorte_repo, resource_name = self._context_repos["cohorte_id"]
        for cohorte_id in cohorte_ids:
            await self._ensure_exists(cohorte_repo, resource_name, cohorte_id)

    async def asignacion_masiva(
        self,
        data: AsignacionMasivaCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> AsignacionMasivaResultado:
        """Asignar un bloque de N docentes a materia x carrera x cohorte x
        rol con vigencia común (F4.4, RN-30, D5/D6).

        Valida usuarios y contexto contra el tenant (404 si ajeno, abort
        total sin crear nada). Un docente con una asignacion VIGENTE
        equivalente (mismo contexto + rol) se omite y se reporta como
        ya-existente, sin duplicar (D5). Crea el resto vía `create_many` y
        emite UN `ASIGNACION_MODIFICAR` con `filas_afectadas` = N creadas.
        """
        tenant_id = current_user.tenant_id
        contexto = {"materia_id": data.materia_id, "carrera_id": data.carrera_id, "cohorte_id": data.cohorte_id}

        await self._validate_context(tenant_id, contexto)
        await self._validate_usuarios(data.usuario_ids)

        rol_value = data.rol.value if hasattr(data.rol, "value") else data.rol

        equipo_vigente = await self._repo.find_equipo(
            tenant_id, data.materia_id, data.carrera_id, data.cohorte_id, solo_vigentes=True
        )
        ya_asignados = {
            (row.usuario_id, row.rol) for row in equipo_vigente
        }

        creadas: list[uuid.UUID] = []
        ya_existentes: list[uuid.UUID] = []
        rows_to_create: list[dict] = []
        for usuario_id in data.usuario_ids:
            if (usuario_id, rol_value) in ya_asignados:
                ya_existentes.append(usuario_id)
                continue
            rows_to_create.append({
                "usuario_id": usuario_id,
                "rol": rol_value,
                "materia_id": data.materia_id,
                "carrera_id": data.carrera_id,
                "cohorte_id": data.cohorte_id,
                "desde": data.desde,
                "hasta": data.hasta,
            })
            creadas.append(usuario_id)

        if rows_to_create:
            await self._repo.create_many(rows_to_create)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ASIGNACION_MODIFICAR,
            detalle={
                "operacion": "asignacion_masiva",
                "materia_id": str(data.materia_id),
                "carrera_id": str(data.carrera_id),
                "cohorte_id": str(data.cohorte_id),
                "rol": rol_value,
                "creadas": [str(uid) for uid in creadas],
                "ya_existentes": [str(uid) for uid in ya_existentes],
            },
            filas_afectadas=len(creadas),
            request=request,
        )

        return AsignacionMasivaResultado(
            creadas=creadas,
            ya_existentes=ya_existentes,
            filas_afectadas=len(creadas),
        )

    async def exportar_equipo(
        self,
        contexto: dict,
        current_user: CurrentUser,
    ) -> list[EquipoExportItem]:
        """Armar las filas del export CSV de un equipo (F4.7, D8).

        Una fila por asignación viva del equipo (vigentes y vencidas, sin
        filtrar por `solo_vigentes`), con `docente` resuelto desde `Usuario`
        y `estado_vigencia` derivado (D3). Acotado al tenant del caller: una
        referencia ajena -> `NotFoundException` (404, D4 [SEC], regla dura
        #9). Operación de sólo lectura: no audita (D7).
        """
        tenant_id = current_user.tenant_id

        await self._validate_context(tenant_id, contexto)

        rows = await self._repo.find_equipo(
            tenant_id, contexto["materia_id"], contexto["carrera_id"], contexto["cohorte_id"]
        )

        items: list[EquipoExportItem] = []
        for row in rows:
            usuario = await self._usuario_repo.find_by_id(row.usuario_id)
            docente = f"{usuario.nombre} {usuario.apellidos}" if usuario is not None else ""
            items.append(
                EquipoExportItem(
                    usuario_id=row.usuario_id,
                    docente=docente,
                    rol=row.rol,
                    materia_id=row.materia_id,
                    carrera_id=row.carrera_id,
                    cohorte_id=row.cohorte_id,
                    desde=row.desde,
                    hasta=row.hasta,
                    estado_vigencia=estado_vigencia_for(row),
                )
            )

        return items

    async def modificar_vigencia(
        self,
        data: VigenciaEquipoUpdate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> int:
        """Actualizar `desde`/`hasta` de todas las asignaciones vivas de un
        equipo en bloque (F4.6, D6). Emite UN `ASIGNACION_MODIFICAR` con
        `filas_afectadas`, incluso si el equipo está vacío (0 filas, sin
        error -- D6)."""
        tenant_id = current_user.tenant_id
        contexto = {"materia_id": data.materia_id, "carrera_id": data.carrera_id, "cohorte_id": data.cohorte_id}

        await self._validate_context(tenant_id, contexto)

        filas_afectadas = await self._repo.update_vigencia_equipo(
            tenant_id, contexto, desde=data.desde, hasta=data.hasta
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ASIGNACION_MODIFICAR,
            detalle={
                "operacion": "modificar_vigencia",
                "materia_id": str(data.materia_id),
                "carrera_id": str(data.carrera_id),
                "cohorte_id": str(data.cohorte_id),
                "desde": str(data.desde) if data.desde is not None else None,
                "hasta": str(data.hasta) if data.hasta is not None else None,
            },
            filas_afectadas=filas_afectadas,
            request=request,
        )

        return filas_afectadas

    async def clonar_equipo(
        self,
        data: ClonarEquipoCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> AsignacionMasivaResultado:
        """Clonar las asignaciones VIGENTES de un equipo origen hacia un
        destino (misma materia/carrera, nueva cohorte) con fechas nuevas
        (F4.5, RN-12, D5/D6).

        Preserva `usuario_id`/`rol`/`responsable_id`/`comisiones`. Una
        equivalente (mismo usuario+rol+contexto) ya viva en el destino se
        omite y se reporta (D5). Origen/destino ajenos al tenant ->
        `NotFoundException` (404, abort total). Emite UN
        `ASIGNACION_MODIFICAR`.
        """
        tenant_id = current_user.tenant_id

        await self._validate_context(tenant_id, {
            "materia_id": data.materia_id,
            "carrera_id": data.carrera_id,
        })
        await self._validate_cohortes([data.cohorte_origen_id, data.cohorte_destino_id])

        origen_vigentes = await self._repo.find_equipo(
            tenant_id, data.materia_id, data.carrera_id, data.cohorte_origen_id, solo_vigentes=True
        )
        destino_existentes = await self._repo.find_equipo(
            tenant_id, data.materia_id, data.carrera_id, data.cohorte_destino_id
        )
        ya_presentes = {(row.usuario_id, row.rol) for row in destino_existentes}

        creadas: list[uuid.UUID] = []
        ya_existentes: list[uuid.UUID] = []
        rows_to_create: list[dict] = []
        for asignacion in origen_vigentes:
            if (asignacion.usuario_id, asignacion.rol) in ya_presentes:
                ya_existentes.append(asignacion.usuario_id)
                continue
            rows_to_create.append({
                "usuario_id": asignacion.usuario_id,
                "rol": asignacion.rol,
                "materia_id": data.materia_id,
                "carrera_id": data.carrera_id,
                "cohorte_id": data.cohorte_destino_id,
                "responsable_id": asignacion.responsable_id,
                "comisiones": list(asignacion.comisiones),
                "desde": data.desde,
                "hasta": data.hasta,
            })
            creadas.append(asignacion.usuario_id)

        if rows_to_create:
            await self._repo.create_many(rows_to_create)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.ASIGNACION_MODIFICAR,
            detalle={
                "operacion": "clonar_equipo",
                "materia_id": str(data.materia_id),
                "carrera_id": str(data.carrera_id),
                "cohorte_origen_id": str(data.cohorte_origen_id),
                "cohorte_destino_id": str(data.cohorte_destino_id),
                "creadas": [str(uid) for uid in creadas],
                "ya_existentes": [str(uid) for uid in ya_existentes],
            },
            filas_afectadas=len(creadas),
            request=request,
        )

        return AsignacionMasivaResultado(
            creadas=creadas,
            ya_existentes=ya_existentes,
            filas_afectadas=len(creadas),
        )
