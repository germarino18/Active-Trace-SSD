from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.calificaciones import (
    ActividadDetectada,
    CalificacionImportRow,
    CalificacionResponse,
    ImportCalificacionesConfirm,
    ImportCalificacionesResponse,
    PreviewCalificacionesRequest,
    PreviewCalificacionesResponse,
    UmbralMateriaCreate,
    UmbralMateriaResponse,
    UmbralMateriaUpdate,
)


class TestCalificacionResponse:
    def test_valid_full(self):
        data = {
            "id": uuid4(),
            "entrada_padron_id": uuid4(),
            "dictado_id": uuid4(),
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("85.50"),
            "nota_textual": None,
            "aprobado": True,
            "origen": "Importado",
            "importado_at": datetime.now(timezone.utc),
        }
        schema = CalificacionResponse(**data)
        assert schema.actividad == "Parcial 1"
        assert schema.nota_numerica == Decimal("85.50")
        assert schema.aprobado is True

    def test_valid_minimal(self):
        data = {
            "id": uuid4(),
            "entrada_padron_id": uuid4(),
            "dictado_id": uuid4(),
            "actividad": "TP Final",
            "nota_numerica": None,
            "nota_textual": "Aprobado",
            "aprobado": True,
            "origen": "Manual",
            "importado_at": datetime.now(timezone.utc),
        }
        schema = CalificacionResponse(**data)
        assert schema.nota_textual == "Aprobado"
        assert schema.nota_numerica is None

    def test_extra_fields_rejected(self):
        data = {
            "id": uuid4(),
            "entrada_padron_id": uuid4(),
            "dictado_id": uuid4(),
            "actividad": "Parcial",
            "aprobado": True,
            "origen": "Importado",
            "importado_at": datetime.now(timezone.utc),
            "extra_field": "should fail",
        }
        with pytest.raises(ValidationError):
            CalificacionResponse(**data)

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            CalificacionResponse()


class TestCalificacionImportRow:
    def test_valid_full(self):
        data = {
            "entrada_padron_id": uuid4(),
            "actividad": "Parcial 1",
            "nota_numerica": Decimal("90.00"),
            "nota_textual": None,
        }
        schema = CalificacionImportRow(**data)
        assert schema.actividad == "Parcial 1"

    def test_valid_minimal(self):
        data = {
            "actividad": "TP 2",
        }
        schema = CalificacionImportRow(**data)
        assert schema.entrada_padron_id is None
        assert schema.nota_numerica is None
        assert schema.nota_textual is None

    def test_extra_fields_rejected(self):
        data = {
            "actividad": "Parcial",
            "origen": "Manual",
        }
        with pytest.raises(ValidationError):
            CalificacionImportRow(**data)


class TestPreviewCalificacionesResponse:
    def test_valid(self):
        data = {
            "actividades_detectadas": [
                {"nombre": "Parcial 1", "tipo": "numerica", "tiene_nota": True},
            ],
            "filas": [{"legajo": "123", "nota": "85"}],
            "total_filas": 1,
            "preview_token": "tok_abc123",
        }
        schema = PreviewCalificacionesResponse(**data)
        assert len(schema.actividades_detectadas) == 1
        assert isinstance(schema.actividades_detectadas[0], ActividadDetectada)
        assert schema.total_filas == 1

    def test_extra_fields_rejected(self):
        data = {
            "actividades_detectadas": [],
            "filas": [],
            "total_filas": 0,
            "preview_token": "tok_abc",
            "extra": "nope",
        }
        with pytest.raises(ValidationError):
            PreviewCalificacionesResponse(**data)


class TestActividadDetectada:
    def test_valid(self):
        data = {"nombre": "Parcial 1", "tipo": "numerica", "tiene_nota": True}
        schema = ActividadDetectada(**data)
        assert schema.tipo == "numerica"

    def test_invalid_tipo(self):
        data = {"nombre": "Parcial", "tipo": "booleana", "tiene_nota": False}
        schema = ActividadDetectada(**data)
        assert schema.tipo == "booleana"  # no enum constraint — free string


class TestPreviewCalificacionesRequest:
    def test_valid(self):
        data = {"dictado_id": uuid4()}
        schema = PreviewCalificacionesRequest(**data)
        assert schema.dictado_id is not None

    def test_extra_fields_rejected(self):
        data = {"dictado_id": uuid4(), "extra": "nope"}
        with pytest.raises(ValidationError):
            PreviewCalificacionesRequest(**data)


