from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.dictado_repository import DictadoRepository
from app.repositories.materia_repository import MateriaRepository


# ── CarreraRepository ────────────────────────────────────────────────


async def test_carrera_repo_find_by_codigo_returns_match(
    db_session: AsyncSession, test_tenant
):
    repo = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    found = await repo.find_by_codigo(test_tenant.id, "ING-INF")
    assert found is not None
    assert found.codigo == "ING-INF"


async def test_carrera_repo_find_by_codigo_excludes_soft_deleted(
    db_session: AsyncSession, test_tenant
):
    repo = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    carrera = await repo.create({"codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"})
    await repo.soft_delete(carrera.id)

    found = await repo.find_by_codigo(test_tenant.id, "ING-SIS")
    assert found is None


async def test_carrera_repo_find_by_codigo_scoped_to_tenant(
    db_session: AsyncSession, test_tenant, another_tenant
):
    repo_a = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    await repo_a.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    repo_b = CarreraRepository(session=db_session, tenant_id=another_tenant.id)
    found = await repo_b.find_by_codigo(another_tenant.id, "ING-INF")
    assert found is None


# ── MateriaRepository ─────────────────────────────────────────────────


async def test_materia_repo_find_by_codigo_returns_match(
    db_session: AsyncSession, test_tenant
):
    repo = MateriaRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})

    found = await repo.find_by_codigo(test_tenant.id, "MAT-101")
    assert found is not None
    assert found.codigo == "MAT-101"


async def test_materia_repo_find_by_codigo_returns_none_when_missing(
    db_session: AsyncSession, test_tenant
):
    repo = MateriaRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_codigo(test_tenant.id, "NO-EXISTE")
    assert found is None


# ── CohorteRepository ────────────────────────────────────────────────


async def test_cohorte_repo_find_by_nombre_returns_match(
    db_session: AsyncSession, test_tenant
):
    carrera_repo = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    repo = CohorteRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})

    found = await repo.find_by_nombre(test_tenant.id, carrera.id, "2024")
    assert found is not None
    assert found.nombre == "2024"


async def test_cohorte_repo_find_by_nombre_scoped_to_carrera(
    db_session: AsyncSession, test_tenant
):
    carrera_repo = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    carrera_a = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})
    carrera_b = await carrera_repo.create({"codigo": "ING-SIS", "nombre": "Ingeniería en Sistemas"})

    repo = CohorteRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create({"carrera_id": carrera_a.id, "nombre": "2024", "anio": 2024})

    # Same nombre, different carrera -> no match for carrera_b
    found = await repo.find_by_nombre(test_tenant.id, carrera_b.id, "2024")
    assert found is None


# ── DictadoRepository ────────────────────────────────────────────────


async def test_dictado_repo_find_by_terna_returns_match(
    db_session: AsyncSession, test_tenant
):
    carrera_repo = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    materia_repo = MateriaRepository(session=db_session, tenant_id=test_tenant.id)
    materia = await materia_repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})

    cohorte_repo = CohorteRepository(session=db_session, tenant_id=test_tenant.id)
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})

    repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
    await repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )

    found = await repo.find_by_terna(test_tenant.id, materia.id, carrera.id, cohorte.id)
    assert found is not None
    assert found.materia_id == materia.id


async def test_dictado_repo_find_by_terna_returns_none_when_no_match(
    db_session: AsyncSession, test_tenant
):
    carrera_repo = CarreraRepository(session=db_session, tenant_id=test_tenant.id)
    carrera = await carrera_repo.create({"codigo": "ING-INF", "nombre": "Ingeniería Informática"})

    materia_repo = MateriaRepository(session=db_session, tenant_id=test_tenant.id)
    materia = await materia_repo.create({"codigo": "MAT-101", "nombre": "Análisis Matemático I"})

    cohorte_repo = CohorteRepository(session=db_session, tenant_id=test_tenant.id)
    cohorte = await cohorte_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})

    repo = DictadoRepository(session=db_session, tenant_id=test_tenant.id)
    found = await repo.find_by_terna(test_tenant.id, materia.id, carrera.id, cohorte.id)
    assert found is None
