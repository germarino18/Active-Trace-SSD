"""Service for liquidaciones (salary period settlements)."""

import uuid
from decimal import Decimal
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import BusinessRuleViolation, NotFoundException, ValidationException
from app.models.liquidacion import EstadoLiquidacion
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.repositories.clave_plus_repository import ClavePlusRepository
from app.repositories.materia_clave_plus_repository import MateriaClavePlusRepository
from app.repositories.asignacion_repository import AsignacionRepository
from app.schemas.auth import CurrentUser
from app.schemas.liquidaciones import (
    LiquidacionRead,
    LiquidacionPeriodoResponse,
    SegmentoLiquidacion,
    LiquidacionCerrarResponse,
)
from app.services.audit.audit_logger import AuditLogger


class LiquidacionService:
    def __init__(
        self,
        liquidacion_repo: LiquidacionRepository,
        salario_base_repo: SalarioBaseRepository,
        salario_plus_repo: SalarioPlusRepository,
        clave_plus_repo: ClavePlusRepository,
        materia_clave_plus_repo: MateriaClavePlusRepository,
        asignacion_repo: AsignacionRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._liquidacion_repo = liquidacion_repo
        self._salario_base_repo = salario_base_repo
        self._salario_plus_repo = salario_plus_repo
        self._clave_plus_repo = clave_plus_repo
        self._materia_clave_plus_repo = materia_clave_plus_repo
        self._asignacion_repo = asignacion_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "LiquidacionService":
        return cls(
            liquidacion_repo=LiquidacionRepository(session=session, tenant_id=tenant_id),
            salario_base_repo=SalarioBaseRepository(session=session, tenant_id=tenant_id),
            salario_plus_repo=SalarioPlusRepository(session=session, tenant_id=tenant_id),
            clave_plus_repo=ClavePlusRepository(session=session, tenant_id=tenant_id),
            materia_clave_plus_repo=MateriaClavePlusRepository(session=session, tenant_id=tenant_id),
            asignacion_repo=AsignacionRepository(session=session, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def calcular_periodo(
        self,
        periodo: str,
        cohorte_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> LiquidacionPeriodoResponse:
        """Calculate salary settlements for all teachers in a period."""
        año_str, mes_str = periodo.split("-")
        fecha_periodo = date(int(año_str), int(mes_str), 1)

        # Get all active assignments for this cohort
        asignaciones = await self._asignacion_repo.find_by(
            cohorte_id=cohorte_id,
        )
        if not asignaciones:
            return self._empty_response(periodo, cohorte_id)

        # Group by usuario_id to get unique teachers
        docentes_map: dict[uuid.UUID, list] = {}
        for asig in asignaciones:
            uid = asig.usuario_id
            if uid not in docentes_map:
                docentes_map[uid] = []
            docentes_map[uid].append(asig)

        liquidaciones_existentes = await self._liquidacion_repo.find_by_periodo(
            periodo, cohorte_id,
        )
        existing_map: dict[uuid.UUID, LiquidacionRead] = {}
        for liq in liquidaciones_existentes:
            if liq.estado == EstadoLiquidacion.CERRADA.value:
                raise BusinessRuleViolation(
                    message=f"Ya existe una liquidación cerrada para el período {periodo}. "
                    "No se puede recalcular.",
                    code="liquidacion_cerrada_existente",
                )
            existing_map[liq.usuario_id] = liq

        nuevas_liquidaciones = []

        for usuario_id, asignaciones_docente in docentes_map.items():
            rol = asignaciones_docente[0].rol
            es_nexo = (rol == "NEXO")

            # Get from Usuario to check facturador
            from app.repositories.usuario_repository import UsuarioRepository
            usuario_repo = UsuarioRepository(
                session=self._session,
                tenant_id=current_user.tenant_id,
            )
            usuarios = await usuario_repo.find_by(user_id=usuario_id)
            if not usuarios:
                continue
            usuario = usuarios[0]
            excluido_por_factura = bool(usuario.facturador)

            # Find SalarioBase vigente
            base = await self._salario_base_repo.find_vigente_en(rol, fecha_periodo)
            if base is None:
                raise ValidationException(
                    message=f"No hay SalarioBase configurado para el rol {rol} en el período {periodo}",
                    details={"rol": rol, "periodo": periodo},
                )
            monto_base = base.monto

            # Calculate Plus: find materias of this teacher, get ClavePlus for each
            monto_plus = Decimal("0")
            for asig in asignaciones_docente:
                if asig.materia_id is None:
                    continue
                mcp = await self._materia_clave_plus_repo.find_vigente_para_materia(
                    asig.materia_id, fecha_periodo,
                )
                if mcp is None:
                    continue
                plus_list = await self._salario_plus_repo.find_vigentes_en(
                    (await self._get_clave_codigo(mcp.clave_plus_id)) or "",
                    rol,
                    fecha_periodo,
                )
                for plus in plus_list:
                    monto_plus += plus.monto

            total = monto_base + monto_plus

            # Build comisiones string
            comisiones = ",".join(
                str(asig.comisiones) for asig in asignaciones_docente
                if asig.comisiones
            ) or None

            liquidacion_data = {
                "cohorte_id": cohorte_id,
                "periodo": periodo,
                "usuario_id": usuario_id,
                "rol": rol,
                "comisiones": comisiones,
                "monto_base": monto_base,
                "monto_plus": monto_plus,
                "total": total,
                "es_nexo": es_nexo,
                "excluido_por_factura": excluido_por_factura,
                "estado": EstadoLiquidacion.ABIERTA.value,
            }

            # Replace existing open liquidacion
            if usuario_id in existing_map:
                existente = existing_map[usuario_id]
                # Hard delete the existing open one (it's a recalculation)
                await self._liquidacion_repo.hard_delete(existente.id)

            nueva = await self._liquidacion_repo.create(liquidacion_data)
            nuevas_liquidaciones.append(nueva)

        return await self._build_response(periodo, cohorte_id, nuevas_liquidaciones)

    async def cerrar(
        self,
        liquidacion_id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> LiquidacionCerrarResponse:
        """Close a liquidacion (immutable)."""
        liquidacion = await self._liquidacion_repo.find_by_id(liquidacion_id)
        if liquidacion is None:
            raise NotFoundException(resource="Liquidacion", id=liquidacion_id)
        if liquidacion.estado == EstadoLiquidacion.CERRADA.value:
            raise BusinessRuleViolation(
                message="La liquidación ya está cerrada",
                code="liquidacion_ya_cerrada",
            )

        liquidacion.estado = EstadoLiquidacion.CERRADA.value
        await self._session.flush()
        await self._session.refresh(liquidacion)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.LIQUIDACION_CERRAR,
            detalle={
                "liquidacion_id": str(liquidacion_id),
                "usuario_id": str(liquidacion.usuario_id),
                "periodo": liquidacion.periodo,
                "total": str(liquidacion.total),
            },
            filas_afectadas=1,
            request=request,
        )

        return LiquidacionCerrarResponse(
            id=liquidacion.id,
            estado=liquidacion.estado,
            mensaje="Liquidación cerrada correctamente",
        )

    async def obtener_vista_periodo(
        self,
        periodo: str,
        cohorte_id: uuid.UUID,
        usuario_id: uuid.UUID | None = None,
    ) -> LiquidacionPeriodoResponse:
        """Get segmented view of liquidations for a period."""
        liquidaciones = await self._liquidacion_repo.find_by_periodo(periodo, cohorte_id)
        if usuario_id:
            liquidaciones = [l for l in liquidaciones if l.usuario_id == usuario_id]
        return await self._build_response(periodo, cohorte_id, liquidaciones)

    async def obtener_historial(
        self,
        cohorte_id: uuid.UUID | None = None,
        desde: str | None = None,
        hasta: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[LiquidacionRead]:
        """Get history of closed liquidations."""
        liquidaciones = await self._liquidacion_repo.find_historial(
            cohorte_id=cohorte_id,
            desde=desde,
            hasta=hasta,
            skip=skip,
            limit=limit,
        )
        return [LiquidacionRead.model_validate(l) for l in liquidaciones]

    async def _build_response(
        self,
        periodo: str,
        cohorte_id: uuid.UUID,
        liquidaciones,
    ) -> LiquidacionPeriodoResponse:
        general_items = []
        nexo_items = []
        factura_items = []

        for l in liquidaciones:
            read = LiquidacionRead.model_validate(l)
            if l.excluido_por_factura:
                factura_items.append(read)
            elif l.es_nexo:
                nexo_items.append(read)
            else:
                general_items.append(read)

        general_subtotal = sum(l.total for l in general_items) or Decimal("0")
        nexo_subtotal = sum(l.total for l in nexo_items) or Decimal("0")
        factura_subtotal = sum(l.total for l in factura_items) or Decimal("0")

        return LiquidacionPeriodoResponse(
            periodo=periodo,
            cohorte_id=cohorte_id,
            general=SegmentoLiquidacion(items=general_items, subtotal=general_subtotal),
            nexo=SegmentoLiquidacion(items=nexo_items, subtotal=nexo_subtotal),
            factura=SegmentoLiquidacion(items=factura_items, subtotal=factura_subtotal),
            kpis={
                "total_sin_factura": general_subtotal + nexo_subtotal,
                "total_con_factura": factura_subtotal,
            },
        )

    def _empty_response(self, periodo: str, cohorte_id: uuid.UUID) -> LiquidacionPeriodoResponse:
        return LiquidacionPeriodoResponse(
            periodo=periodo,
            cohorte_id=cohorte_id,
            general=SegmentoLiquidacion(items=[], subtotal=Decimal("0")),
            nexo=SegmentoLiquidacion(items=[], subtotal=Decimal("0")),
            factura=SegmentoLiquidacion(items=[], subtotal=Decimal("0")),
            kpis={"total_sin_factura": Decimal("0"), "total_con_factura": Decimal("0")},
        )

    async def _get_clave_codigo(self, clave_plus_id: uuid.UUID) -> str | None:
        cp = await self._clave_plus_repo.find_by_id(clave_plus_id)
        return cp.codigo if cp else None
