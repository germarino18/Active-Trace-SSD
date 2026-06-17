"""Tests for auditoria schemas."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.auditoria import (
    AccionesPorDiaItem,
    AuditoriaFiltros,
    ComunicacionesPorDocenteItem,
    InteraccionItem,
    InteraccionesPorDocenteMateriaItem,
    LogAuditoriaItem,
    LogAuditoriaPaginado,
    UltimasAccionesItem,
    UltimasAccionesResponse,
)


class TestAccionesPorDiaItem:
    def test_valid(self):
        item = AccionesPorDiaItem(fecha="2026-06-01", total=5)
        assert item.fecha == "2026-06-01"
        assert item.total == 5

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            AccionesPorDiaItem(fecha="2026-06-01", total=5, extra_field="nope")

    def test_negative_total_rejected(self):
        with pytest.raises(ValidationError):
            AccionesPorDiaItem(fecha="2026-06-01", total=-1)


class TestComunicacionesPorDocenteItem:
    def test_valid_with_defaults(self):
        item = ComunicacionesPorDocenteItem(
            docente_id=uuid4(),
            materia_id=uuid4(),
        )
        assert item.pendiente == 0
        assert item.enviado == 0
        assert item.error == 0
        assert item.cancelado == 0

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            ComunicacionesPorDocenteItem(
                docente_id=uuid4(),
                materia_id=uuid4(),
                extra="nope",
            )


class TestInteraccionItem:
    def test_valid(self):
        item = InteraccionItem(accion="CALIFICACIONES_IMPORTAR", total=3)
        assert item.accion == "CALIFICACIONES_IMPORTAR"
        assert item.total == 3


class TestInteraccionesPorDocenteMateriaItem:
    def test_valid(self):
        item = InteraccionesPorDocenteMateriaItem(
            docente_id=uuid4(),
            materia_id=uuid4(),
            interacciones=[InteraccionItem(accion="A", total=1)],
        )
        assert len(item.interacciones) == 1


class TestUltimasAccionesItem:
    def test_valid(self):
        item = UltimasAccionesItem(
            id=uuid4(),
            fecha_hora=datetime.now(timezone.utc),
            actor_id=uuid4(),
            accion="TEST_ACTION",
        )
        assert item.actor_nombre is None
        assert item.materia_nombre is None

    def test_with_nombres(self):
        item = UltimasAccionesItem(
            id=uuid4(),
            fecha_hora=datetime.now(timezone.utc),
            actor_id=uuid4(),
            accion="TEST_ACTION",
            actor_nombre="Juan",
            materia_nombre="Matemáticas",
        )
        assert item.actor_nombre == "Juan"


class TestUltimasAccionesResponse:
    def test_valid(self):
        resp = UltimasAccionesResponse(
            items=[],
            limit=200,
        )
        assert resp.limit == 200
        assert resp.items == []


class TestLogAuditoriaItem:
    def test_valid(self):
        item = LogAuditoriaItem(
            id=uuid4(),
            fecha_hora=datetime.now(timezone.utc),
            actor_id=uuid4(),
            accion="TEST",
        )
        assert item.accion == "TEST"


class TestLogAuditoriaPaginado:
    def test_valid(self):
        pag = LogAuditoriaPaginado(items=[], total=0, offset=0, limit=50)
        assert pag.total == 0

    def test_limit_bounds(self):
        with pytest.raises(ValidationError):
            LogAuditoriaPaginado(items=[], total=0, offset=0, limit=300)


class TestAuditoriaFiltros:
    def test_all_optional(self):
        filtros = AuditoriaFiltros()
        assert filtros.fecha_desde is None

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            AuditoriaFiltros(unknown_field="x")
