"""Fixtures for liquidaciones tests.

Defines entities that are shared across all liquidacion test files.
Per-file fixtures (test_usuario, test_cohorte, etc.) live in each test file.
"""

from datetime import date, UTC
from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clave_plus import ClavePlus
from app.models.materia import Materia
from app.models.materia_clave_plus import MateriaClavePlus
from app.models.salario_base import SalarioBase
from app.models.salario_plus import SalarioPlus
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


@pytest_asyncio.fixture
async def salario_base_data(db_session: AsyncSession, test_tenant: Tenant) -> SalarioBase:
    repo = BaseRepository(model=SalarioBase, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "rol": "PROFESOR",
        "monto": Decimal("150000.00"),
        "desde": date(2026, 1, 1),
        "hasta": None,
    })


@pytest_asyncio.fixture
async def salario_base_tutor(db_session: AsyncSession, test_tenant: Tenant) -> SalarioBase:
    repo = BaseRepository(model=SalarioBase, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "rol": "TUTOR",
        "monto": Decimal("80000.00"),
        "desde": date(2026, 1, 1),
        "hasta": None,
    })


@pytest_asyncio.fixture
async def clave_prog(db_session: AsyncSession, test_tenant: Tenant) -> ClavePlus:
    repo = BaseRepository(model=ClavePlus, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "codigo": "PROG",
        "descripcion": "Materias de Programación",
        "desde": date(2026, 1, 1),
        "hasta": None,
    })


@pytest_asyncio.fixture
async def clave_bd(db_session: AsyncSession, test_tenant: Tenant) -> ClavePlus:
    repo = BaseRepository(model=ClavePlus, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "codigo": "BD",
        "descripcion": "Materias de Base de Datos",
        "desde": date(2026, 1, 1),
        "hasta": None,
    })


@pytest_asyncio.fixture
async def salario_plus_prog(
    db_session: AsyncSession, test_tenant: Tenant, clave_prog: ClavePlus,
) -> SalarioPlus:
    repo = BaseRepository(model=SalarioPlus, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "grupo": "PROG",
        "rol": "PROFESOR",
        "descripcion": "Plus Programación",
        "monto": Decimal("25000.00"),
        "desde": date(2026, 1, 1),
        "hasta": None,
    })


@pytest_asyncio.fixture
async def salario_plus_bd(
    db_session: AsyncSession, test_tenant: Tenant, clave_bd: ClavePlus,
) -> SalarioPlus:
    repo = BaseRepository(model=SalarioPlus, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "grupo": "BD",
        "rol": "PROFESOR",
        "descripcion": "Plus Base de Datos",
        "monto": Decimal("20000.00"),
        "desde": date(2026, 1, 1),
        "hasta": None,
    })


@pytest_asyncio.fixture
async def materia_prog(db_session: AsyncSession, test_tenant: Tenant) -> Materia:
    repo = BaseRepository(model=Materia, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "codigo": "PROG_I",
        "nombre": "Programación I",
        "estado": "Activa",
    })


@pytest_asyncio.fixture
async def materia_clave_prog(
    db_session: AsyncSession,
    test_tenant: Tenant,
    materia_prog: Materia,
    clave_prog: ClavePlus,
) -> MateriaClavePlus:
    repo = BaseRepository(model=MateriaClavePlus, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({
        "materia_id": materia_prog.id,
        "clave_plus_id": clave_prog.id,
        "desde": date(2026, 1, 1),
        "hasta": None,
    })
