import uuid

import pytest

from app.services.analisis.compute import (
    compute_alumno_atrasado,
    compute_metricas_materia,
    compute_nota_final,
    compute_ranking_aprobadas,
    detect_tps_sin_corregir,
    resolve_umbral,
)

_DEFAULT_UMBRAL = {"umbral_pct": 60, "valores_aprobatorios": ["Satisfactorio", "Supera lo esperado"]}


# ─── Resolve umbral ───────────────────────────────────────────────────────


class TestResolveUmbral:
    def test_returns_defaults_when_none(self):
        result = resolve_umbral(None)
        assert result["umbral_pct"] == 60
        assert "Satisfactorio" in result["valores_aprobatorios"]

    def test_uses_provided_umbral(self):
        umbral = type("Umbral", (), {"umbral_pct": 75, "valores_aprobatorios": ["Aprobado"]})()
        result = resolve_umbral(umbral)
        assert result["umbral_pct"] == 75
        assert result["valores_aprobatorios"] == ["Aprobado"]

    def test_uses_default_valores_when_umbral_has_none(self):
        umbral = type("Umbral", (), {"umbral_pct": 70, "valores_aprobatorios": None})()
        result = resolve_umbral(umbral)
        assert result["umbral_pct"] == 70
        assert result["valores_aprobatorios"] == ["Satisfactorio", "Supera lo esperado"]


# ─── Alumno atrasado ──────────────────────────────────────────────────────


