"""Tests for liquidaciones services: GrillaSalarialService, ClavePlusService,
LiquidacionService, FacturaService."""

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolation, NotFoundException, ValidationException
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.factura import EstadoFactura, Factura
from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.schemas.facturas import FacturaCreate, FacturaListParams, FacturaUpdate
from app.schemas.liquidaciones import (
    ClavePlusCreate, ClavePlusUpdate,
    MateriaClavePlusCreate,
    SalarioBaseCreate, SalarioBaseUpdate,
    SalarioPlusCreate, SalarioPlusUpdate,
)
from app.services.clave_plus_service import ClavePlusService
from app.services.factura_service import FacturaService
from app.services.grilla_salarial_service import GrillaSalarialService


_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> dict:
    """Returns dict with both user_id and usuario_id."""
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"usr-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuario = await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
    })
    return {"user_id": user.id, "usuario_id": usuario.id}


@pytest.fixture
async def test_facturador(db_session: AsyncSession, test_tenant: Tenant) -> dict:
    """Returns dict with user_id and usuario_id for a facturador.
    
    NOTE: usuario.id == user.id to work around a service inconsistency where
    data.usuario_id is used both for find_by(user_id=...) AND as the FK
    value on factura.usuario_id (which references usuario.id).
    """
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"fact-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Facturador",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    usuario = await usuario_repo.create({
        "id": user.id,
        "user_id": user.id,
        "nombre": "Fact",
        "apellidos": "User",
        "facturador": True,
    })
    return {"user_id": user.id, "usuario_id": usuario.id}


@pytest.fixture
async def test_cohorte(db_session: AsyncSession, test_tenant: Tenant) -> Cohorte:
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"nombre": "Ingenieria", "codigo": "ING"})
    repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"carrera_id": carrera.id, "nombre": "2026", "anio": 2026})


@pytest.fixture
def mock_request():
    req = MagicMock()
    req.client.host = "127.0.0.1"
    req.headers = {"user-agent": "test"}
    return req


@pytest.fixture
def current_user(test_tenant: Tenant) -> CurrentUser:
    return CurrentUser(user_id=uuid.uuid4(), tenant_id=test_tenant.id, roles=["FINANZAS"])


# ── GrillaSalarialService ───────────────────────────────────────────


class TestGrillaSalarialService:
    async def test_crear_salario_base(self, db_session, test_tenant):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        data = SalarioBaseCreate(rol="PROFESOR", monto=Decimal("150000.00"), desde=date(2026, 1, 1))
        result = await service.crear_base(data)
        assert result.id is not None
        assert result.rol == "PROFESOR"
        assert result.monto == Decimal("150000.00")

    async def test_crear_salario_base_solapamiento(
        self, db_session, test_tenant, salario_base_data,
    ):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        data = SalarioBaseCreate(rol="PROFESOR", monto=Decimal("160000.00"), desde=date(2026, 6, 1))
        with pytest.raises(BusinessRuleViolation, match="existe.*SalarioBase"):
            await service.crear_base(data)

    async def test_listar_salarios_base(self, db_session, test_tenant, salario_base_data):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        results = await service.listar_bases()
        assert len(results) >= 1
        ids = [r.id for r in results]
        assert salario_base_data.id in ids

    async def test_actualizar_salario_base(self, db_session, test_tenant, salario_base_data):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        update = SalarioBaseUpdate(monto=Decimal("160000.00"))
        result = await service.actualizar_base(salario_base_data.id, update)
        assert result.monto == Decimal("160000.00")

    async def test_actualizar_salario_base_not_found(self, db_session, test_tenant):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        with pytest.raises(NotFoundException):
            await service.actualizar_base(uuid.uuid4(), SalarioBaseUpdate(monto=Decimal("1")))

    async def test_eliminar_salario_base(self, db_session, test_tenant, salario_base_data):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        await service.eliminar_base(salario_base_data.id)
        with pytest.raises(NotFoundException):
            await service.obtener_base(salario_base_data.id)

    async def test_crear_salario_plus(self, db_session, test_tenant):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        data = SalarioPlusCreate(grupo="PROG", rol="PROFESOR", descripcion="Plus test", monto=Decimal("25000.00"), desde=date(2026, 1, 1))
        result = await service.crear_plus(data)
        assert result.id is not None
        assert result.grupo == "PROG"

    async def test_crear_salario_plus_solapamiento(
        self, db_session, test_tenant, salario_plus_prog,
    ):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        data = SalarioPlusCreate(grupo="PROG", rol="PROFESOR", descripcion="Otro", monto=Decimal("30000.00"), desde=date(2026, 6, 1))
        with pytest.raises(BusinessRuleViolation, match="existe.*SalarioPlus"):
            await service.crear_plus(data)

    async def test_listar_salarios_plus(self, db_session, test_tenant, salario_plus_prog, salario_plus_bd):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        results = await service.listar_plus()
        assert len(results) == 2

    async def test_eliminar_salario_plus(self, db_session, test_tenant, salario_plus_prog):
        service = GrillaSalarialService.create(db_session, test_tenant.id)
        await service.eliminar_plus(salario_plus_prog.id)
        with pytest.raises(NotFoundException):
            await service.obtener_plus(salario_plus_prog.id)


