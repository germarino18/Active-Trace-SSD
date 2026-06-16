"""Tests for liquidaciones repositories."""

from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clave_plus import ClavePlus
from app.models.cohorte import Cohorte
from app.models.factura import EstadoFactura, Factura
from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.models.materia_clave_plus import MateriaClavePlus
from app.models.salario_base import SalarioBase
from app.models.salario_plus import SalarioPlus
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.models.carrera import Carrera
from app.repositories.base import BaseRepository
from app.repositories.clave_plus_repository import ClavePlusRepository
from app.repositories.factura_repository import FacturaRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.materia_clave_plus_repository import MateriaClavePlusRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository


@pytest.fixture
async def test_usuario(db_session: AsyncSession, test_tenant: Tenant) -> Usuario:
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=test_tenant.id)
    user = await user_repo.create({
        "email": f"usr-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "Test User",
    })
    usuario_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=test_tenant.id)
    return await usuario_repo.create({
        "user_id": user.id,
        "nombre": "Test",
        "apellidos": "User",
    })


@pytest.fixture
async def test_cohorte(db_session: AsyncSession, test_tenant: Tenant) -> Cohorte:
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"nombre": "Ingenieria", "codigo": "ING"})
    repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"carrera_id": carrera.id, "nombre": "2026", "anio": 2026})


@pytest.mark.asyncio
async def test_salario_base_find_vigente_en(
    db_session: AsyncSession, test_tenant: Tenant, salario_base_data: SalarioBase,
):
    repo = SalarioBaseRepository(session=db_session, tenant_id=test_tenant.id)
    result = await repo.find_vigente_en("PROFESOR", date(2026, 6, 1))
    assert result is not None
    assert result.id == salario_base_data.id
    assert result.monto == Decimal("150000.00")

    # Should NOT find for a different role
    no_result = await repo.find_vigente_en("COORDINADOR", date(2026, 6, 1))
    assert no_result is None

    # Should NOT find before desde
    no_result2 = await repo.find_vigente_en("PROFESOR", date(2025, 12, 31))
    assert no_result2 is None


@pytest.mark.asyncio
async def test_salario_base_check_solapamiento(
    db_session: AsyncSession, test_tenant: Tenant, salario_base_data: SalarioBase,
):
    repo = SalarioBaseRepository(session=db_session, tenant_id=test_tenant.id)

    # Overlapping period (same rol, overlapping dates)
    has_overlap = await repo.check_solapamiento("PROFESOR", date(2026, 3, 1), None)
    assert has_overlap is True

    # Non-overlapping (different rol)
    no_overlap = await repo.check_solapamiento("TUTOR", date(2026, 3, 1), None)
    assert no_overlap is False

    # Exclude self
    excluded = await repo.check_solapamiento(
        "PROFESOR", date(2026, 3, 1), None, exclude_id=salario_base_data.id,
    )
    # The existing entry IS overlapping, but we exclude it by id
    assert excluded is False


@pytest.mark.asyncio
async def test_salario_plus_find_vigentes_en(
    db_session: AsyncSession, test_tenant: Tenant, salario_plus_prog: SalarioPlus,
):
    repo = SalarioPlusRepository(session=db_session, tenant_id=test_tenant.id)
    results = await repo.find_vigentes_en("PROG", "PROFESOR", date(2026, 6, 1))
    assert len(results) == 1
    assert results[0].id == salario_plus_prog.id

    # Wrong group → empty (no BD salario_plus loaded in this test)
    no_results = await repo.find_vigentes_en("BD", "PROFESOR", date(2026, 6, 1))
    assert len(no_results) == 0


@pytest.mark.asyncio
async def test_salario_plus_check_solapamiento(
    db_session: AsyncSession, test_tenant: Tenant, salario_plus_prog: SalarioPlus,
):
    repo = SalarioPlusRepository(session=db_session, tenant_id=test_tenant.id)

    has_overlap = await repo.check_solapamiento("PROG", "PROFESOR", date(2026, 3, 1), None)
    assert has_overlap is True

    no_overlap = await repo.check_solapamiento("PROG", "TUTOR", date(2026, 3, 1), None)
    assert no_overlap is False

    excluded = await repo.check_solapamiento(
        "PROG", "PROFESOR", date(2026, 3, 1), None, exclude_id=salario_plus_prog.id,
    )
    assert excluded is False


@pytest.mark.asyncio
async def test_clave_plus_find_by_codigo(
    db_session: AsyncSession, test_tenant: Tenant, clave_prog: ClavePlus,
):
    repo = ClavePlusRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_codigo("PROG")
    assert found is not None
    assert found.id == clave_prog.id

    not_found = await repo.find_by_codigo("NONEXISTENT")
    assert not_found is None