class TestComputeAlumnoAtrasado:
    def test_alumno_with_all_aprobadas_is_not_atrasado(self):
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 80, "nota_textual": None, "aprobado": True},
            {"actividad": "TP 1", "nota_numerica": 90, "nota_textual": None, "aprobado": True},
        ]
        esperadas = ["Parcial 1", "TP 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is False
        assert faltantes == []
        assert desaprobadas == []

    def test_atrasado_by_faltante(self):
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 80, "nota_textual": None, "aprobado": True},
        ]
        esperadas = ["Parcial 1", "TP 1", "TP 2"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert sorted(faltantes) == ["TP 1", "TP 2"]
        assert desaprobadas == []

    def test_atrasado_by_umbral_numerico(self):
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 40, "nota_textual": None, "aprobado": False},
        ]
        esperadas = ["Parcial 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert faltantes == []
        assert desaprobadas == ["Parcial 1"]

    def test_atrasado_by_textual_outside_valores(self):
        califs = [
            {"actividad": "TP 1", "nota_numerica": None, "nota_textual": "Insatisfactorio", "aprobado": False},
        ]
        esperadas = ["TP 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert desaprobadas == ["TP 1"]

    def test_not_atrasado_by_textual_in_valores(self):
        califs = [
            {"actividad": "TP 1", "nota_numerica": None, "nota_textual": "Satisfactorio", "aprobado": True},
        ]
        esperadas = ["TP 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is False

    def test_empty_calificaciones_all_faltantes(self):
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado([], ["P1", "P2"], _DEFAULT_UMBRAL)
        assert atrasado is True
        assert sorted(faltantes) == ["P1", "P2"]

    def test_mixed_faltante_and_desaprobada(self):
        califs = [
            {"actividad": "P1", "nota_numerica": 30, "nota_textual": None, "aprobado": False},
            {"actividad": "P2", "nota_numerica": 80, "nota_textual": None, "aprobado": True},
        ]
        esperadas = ["P1", "P2", "P3"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert faltantes == ["P3"]
        assert desaprobadas == ["P1"]


# ─── Ranking aprobadas ────────────────────────────────────────────────────


class TestComputeRankingAprobadas:
    def test_ranking_simple(self):
        juan_id = uuid.uuid4()
        maria_id = uuid.uuid4()
        califs = [
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P1", "aprobado": True},
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P2", "aprobado": True},
            {"entrada_padron_id": maria_id, "nombre": "María", "apellidos": "García", "actividad": "P1", "aprobado": True},
            {"entrada_padron_id": maria_id, "nombre": "María", "apellidos": "García", "actividad": "P2", "aprobado": False},
        ]
        result = compute_ranking_aprobadas(califs)
        assert len(result) == 2
        assert result[0]["aprobadas"] == 2  # Juan first
        assert result[1]["aprobadas"] == 1  # María second

    def test_excludes_alumnos_with_zero_aprobadas(self):
        juan_id = uuid.uuid4()
        califs = [
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P1", "aprobado": False},
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P2", "aprobado": False},
        ]
        result = compute_ranking_aprobadas(califs)
        assert result == []

    def test_ranking_empty_calificaciones(self):
        result = compute_ranking_aprobadas([])
        assert result == []

    def test_tie_ordered_alphabetically(self):
        ana_id = uuid.uuid4()
        juan_id = uuid.uuid4()
        califs = [
            {"entrada_padron_id": ana_id, "nombre": "Ana", "apellidos": "García", "actividad": "P1", "aprobado": True},
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P1", "aprobado": True},
            {"entrada_padron_id": ana_id, "nombre": "Ana", "apellidos": "García", "actividad": "P2", "aprobado": True},
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P2", "aprobado": True},
        ]
        result = compute_ranking_aprobadas(califs)
        assert result[0]["alumno_apellido"] == "García"
        assert result[1]["alumno_apellido"] == "Pérez"

    def test_includes_total_actividades(self):
        juan_id = uuid.uuid4()
        califs = [
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P1", "aprobado": True},
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P2", "aprobado": False},
            {"entrada_padron_id": juan_id, "nombre": "Juan", "apellidos": "Pérez", "actividad": "P3", "aprobado": True},
        ]
        result = compute_ranking_aprobadas(califs)
        assert len(result) == 1
        assert result[0]["aprobadas"] == 2
        assert result[0]["total_actividades"] == 3


# ─── Nota final ───────────────────────────────────────────────────────────


class TestComputeNotaFinal:
    def test_promedio_simple(self):
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 80},
            {"actividad": "Parcial 2", "nota_numerica": 90},
        ]
        result = compute_nota_final(califs)
        assert result == 85.0

    def test_exclude_textual_only(self):
        califs = [
            {"actividad": "TP 1", "nota_numerica": None, "nota_textual": "Satisfactorio"},
            {"actividad": "Parcial 1", "nota_numerica": 70},
        ]
        result = compute_nota_final(califs)
        assert result == 70.0

    def test_no_numeric_returns_none(self):
        califs = [
            {"actividad": "TP 1", "nota_numerica": None, "nota_textual": "Satisfactorio"},
        ]
        result = compute_nota_final(califs)
        assert result is None

    def test_empty_list_returns_none(self):
        result = compute_nota_final([])
        assert result is None

    def test_single_numeric(self):
        califs = [
            {"actividad": "TP 1", "nota_numerica": 75},
        ]
        result = compute_nota_final(califs)
        assert result == 75.0


# ─── TPs sin corregir ─────────────────────────────────────────────────────


class TestDetectTPSinCorregir:
    def test_detecta_entregas_sin_calificar(self):
        finalizaciones = [
            {"entrada_padron_id": uuid.uuid4(), "actividad": "TP 1", "fecha": "2026-01-15"},
            {"entrada_padron_id": uuid.uuid4(), "actividad": "TP 2", "fecha": "2026-01-20"},
        ]
        calificaciones = [
            {"entrada_padron_id": finalizaciones[0]["entrada_padron_id"], "actividad": "TP 1", "nota_numerica": 80},
        ]
        result = detect_tps_sin_corregir(finalizaciones, calificaciones, es_textual=True)
        assert len(result) == 1
        assert result[0]["actividad"] == "TP 2"

    def test_no_pendientes_when_all_calificadas(self):
        ep_id = uuid.uuid4()
        finalizaciones = [
            {"entrada_padron_id": ep_id, "actividad": "TP 1", "fecha": "2026-01-15"},
        ]
        calificaciones = [
            {"entrada_padron_id": ep_id, "actividad": "TP 1", "nota_textual": "Satisfactorio"},
        ]
        result = detect_tps_sin_corregir(finalizaciones, calificaciones, es_textual=True)
        assert result == []

    def test_no_finalizaciones_returns_empty(self):
        result = detect_tps_sin_corregir([], [], es_textual=True)
        assert result == []

    def test_filtra_actividades_no_textuales(self):
        ep_id = uuid.uuid4()
        finalizaciones = [
            {"entrada_padron_id": ep_id, "actividad": "Parcial 1", "fecha": "2026-01-15"},
            {"entrada_padron_id": ep_id, "actividad": "TP 1", "fecha": "2026-01-20"},
        ]
        calificaciones = []
        result = detect_tps_sin_corregir(finalizaciones, calificaciones, es_textual=False)
        assert result == []

    def test_mismo_alumno_varias_actividades(self):
        ep_id = uuid.uuid4()
        finalizaciones = [
            {"entrada_padron_id": ep_id, "actividad": "TP 1", "fecha": "2026-01-15"},
            {"entrada_padron_id": ep_id, "actividad": "TP 2", "fecha": "2026-01-20"},
        ]
        calificaciones = [
            {"entrada_padron_id": ep_id, "actividad": "TP 1", "nota_textual": "Satisfactorio"},
        ]
        result = detect_tps_sin_corregir(finalizaciones, calificaciones, es_textual=True)
        assert len(result) == 1
        assert result[0]["actividad"] == "TP 2"


# ─── Metricas materia ─────────────────────────────────────────────────────


class TestComputeMetricasMateria:
    def test_basic_metrics(self):
        juan_id = uuid.uuid4()
        maria_id = uuid.uuid4()
        califs = [
            {"entrada_padron_id": juan_id, "actividad": "P1", "aprobado": True, "nota_numerica": 80, "nombre": "Juan", "apellidos": "Pérez"},
            {"entrada_padron_id": juan_id, "actividad": "P2", "aprobado": True, "nota_numerica": 90, "nombre": "Juan", "apellidos": "Pérez"},
            {"entrada_padron_id": maria_id, "actividad": "P1", "aprobado": True, "nota_numerica": 80, "nombre": "María", "apellidos": "García"},
            {"entrada_padron_id": maria_id, "actividad": "P2", "aprobado": False, "nota_numerica": 40, "nombre": "María", "apellidos": "García"},
        ]
        result = compute_metricas_materia(califs, _DEFAULT_UMBRAL)
        assert result["total_alumnos"] == 2
        assert result["aprobados"] == 1
        assert result["atrasados"] == 1
        result = compute_metricas_materia(califs, _DEFAULT_UMBRAL)
        assert result["total_alumnos"] == 2
        assert result["aprobados"] == 1
        assert result["atrasados"] == 1
        assert result["total_actividades"] == 2

    def test_empty_calificaciones(self):
        result = compute_metricas_materia([], _DEFAULT_UMBRAL)
        assert result["total_alumnos"] == 0
        assert result["aprobados"] == 0
        assert result["atrasados"] == 0
        assert result["total_actividades"] == 0
        assert result["sin_datos"] is True

    def test_promedio_general(self):
        juan_id = uuid.uuid4()
        maria_id = uuid.uuid4()
        califs = [
            {"entrada_padron_id": juan_id, "actividad": "P1", "aprobado": True, "nota_numerica": 80, "nombre": "Juan", "apellidos": "Pérez"},
            {"entrada_padron_id": juan_id, "actividad": "P2", "aprobado": True, "nota_numerica": 90, "nombre": "Juan", "apellidos": "Pérez"},
            {"entrada_padron_id": maria_id, "actividad": "P1", "aprobado": True, "nota_numerica": 70, "nombre": "María", "apellidos": "García"},
            {"entrada_padron_id": maria_id, "actividad": "P2", "aprobado": True, "nota_numerica": 60, "nombre": "María", "apellidos": "García"},
        ]
        result = compute_metricas_materia(califs, _DEFAULT_UMBRAL)
        assert result["promedio_general"] is not None
        assert result["promedio_general"] == 75.0  # (80+90+70+60)/4


# ─── Helpers ──────────────────────────────────────────────────────────────


def _make_calif(nombre: str, apellidos: str, actividad: str, aprobado: bool, nota_numerica: float | None = None):
    return {
        "entrada_padron_id": uuid.uuid4(),
        "nombre": nombre,
        "apellidos": apellidos,
        "actividad": actividad,
        "aprobado": aprobado,
        "nota_numerica": nota_numerica or (80 if aprobado else 40),
        "nota_textual": None,
    }