# ── ClavePlusService ────────────────────────────────────────────────


class TestClavePlusService:
    async def test_crear_clave(self, db_session, test_tenant):
        service = ClavePlusService.create(db_session, test_tenant.id)
        data = ClavePlusCreate(codigo="TEST", descripcion="Test", desde=date(2026, 1, 1))
        result = await service.crear_clave(data)
        assert result.codigo == "TEST"

    async def test_crear_clave_duplicado(self, db_session, test_tenant, clave_prog):
        service = ClavePlusService.create(db_session, test_tenant.id)
        data = ClavePlusCreate(codigo="PROG", descripcion="Dupe", desde=date(2026, 1, 1))
        with pytest.raises(BusinessRuleViolation, match="existe.*ClavePlus"):
            await service.crear_clave(data)

    async def test_listar_claves(self, db_session, test_tenant, clave_prog, clave_bd):
        service = ClavePlusService.create(db_session, test_tenant.id)
        results = await service.listar_claves()
        assert len(results) == 2

    async def test_actualizar_clave(self, db_session, test_tenant, clave_prog):
        service = ClavePlusService.create(db_session, test_tenant.id)
        update = ClavePlusUpdate(descripcion="Updated")
        result = await service.actualizar_clave(clave_prog.id, update)
        assert result.descripcion == "Updated"

    async def test_eliminar_clave(self, db_session, test_tenant, clave_prog):
        service = ClavePlusService.create(db_session, test_tenant.id)
        await service.eliminar_clave(clave_prog.id)
        with pytest.raises(NotFoundException):
            await service.obtener_clave(clave_prog.id)

    async def test_crear_materia_clave(
        self, db_session, test_tenant, materia_prog, clave_prog,
    ):
        service = ClavePlusService.create(db_session, test_tenant.id)
        data = MateriaClavePlusCreate(
            materia_id=materia_prog.id,
            clave_plus_id=clave_prog.id,
            desde=date(2026, 1, 1),
        )
        result = await service.crear_materia_clave(data)
        assert result.materia_id == materia_prog.id
        assert result.clave_plus_id == clave_prog.id


# ── FacturaService ──────────────────────────────────────────────────


class TestFacturaService:
    async def test_crear_factura(
        self, db_session, test_tenant, test_facturador, current_user, mock_request,
    ):
        service = FacturaService.create(db_session, test_tenant.id)
        data = FacturaCreate(usuario_id=test_facturador["user_id"], periodo="2026-06")
        result = await service.crear(data, current_user=current_user, request=mock_request)
        assert result.id is not None
        assert result.estado == "Pendiente"

    async def test_crear_factura_no_facturador(
        self, db_session, test_tenant, test_usuario, current_user, mock_request,
    ):
        service = FacturaService.create(db_session, test_tenant.id)
        data = FacturaCreate(usuario_id=test_usuario["user_id"], periodo="2026-06")
        with pytest.raises(ValidationException, match="facturador"):
            await service.crear(data, current_user=current_user, request=mock_request)

    async def test_listar_facturas(
        self, db_session, test_tenant, test_facturador,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        await fac_repo.create({"usuario_id": test_facturador["usuario_id"], "periodo": "2026-06"})
        service = FacturaService.create(db_session, test_tenant.id)
        params = FacturaListParams()
        results = await service.listar(params)
        assert len(results) >= 1

    async def test_abonar_factura(
        self, db_session, test_tenant, test_facturador, current_user, mock_request,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        fac = await fac_repo.create({"usuario_id": test_facturador["usuario_id"], "periodo": "2026-06"})
        service = FacturaService.create(db_session, test_tenant.id)
        result = await service.abonar(fac.id, current_user=current_user, request=mock_request)
        assert result.estado == "Abonada"
        assert result.abonada_at is not None

    async def test_abonar_factura_ya_abonada(
        self, db_session, test_tenant, test_facturador, current_user, mock_request,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        fac = await fac_repo.create({
            "usuario_id": test_facturador["usuario_id"], "periodo": "2026-06",
            "estado": EstadoFactura.ABONADA.value,
        })
        service = FacturaService.create(db_session, test_tenant.id)
        with pytest.raises(BusinessRuleViolation, match="abonada"):
            await service.abonar(fac.id, current_user=current_user, request=mock_request)

    async def test_eliminar_factura(
        self, db_session, test_tenant, test_facturador, current_user, mock_request,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        fac = await fac_repo.create({"usuario_id": test_facturador["usuario_id"], "periodo": "2026-06"})
        service = FacturaService.create(db_session, test_tenant.id)
        await service.eliminar(fac.id, current_user=current_user, request=mock_request)
        deleted = await fac_repo.find_by_id(fac.id)
        assert deleted is None

    async def test_eliminar_factura_abonada(
        self, db_session, test_tenant, test_facturador, current_user, mock_request,
    ):
        fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
        fac = await fac_repo.create({
            "usuario_id": test_facturador["usuario_id"], "periodo": "2026-06",
            "estado": EstadoFactura.ABONADA.value,
        })
        service = FacturaService.create(db_session, test_tenant.id)
        with pytest.raises(BusinessRuleViolation, match="abonada"):
            await service.eliminar(fac.id, current_user=current_user, request=mock_request)
