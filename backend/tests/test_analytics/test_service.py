"""Tests for AnalyticsService."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository
from app.schemas.auth import CurrentUser
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def service(db_session: AsyncSession, test_tenant: Tenant) -> AnalyticsService:
    return AnalyticsService(db_session, test_tenant.id)


class TestGetAtrasadosPorCohorte:
    async def test_returns_atrasados_grouped(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_entrada_padron_2,
        test_dictado,
    ):
        """Given 1 atrasado and 1 no-atrasado, returns correct counts."""
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        # Atrasado
        await repo.create({
            "entrada_padron_id": test_entrada_padron.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("2.0"),
            "aprobado": False,
        })
        # No atrasado
        await repo.create({
            "entrada_padron_id": test_entrada_padron_2.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("8.0"),
            "aprobado": True,
        })

        result = await service.get_atrasados_por_cohorte()
        assert len(result) >= 1
        match = [r for r in result if r.cohorte == "2025"]
        assert len(match) == 1
        assert match[0].total_atrasados == 1
        assert match[0].total_alumnos == 2
        assert match[0].porcentaje == 50.0

    async def test_empty_when_no_data(self, service: AnalyticsService):
        result = await service.get_atrasados_por_cohorte()
        assert result == []


class TestGetDistribucionNotas:
    async def test_returns_four_buckets(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_dictado,
    ):
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        notas = [Decimal("1.0"), Decimal("3.0"), Decimal("6.0"), Decimal("9.0")]
        for nota in notas:
            await repo.create({
                "entrada_padron_id": test_entrada_padron.id,
                "dictado_id": test_dictado.id,
                "actividad": "Parcial 1",
                "nota_numerica": nota,
                "aprobado": nota >= Decimal("4.0"),
            })

        result = await service.get_distribucion_notas()
        assert len(result) == 4
        bucket_map = {r.rango: r.cantidad for r in result}
        # 1.0 -> 10% -> bucket 0-25%
        assert bucket_map["0-25%"] >= 1
        # 3.0 -> 30% -> bucket 26-50%
        assert bucket_map["26-50%"] >= 1
        # 6.0 -> 60% -> bucket 51-75%
        assert bucket_map["51-75%"] >= 1
        # 9.0 -> 90% -> bucket 76-100%
        assert bucket_map["76-100%"] >= 1

    async def test_empty_when_no_notas(self, service: AnalyticsService):
        result = await service.get_distribucion_notas()
        assert len(result) == 4
        assert all(r.cantidad == 0 for r in result)

    async def test_filters_by_dictado(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_dictado,
    ):
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        await repo.create({
            "entrada_padron_id": test_entrada_padron.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("5.0"),
            "aprobado": True,
        })
        result = await service.get_distribucion_notas(dictado_id=test_dictado.id)
        assert len(result) == 4
        assert sum(r.cantidad for r in result) == 1

        import uuid
        result_empty = await service.get_distribucion_notas(dictado_id=uuid.uuid4())
        assert sum(r.cantidad for r in result_empty) == 0


class TestGetPrediccionAbandono:
    async def test_classifies_riesgo_alto(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_dictado,
    ):
        """>=3 atrasos AND promedio < 60 -> ALTO."""
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        for i in range(3):
            await repo.create({
                "entrada_padron_id": test_entrada_padron.id,
                "dictado_id": test_dictado.id,
                "actividad": f"Act {i}",
                "nota_numerica": Decimal("3.0"),  # 30% promedio
                "aprobado": False,
            })

        result = await service.get_prediccion_abandono()
        match = [r for r in result if r.alumno_id == test_entrada_padron.id]
        assert len(match) >= 1
        assert match[0].riesgo == "alto"

    async def test_classifies_riesgo_bajo(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_dictado,
    ):
        """Sin atrasos AND promedio >= 60 -> BAJO."""
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        await repo.create({
            "entrada_padron_id": test_entrada_padron.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("7.0"),  # 70%
            "aprobado": True,
        })

        result = await service.get_prediccion_abandono()
        match = [r for r in result if r.alumno_id == test_entrada_padron.id]
        assert len(match) >= 1
        assert match[0].riesgo == "bajo"

    async def test_classifies_riesgo_medio(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_dictado,
    ):
        """1 atraso OR promedio < 60 -> MEDIO."""
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        await repo.create({
            "entrada_padron_id": test_entrada_padron.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("3.0"),  # 30% (< 60)
            "aprobado": False,
        })

        result = await service.get_prediccion_abandono()
        match = [r for r in result if r.alumno_id == test_entrada_padron.id]
        assert len(match) >= 1
        assert match[0].riesgo == "medio"

    async def test_filters_by_riesgo(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_dictado,
    ):
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        await repo.create({
            "entrada_padron_id": test_entrada_padron.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("7.0"),
            "aprobado": True,
        })
        result = await service.get_prediccion_abandono(riesgo="bajo")
        assert all(r.riesgo == "bajo" for r in result)

        result_no_match = await service.get_prediccion_abandono(riesgo="alto")
        assert result_no_match == []


class TestGetDashboard:
    async def test_returns_kpis(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        service: AnalyticsService,
        test_entrada_padron,
        test_entrada_padron_2,
        test_dictado,
    ):
        repo = BaseRepository(model=Calificacion, session=db_session, tenant_id=test_tenant.id)
        await repo.create({
            "entrada_padron_id": test_entrada_padron.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("2.0"),
            "aprobado": False,
        })
        await repo.create({
            "entrada_padron_id": test_entrada_padron_2.id,
            "dictado_id": test_dictado.id,
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("8.0"),
            "aprobado": True,
        })

        result = await service.get_dashboard()
        assert result.total_alumnos >= 2
        assert result.total_atrasados_actual >= 1
        assert result.promedio_general > 0
        assert "bajo" in result.alumnos_en_riesgo
        assert "medio" in result.alumnos_en_riesgo
        assert "alto" in result.alumnos_en_riesgo
        assert result.total_materias >= 0
