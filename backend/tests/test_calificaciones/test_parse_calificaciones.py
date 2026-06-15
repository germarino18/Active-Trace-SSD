"""Tests for parse_calificaciones.py — File parsing for grades and completion reports.

Tests cover:
- CSV parsing with (Real) columns detection
- XLSX parsing with (Real) columns detection
- Textual value columns detection
- RN-01: (Real) suffix → numeric grade
- RN-02: Textual columns patterns
- F1.2 Finalización: completion detection
- detectar_tps_sin_calificar
- Invalid/missing files
"""

import csv
import io
import uuid

import pytest
from openpyxl import Workbook

from app.services.calificaciones.parse_calificaciones import (
    detectar_tps_sin_calificar,
    parse_calificaciones_file,
    parse_finalizacion_file,
)


def _make_csv_bytes(headers: list[str], rows: list[list]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def _make_xlsx_bytes(headers: list[str], rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── parse_calificaciones_file ─────────────────────────────────────────────


class TestParseCalificacionesColumnDetection:
    """RN-01, RN-02: Column detection algorithm."""

    def test_detects_numeric_columns_with_real_suffix(self):
        """RN-01: Columns ending in (Real) → numeric grade."""
        headers = ["Apellidos", "Nombre", "Parcial 1 (Real)", "TP 1 (Real)"]
        rows = [
            ["Pérez", "Juan", "85", "90"],
            ["García", "María", "70", "60"],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        assert len(result["actividades"]) == 2
        act_map = {a["nombre"]: a for a in result["actividades"]}

        assert "Parcial 1" in act_map
        assert act_map["Parcial 1"]["tipo"] == "numerica"

        assert "TP 1" in act_map
        assert act_map["TP 1"]["tipo"] == "numerica"

    def test_detects_textual_columns_without_real_suffix(self):
        """RN-02: Columns without (Real) can contain textual values."""
        headers = ["Apellidos", "Nombre", "TP 1 (Real)", "TP 1"]
        rows = [
            ["Pérez", "Juan", "85", "Satisfactorio"],
            ["García", "María", "70", "No satisfactorio"],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        assert len(result["actividades"]) >= 1
        tp1_activities = [a for a in result["actividades"] if a["nombre"] == "TP 1"]
        assert len(tp1_activities) >= 1
        numeric_tps = [a for a in tp1_activities if a["tipo"] == "numerica"]
        textual_tps = [a for a in tp1_activities if a["tipo"] == "textual"]
        assert len(numeric_tps) >= 1 or len(textual_tps) >= 1

    def test_parses_rows_with_numeric_values(self):
        """Rows contain student data and numeric grades."""
        headers = ["Apellidos", "Nombre", "Parcial 1 (Real)"]
        rows = [
            ["Pérez", "Juan", "85"],
            ["García", "María", "70"],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        assert result["total_filas"] == 2
        assert len(result["filas"]) == 2
        assert result["filas"][0]["alumno_apellidos"] == "Pérez"
        assert result["filas"][0]["alumno_nombre"] == "Juan"
        assert result["filas"][0]["Parcial 1_num"] == 85.0

    def test_parses_decimal_numeric_values(self):
        """Decimal values are preserved."""
        headers = ["Apellidos", "Nombre", "Examen (Real)"]
        rows = [
            ["Pérez", "Juan", "85.50"],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")
        assert result["filas"][0]["Examen_num"] == 85.50

    def test_parses_textual_values(self):
        """Textual values are captured as strings."""
        headers = ["Apellidos", "Nombre", "TP 1", "TP 2"]
        rows = [
            ["Pérez", "Juan", "Satisfactorio", "Supera lo esperado"],
            ["García", "María", "No satisfactorio", ""],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        assert result["filas"][0]["TP 1_txt"] == "Satisfactorio"
        assert result["filas"][0]["TP 2_txt"] == "Supera lo esperado"
        assert result["filas"][1]["TP 1_txt"] == "No satisfactorio"

    def test_handles_mixed_numeric_and_textual_for_same_activity(self):
        """Activity can have both (Real) and textual column."""
        headers = ["Apellidos", "Nombre", "TP 1 (Real)", "TP 1"]
        rows = [
            ["Pérez", "Juan", "85", "Satisfactorio"],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        row = result["filas"][0]
        assert row["TP 1_num"] == 85.0
        assert row["TP 1_txt"] == "Satisfactorio"

    def test_empty_cells_are_none(self):
        """Empty cells are returned as None."""
        headers = ["Apellidos", "Nombre", "Parcial 1 (Real)", "TP 1"]
        rows = [
            ["Pérez", "Juan", "", ""],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        row = result["filas"][0]
        assert row["Parcial 1_num"] is None
        assert row["TP 1_txt"] is None

    def test_handles_only_student_columns_no_grades(self):
        """File with only student info columns produces no activities."""
        headers = ["Apellidos", "Nombre"]
        rows = [
            ["Pérez", "Juan"],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.csv")

        assert result["total_filas"] == 1
        assert result["actividades"] == []

    def test_parses_xlsx_file(self):
        """XLSX files are parsed correctly."""
        headers = ["Apellidos", "Nombre", "Parcial 1 (Real)"]
        rows = [
            ["Pérez", "Juan", "85"],
        ]
        content = _make_xlsx_bytes(headers, rows)
        result = parse_calificaciones_file(content, "grades.xlsx")

        assert result["total_filas"] == 1
        assert result["filas"][0]["Parcial 1_num"] == 85.0

    def test_rejects_unsupported_format(self):
        with pytest.raises(ValueError, match="(?i)formato"):
            parse_calificaciones_file(b"data", "grades.pdf")


# ── parse_finalizacion_file ───────────────────────────────────────────────


class TestParseFinalizacion:
    """F1.2 Finalización: completion report parsing."""

    def test_detects_completion_columns(self):
        """Completion columns (Aprobado/No aprobado/Entregado) are detected."""
        headers = ["Apellidos", "Nombre", "Finalización", "TP Final"]
        rows = [
            ["Pérez", "Juan", "Aprobado", "Entregado"],
            ["García", "María", "No aprobado", "Entregado"],
            ["López", "Ana", "Entregado", ""],
        ]
        content = _make_csv_bytes(headers, rows)
        result = parse_finalizacion_file(content, "finalizacion.csv")

        assert result["total_filas"] == 3
        assert "actividades" in result
        assert len(result["actividades"]) >= 1

    def test_parses_xlsx_completion_file(self):
        headers = ["Apellidos", "Nombre", "Finalización"]
        rows = [
            ["Pérez", "Juan", "Aprobado"],
        ]
        content = _make_xlsx_bytes(headers, rows)
        result = parse_finalizacion_file(content, "finalizacion.xlsx")
        assert result["total_filas"] == 1


# ── detectar_tps_sin_calificar ────────────────────────────────────────────


class TestDetectarTPSinCalificar:
    """TPs that are 'Entregado' but have no numeric grade."""

    def test_detects_tp_sin_calificar(self):
        """Row where TP is 'Entregado' but no grade exists."""
        rows = [
            {
                "alumno_nombre": "Juan",
                "alumno_apellidos": "Pérez",
                "TP 1_txt": "Entregado",
                "TP 1_num": None,
            },
        ]
        actividades = [{"nombre": "TP 1", "tipo": "textual", "columna": "TP 1"}]
        result = detectar_tps_sin_calificar(rows, actividades)

        assert len(result) == 1
        assert result[0]["actividad"] == "TP 1"
        assert result[0]["alumno_apellidos"] == "Pérez"

    def test_ignores_tp_with_grade(self):
        """Row where TP has both 'Entregado' and a grade → not detected."""
        rows = [
            {
                "alumno_nombre": "Juan",
                "alumno_apellidos": "Pérez",
                "TP 1_txt": "Entregado",
                "TP 1_num": 85.0,
            },
        ]
        actividades = [{"nombre": "TP 1", "tipo": "textual", "columna": "TP 1"}]
        result = detectar_tps_sin_calificar(rows, actividades)
        assert len(result) == 0

    def test_ignores_not_entregado(self):
        """Row where TP is not 'Entregado' → not detected."""
        rows = [
            {
                "alumno_nombre": "Juan",
                "alumno_apellidos": "Pérez",
                "TP 1_txt": "No entregado",
                "TP 1_num": None,
            },
        ]
        actividades = [{"nombre": "TP 1", "tipo": "textual", "columna": "TP 1"}]
        result = detectar_tps_sin_calificar(rows, actividades)
        assert len(result) == 0

    def test_empty_rows_returns_empty(self):
        assert detectar_tps_sin_calificar([], []) == []

    def test_rejects_invalid_file_format(self):
        with pytest.raises(ValueError, match="(?i)formato"):
            parse_finalizacion_file(b"data", "grades.pdf")
