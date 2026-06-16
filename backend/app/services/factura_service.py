"""Service for facturas (invoices from teachers who invoice)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.exceptions import BusinessRuleViolation, NotFoundException, ValidationException
from app.models.factura import EstadoFactura
from app.repositories.factura_repository import FacturaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import CurrentUser
from app.schemas.facturas import (
    FacturaCreate,
    FacturaRead,
    FacturaListParams,
    FacturaAbonarResponse,
)
from app.services.audit.audit_logger import AuditLogger
from app.repositories.audit_log_repository import AuditLogRepository
from app.core.acciones_auditoria import AccionAuditoria


class FacturaService:
    def __init__(
        self,
        factura_repo: FacturaRepository,
        usuario_repo: UsuarioRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._factura_repo = factura_repo
        self._usuario_repo = usuario_repo
        self._audit = AuditLogger(repository=audit_repo)
        self._session = session

    @classmethod
    def create(cls, session: AsyncSession, tenant_id: uuid.UUID) -> "FacturaService":
        return cls(
            factura_repo=FacturaRepository(session=session, tenant_id=tenant_id),
            usuario_repo=UsuarioRepository(session=session, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=session, tenant_id=tenant_id),
            session=session,
        )

    async def crear(
        self,
        data: FacturaCreate,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> FacturaRead:
        # Validate user exists and is facturador
        # NOTE: data.usuario_id is the User.id (auth user PK), not Usuario.id.
        # We look up Usuario by user_id FK first, then use the actual
        # Usuario.id for the factura FK constraint.
        usuarios = await self._usuario_repo.find_by(user_id=data.usuario_id)
        if not usuarios:
            raise NotFoundException(resource="Usuario", id=data.usuario_id)
        usuario = usuarios[0]
        if not usuario.facturador:
            raise ValidationException(
                message="El usuario no está configurado como facturador",
                details={"usuario_id": str(data.usuario_id)},
            )

        # Build create data with the actual Usuario.id for the FK constraint
        create_data = data.model_dump()
        create_data["usuario_id"] = usuario.id
        factura = await self._factura_repo.create(create_data)
        return FacturaRead.model_validate(factura)

    async def listar(
        self, params: FacturaListParams,
    ) -> list[FacturaRead]:
        facturas = await self._factura_repo.find_filtered(
            usuario_id=params.usuario_id,
            periodo=params.periodo,
            estado=params.estado,
            desde=params.desde,
            hasta=params.hasta,
            skip=params.skip,
            limit=params.limit,
        )
        return [FacturaRead.model_validate(f) for f in facturas]

    async def obtener(self, id: uuid.UUID) -> FacturaRead:
        factura = await self._factura_repo.find_by_id(id)
        if factura is None:
            raise NotFoundException(resource="Factura", id=id)
        return FacturaRead.model_validate(factura)

    async def actualizar(
        self,
        id: uuid.UUID,
        data: dict,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> FacturaRead:
        factura = await self._factura_repo.find_by_id(id)
        if factura is None:
            raise NotFoundException(resource="Factura", id=id)
        if factura.estado == EstadoFactura.ABONADA.value:
            raise BusinessRuleViolation(
                message="No se puede modificar una factura ya abonada",
                code="factura_abonada",
            )
        updated = await self._factura_repo.update(id, data)
        return FacturaRead.model_validate(updated)

    async def abonar(
        self,
        id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> FacturaAbonarResponse:
        factura = await self._factura_repo.find_by_id(id)
        if factura is None:
            raise NotFoundException(resource="Factura", id=id)
        if factura.estado == EstadoFactura.ABONADA.value:
            raise BusinessRuleViolation(
                message="La factura ya está abonada",
                code="factura_ya_abonada",
            )

        factura.estado = EstadoFactura.ABONADA.value
        factura.abonada_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.refresh(factura)

        return FacturaAbonarResponse(
            id=factura.id,
            estado=factura.estado,
            abonada_at=factura.abonada_at,
            mensaje="Factura abonada correctamente",
        )

    async def eliminar(
        self,
        id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> None:
        factura = await self._factura_repo.find_by_id(id)
        if factura is None:
            raise NotFoundException(resource="Factura", id=id)
        if factura.estado == EstadoFactura.ABONADA.value:
            raise BusinessRuleViolation(
                message="No se puede eliminar una factura ya abonada",
                code="factura_abonada",
            )
        await self._factura_repo.soft_delete(id)
