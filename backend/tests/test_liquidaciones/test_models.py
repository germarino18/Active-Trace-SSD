"""Tests for liquidaciones models: SalarioBase, SalarioPlus, ClavePlus,
MateriaClavePlus, Liquidacion, Factura."""

from datetime import date
from decimal import Decimal
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.factura import EstadoFactura, Factura
from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.models.clave_plus import ClavePlus
from app.models.materia_clave_plus import MateriaClavePlus
from app.models.salario_base import SalarioBase
from app.models.salario_plus import SalarioPlus
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
async def test_cohorte(db_session: AsyncSession, test_tenant: Tenant) -> Cohorte:
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"nombre": "Ingenieria", "codigo": "ING"})
    repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=test_tenant.id)
    return await repo.create({"carrera_id": carrera.id, "nombre": "2026", "anio": 2026})


@pytest.mark.asyncio
async def test_create_salario_base(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=SalarioBase, session=db_session, tenant_id=test_tenant.id)
    sb = await repo.create({
        "rol": "PROFESOR",
        "monto": Decimal("150000.00"),
        "desde": date(2026, 1, 1),
    })
    assert sb.id is not None
    assert sb.rol == "PROFESOR"
    assert sb.monto == Decimal("150000.00")
    assert sb.desde == date(2026, 1, 1)
    assert sb.hasta is None
    assert sb.deleted_at is None


@pytest.mark.asyncio
async def test_create_salario_plus(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=SalarioPlus, session=db_session, tenant_id=test_tenant.id)
    sp = await repo.create({
        "grupo": "PROG",
        "rol": "TUTOR",
        "descripcion": "Plus test",
        "monto": Decimal("10000.00"),
        "desde": date(2026, 1, 1),
    })
    assert sp.id is not None
    assert sp.grupo == "PROG"
    assert sp.rol == "TUTOR"
    assert sp.monto == Decimal("10000.00")


@pytest.mark.asyncio
async def test_create_clave_plus(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=ClavePlus, session=db_session, tenant_id=test_tenant.id)
    cp = await repo.create({
        "codigo": "TEST",
        "descripcion": "Test clave",
        "desde": date(2026, 1, 1),
    })
    assert cp.id is not None
    assert cp.codigo == "TEST"
    assert cp.descripcion == "Test clave"


@pytest.mark.asyncio
async def test_create_materia_clave_plus(
    db_session: AsyncSession, test_tenant: Tenant, materia_prog, clave_prog,
):
    repo = BaseRepository(model=MateriaClavePlus, session=db_session, tenant_id=test_tenant.id)
    mcp = await repo.create({
        "materia_id": materia_prog.id,
        "clave_plus_id": clave_prog.id,
        "desde": date(2026, 1, 1),
    })
    assert mcp.id is not None
    assert mcp.materia_id == materia_prog.id
    assert mcp.clave_plus_id == clave_prog.id


@pytest.mark.asyncio
async def test_create_liquidacion_abierta(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario, test_cohorte: Cohorte,
):
    repo = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    liq = await repo.create({
        "cohorte_id": test_cohorte.id,
        "periodo": "2026-06",
        "usuario_id": test_usuario.id,
        "rol": "PROFESOR",
        "monto_base": Decimal("150000.00"),
        "monto_plus": Decimal("0"),
        "total": Decimal("150000.00"),
        "estado": EstadoLiquidacion.ABIERTA.value,
    })
    assert liq.id is not None
    assert liq.periodo == "2026-06"
    assert liq.estado == "Abierta"
    assert liq.es_nexo is False
    assert liq.excluido_por_factura is False


@pytest.mark.asyncio
async def test_create_liquidacion_cerrada(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario, test_cohorte: Cohorte,
):
    repo = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    liq = await repo.create({
        "cohorte_id": test_cohorte.id,
        "periodo": "2026-05",
        "usuario_id": test_usuario.id,
        "rol": "TUTOR",
        "monto_base": Decimal("80000.00"),
        "monto_plus": Decimal("5000.00"),
        "total": Decimal("85000.00"),
        "estado": EstadoLiquidacion.CERRADA.value,
    })
    assert liq.estado == "Cerrada"
    assert liq.total == Decimal("85000.00")


@pytest.mark.asyncio
async def test_create_factura_pendiente(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario,
):
    repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
    fac = await repo.create({
        "usuario_id": test_usuario.id,
        "periodo": "2026-06",
        "estado": EstadoFactura.PENDIENTE.value,
    })
    assert fac.id is not None
    assert fac.estado == "Pendiente"
    assert fac.abonada_at is None