class TestImportCalificacionesConfirm:
    def test_valid(self):
        data = {
            "dictado_id": uuid4(),
            "preview_token": "tok_valid",
            "actividades_seleccionadas": ["Parcial 1", "TP 2"],
        }
        schema = ImportCalificacionesConfirm(**data)
        assert len(schema.actividades_seleccionadas) == 2

    def test_extra_fields_rejected(self):
        data = {
            "dictado_id": uuid4(),
            "preview_token": "tok",
            "actividades_seleccionadas": [],
            "extra": "nope",
        }
        with pytest.raises(ValidationError):
            ImportCalificacionesConfirm(**data)


class TestImportCalificacionesResponse:
    def test_valid(self):
        data = {
            "total_importados": 50,
            "aprobados": 35,
            "desaprobados": 15,
            "mensaje": "Importación exitosa",
        }
        schema = ImportCalificacionesResponse(**data)
        assert schema.total_importados == 50
        assert schema.aprobados + schema.desaprobados == schema.total_importados

    def test_extra_fields_rejected(self):
        data = {
            "total_importados": 0,
            "aprobados": 0,
            "desaprobados": 0,
            "mensaje": "ok",
            "extra": "nope",
        }
        with pytest.raises(ValidationError):
            ImportCalificacionesResponse(**data)


class TestUmbralMateriaCreate:
    def test_valid_defaults(self):
        data = {"dictado_id": uuid4(), "umbral_pct": 60}
        schema = UmbralMateriaCreate(**data)
        assert schema.umbral_pct == 60
        assert schema.valores_aprobatorios is None

    def test_valid_with_valores(self):
        data = {
            "dictado_id": uuid4(),
            "umbral_pct": 70,
            "valores_aprobatorios": ["Aprobado", "Promocionado"],
        }
        schema = UmbralMateriaCreate(**data)
        assert schema.valores_aprobatorios == ["Aprobado", "Promocionado"]

    def test_umbral_under_0(self):
        data = {"dictado_id": uuid4(), "umbral_pct": -1}
        with pytest.raises(ValidationError):
            UmbralMateriaCreate(**data)

    def test_umbral_over_100(self):
        data = {"dictado_id": uuid4(), "umbral_pct": 101}
        with pytest.raises(ValidationError):
            UmbralMateriaCreate(**data)

    def test_umbral_at_boundaries(self):
        data = {"dictado_id": uuid4(), "umbral_pct": 0}
        schema = UmbralMateriaCreate(**data)
        assert schema.umbral_pct == 0
        data2 = {"dictado_id": uuid4(), "umbral_pct": 100}
        schema2 = UmbralMateriaCreate(**data2)
        assert schema2.umbral_pct == 100

    def test_extra_fields_rejected(self):
        data = {"dictado_id": uuid4(), "umbral_pct": 60, "extra": "nope"}
        with pytest.raises(ValidationError):
            UmbralMateriaCreate(**data)


class TestUmbralMateriaUpdate:
    def test_valid_partial(self):
        data = {"umbral_pct": 75}
        schema = UmbralMateriaUpdate(**data)
        assert schema.umbral_pct == 75

    def test_valid_valores_only(self):
        data = {"valores_aprobatorios": ["Aprobado"]}
        schema = UmbralMateriaUpdate(**data)
        assert schema.valores_aprobatorios == ["Aprobado"]

    def test_valid_empty(self):
        schema = UmbralMateriaUpdate()
        assert schema.umbral_pct is None
        assert schema.valores_aprobatorios is None

    def test_umbral_out_of_range(self):
        data = {"umbral_pct": 150}
        with pytest.raises(ValidationError):
            UmbralMateriaUpdate(**data)

    def test_extra_fields_rejected(self):
        data = {"extra": "nope"}
        with pytest.raises(ValidationError):
            UmbralMateriaUpdate(**data)


class TestUmbralMateriaResponse:
    def test_valid(self):
        data = {
            "id": uuid4(),
            "asignacion_id": uuid4(),
            "dictado_id": uuid4(),
            "umbral_pct": 60,
            "valores_aprobatorios": None,
        }
        schema = UmbralMateriaResponse(**data)
        assert schema.umbral_pct == 60

    def test_valid_with_valores(self):
        data = {
            "id": uuid4(),
            "asignacion_id": uuid4(),
            "dictado_id": uuid4(),
            "umbral_pct": 80,
            "valores_aprobatorios": ["Promocionado"],
        }
        schema = UmbralMateriaResponse(**data)
        assert schema.valores_aprobatorios == ["Promocionado"]

    def test_extra_fields_rejected(self):
        data = {
            "id": uuid4(),
            "asignacion_id": uuid4(),
            "dictado_id": uuid4(),
            "umbral_pct": 60,
            "extra": "nope",
        }
        with pytest.raises(ValidationError):
            UmbralMateriaResponse(**data)