@pytest.mark.asyncio
async def test_clave_plus_find_vigentes_en(
    db_session: AsyncSession, test_tenant: Tenant, clave_prog: ClavePlus, clave_bd: ClavePlus,
):
    repo = ClavePlusRepository(session=db_session, tenant_id=test_tenant.id)
    results = await repo.find_vigentes_en(date(2026, 6, 1))
    assert len(results) == 2

    results_past = await repo.find_vigentes_en(date(2025, 12, 31))
    assert len(results_past) == 0


@pytest.mark.asyncio
async def test_materia_clave_plus_find_vigente_para_materia(
    db_session: AsyncSession, test_tenant: Tenant,
    materia_prog, clave_prog, materia_clave_prog: MateriaClavePlus,
):
    repo = MateriaClavePlusRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_vigente_para_materia(materia_prog.id, date(2026, 6, 1))
    assert found is not None
    assert found.id == materia_clave_prog.id

    not_found = await repo.find_vigente_para_materia(materia_prog.id, date(2025, 12, 31))
    assert not_found is None


@pytest.mark.asyncio
async def test_liquidacion_find_by_periodo(
    db_session: AsyncSession, test_tenant: Tenant,
    test_usuario: Usuario, test_cohorte: Cohorte,
):
    liq_repo = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    await liq_repo.create({
        "cohorte_id": test_cohorte.id, "periodo": "2026-06",
        "usuario_id": test_usuario.id, "rol": "PROFESOR",
        "monto_base": Decimal("150000.00"), "monto_plus": Decimal("0"),
        "total": Decimal("150000.00"),
    })
    repo = LiquidacionRepository(session=db_session, tenant_id=test_tenant.id)
    results = await repo.find_by_periodo("2026-06", test_cohorte.id)
    assert len(results) == 1

    no_results = await repo.find_by_periodo("2026-07", test_cohorte.id)
    assert len(no_results) == 0


@pytest.mark.asyncio
async def test_liquidacion_find_historial(
    db_session: AsyncSession, test_tenant: Tenant,
    test_usuario: Usuario, test_cohorte: Cohorte,
):
    liq_repo = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    await liq_repo.create({
        "cohorte_id": test_cohorte.id, "periodo": "2026-05",
        "usuario_id": test_usuario.id, "rol": "PROFESOR",
        "monto_base": Decimal("150000.00"), "monto_plus": Decimal("0"),
        "total": Decimal("150000.00"), "estado": EstadoLiquidacion.CERRADA.value,
    })
    repo = LiquidacionRepository(session=db_session, tenant_id=test_tenant.id)
    results = await repo.find_historial()
    assert len(results) == 1

    results_empty = await repo.find_historial(desde="2026-06")
    assert len(results_empty) == 0


@pytest.mark.asyncio
async def test_liquidacion_find_abiertas_por_periodo(
    db_session: AsyncSession, test_tenant: Tenant,
    test_usuario: Usuario, test_cohorte: Cohorte,
):
    liq_repo = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    await liq_repo.create({
        "cohorte_id": test_cohorte.id, "periodo": "2026-06",
        "usuario_id": test_usuario.id, "rol": "PROFESOR",
        "monto_base": Decimal("150000.00"), "monto_plus": Decimal("0"),
        "total": Decimal("150000.00"), "estado": EstadoLiquidacion.ABIERTA.value,
    })
    await liq_repo.create({
        "cohorte_id": test_cohorte.id, "periodo": "2026-06",
        "usuario_id": test_usuario.id, "rol": "TUTOR",
        "monto_base": Decimal("80000.00"), "monto_plus": Decimal("0"),
        "total": Decimal("80000.00"), "estado": EstadoLiquidacion.CERRADA.value,
    })
    repo = LiquidacionRepository(session=db_session, tenant_id=test_tenant.id)
    results = await repo.find_abiertas_por_periodo("2026-06", test_cohorte.id)
    assert len(results) == 1
    assert results[0].rol == "PROFESOR"


@pytest.mark.asyncio
async def test_factura_find_filtered(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario,
):
    fac_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
    await fac_repo.create({
        "usuario_id": test_usuario.id, "periodo": "2026-06",
        "estado": EstadoFactura.PENDIENTE.value,
    })
    repo = FacturaRepository(session=db_session, tenant_id=test_tenant.id)

    all_fac = await repo.find_filtered()
    assert len(all_fac) == 1

    filtered_by_estado = await repo.find_filtered(estado="Pendiente")
    assert len(filtered_by_estado) == 1

    filtered_by_estado_wrong = await repo.find_filtered(estado="Abonada")
    assert len(filtered_by_estado_wrong) == 0

    filtered_by_periodo = await repo.find_filtered(periodo="2026-06")
    assert len(filtered_by_periodo) == 1