@pytest.mark.asyncio
async def test_create_factura_abonada(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario,
):
    from datetime import UTC, datetime
    repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
    fac = await repo.create({
        "usuario_id": test_usuario.id,
        "periodo": "2026-06",
        "estado": EstadoFactura.ABONADA.value,
        "abonada_at": datetime.now(UTC),
    })
    assert fac.estado == "Abonada"
    assert fac.abonada_at is not None


@pytest.mark.asyncio
async def test_unique_clave_plus_codigo(db_session: AsyncSession, test_tenant: Tenant):
    repo = BaseRepository(model=ClavePlus, session=db_session, tenant_id=test_tenant.id)
    await repo.create({"codigo": "UNICO", "descripcion": "First", "desde": date(2026, 1, 1)})
    with pytest.raises(Exception):  # unique constraint violation
        await repo.create({"codigo": "UNICO", "descripcion": "Second", "desde": date(2026, 2, 1)})


@pytest.mark.asyncio
async def test_soft_delete_liquidacion(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario, test_cohorte: Cohorte,
):
    repo = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    liq = await repo.create({
        "cohorte_id": test_cohorte.id,
        "periodo": "2026-06",
        "usuario_id": test_usuario.id,
        "rol": "PROFESOR",
        "monto_base": Decimal("100000.00"),
        "monto_plus": Decimal("0"),
        "total": Decimal("100000.00"),
    })
    assert liq.deleted_at is None
    deleted = await repo.soft_delete(liq.id)
    assert deleted.deleted_at is not None
    not_found = await repo.find_by_id(liq.id)
    assert not_found is None


@pytest.mark.asyncio
async def test_multi_tenant_isolation_liquidacion(
    db_session: AsyncSession, test_tenant: Tenant, another_tenant: Tenant,
    test_usuario: Usuario, test_cohorte: Cohorte,
):
    repo1 = BaseRepository(model=Liquidacion, session=db_session, tenant_id=test_tenant.id)
    repo2 = BaseRepository(model=Liquidacion, session=db_session, tenant_id=another_tenant.id)

    liq1 = await repo1.create({
        "cohorte_id": test_cohorte.id,
        "periodo": "2026-06",
        "usuario_id": test_usuario.id,
        "rol": "PROFESOR",
        "monto_base": Decimal("100000.00"),
        "monto_plus": Decimal("0"),
        "total": Decimal("100000.00"),
    })
    # Create 2nd tenant's cohorte + usuario
    carrera_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=another_tenant.id)
    carrera2 = await carrera_repo.create({"nombre": "Arquitectura", "codigo": "ARQ"})
    cohorte_repo2 = BaseRepository(model=Cohorte, session=db_session, tenant_id=another_tenant.id)
    cohorte2 = await cohorte_repo2.create({"carrera_id": carrera2.id, "nombre": "2026", "anio": 2026})
    user_repo2 = BaseRepository(model=User, session=db_session, tenant_id=another_tenant.id)
    user2 = await user_repo2.create({
        "email": f"usr2-{uuid.uuid4().hex[:8]}@test.com",
        "password_hash": "hash",
        "display_name": "User 2",
    })
    usuario_repo2 = BaseRepository(model=Usuario, session=db_session, tenant_id=another_tenant.id)
    usuario2 = await usuario_repo2.create({"user_id": user2.id, "nombre": "Otro", "apellidos": "User"})
    liq2 = await repo2.create({
        "cohorte_id": cohorte2.id,
        "periodo": "2026-06",
        "usuario_id": usuario2.id,
        "rol": "TUTOR",
        "monto_base": Decimal("80000.00"),
        "monto_plus": Decimal("0"),
        "total": Decimal("80000.00"),
    })
    t1_all = await repo1.find_all()
    t2_all = await repo2.find_all()
    assert len(t1_all) == 1
    assert len(t2_all) == 1
    assert t1_all[0].id == liq1.id
    assert t2_all[0].id == liq2.id


@pytest.mark.asyncio
async def test_factura_relation_liquidacion(
    db_session: AsyncSession, test_tenant: Tenant, test_usuario: Usuario,
):
    factura_repo = BaseRepository(model=Factura, session=db_session, tenant_id=test_tenant.id)
    fac = await factura_repo.create({
        "usuario_id": test_usuario.id,
        "periodo": "2026-06",
    })
    assert fac.usuario_id == test_usuario.id
    assert fac.periodo == "2026-06"
    assert fac.detalle is None
    assert fac.referencia_archivo is None
    assert fac.tamano_kb is None
