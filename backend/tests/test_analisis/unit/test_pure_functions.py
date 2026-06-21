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

    # Renamed from test_atrasado_by_umbral_numerico: the rule is now boolean aprobado,
    # not nota threshold. A row with aprobado=False is desaprobada regardless of nota.
    def test_atrasado_by_aprobado_false(self):
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 40, "nota_textual": None, "aprobado": False},
        ]
        esperadas = ["Parcial 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert faltantes == []
        assert desaprobadas == ["Parcial 1"]

    # Renamed from test_atrasado_by_textual_outside_valores: aprobado=False drives result.
    def test_atrasado_by_aprobado_false_textual(self):
        califs = [
            {"actividad": "TP 1", "nota_numerica": None, "nota_textual": "Insatisfactorio", "aprobado": False},
        ]
        esperadas = ["TP 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert desaprobadas == ["TP 1"]

    # Renamed from test_not_atrasado_by_textual_in_valores: aprobado=True drives result.
    def test_not_atrasado_by_aprobado_true(self):
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

    # aprobado field drives desaprobadas; P1 is False, P2 is True.
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

    # ── NEW RED tests for the boolean-aprobado rule (tasks §2) ──────────────

    def test_aprobado_false_nota_alta_is_atrasado(self):
        """aprobado=False + nota_numerica >= umbral → atrasado (new rule).

        With the old umbral-based logic the nota 80 >= 60 would have produced
        no desaprobadas, giving is_atrasado=False. With the boolean rule the
        aprobado=False field is the only criterion.
        """
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 80, "nota_textual": None, "aprobado": False},
        ]
        esperadas = ["Parcial 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert desaprobadas == ["Parcial 1"]
        assert faltantes == []

    def test_aprobado_true_nota_baja_is_not_atrasado(self):
        """aprobado=True + nota_numerica < umbral → aprobado (new rule).

        With the old umbral-based logic nota 40 < 60 would add to desaprobadas,
        giving is_atrasado=True. With the boolean rule aprobado=True is
        sufficient regardless of nota.
        """
        califs = [
            {"actividad": "Parcial 1", "nota_numerica": 40, "nota_textual": None, "aprobado": True},
        ]
        esperadas = ["Parcial 1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is False
        assert desaprobadas == []
        assert faltantes == []

    def test_all_actividades_aprobado_true_not_atrasado(self):
        """Every expected activity has aprobado=True → alumno is aprobado."""
        califs = [
            {"actividad": "P1", "nota_numerica": 30, "nota_textual": None, "aprobado": True},
            {"actividad": "P2", "nota_numerica": 30, "nota_textual": None, "aprobado": True},
            {"actividad": "P3", "nota_numerica": None, "nota_textual": "Insatisfactorio", "aprobado": True},
        ]
        esperadas = ["P1", "P2", "P3"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is False
        assert desaprobadas == []
        assert faltantes == []

    def test_zero_filas_all_faltantes_atrasado(self):
        """Zero calificacion rows → all expected activities are faltantes → atrasado."""
        esperadas = ["P1", "P2", "P3"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado([], esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert sorted(faltantes) == ["P1", "P2", "P3"]
        assert desaprobadas == []

    def test_mix_faltante_and_aprobado_false_desglose(self):
        """Mix of faltante + aprobado=False → atrasado with correct breakdown."""
        califs = [
            {"actividad": "P1", "nota_numerica": 80, "nota_textual": None, "aprobado": False},
            {"actividad": "P2", "nota_numerica": 90, "nota_textual": None, "aprobado": True},
        ]
        esperadas = ["P1", "P2", "P3"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert atrasado is True
        assert faltantes == ["P3"]
        assert desaprobadas == ["P1"]

    def test_aprobado_none_not_counted_as_desaprobada(self):
        """A row with aprobado=None is NOT counted as desaprobada.

        The rule uses `c.get("aprobado") is False` (strict identity check) so
        None ≠ False. A row with aprobado=None is treated as pending/neutral —
        it occupies the actividad slot (no faltante) but does not add to
        desaprobadas. Whether the alumno is atrasado depends on other factors.
        This is consistent with get_alumnos_clasificados which only marks
        desaprobado when `not calif.aprobado` is evaluated on a real row with
        explicit aprobado=False.
        """
        califs = [
            {"actividad": "P1", "nota_numerica": 40, "nota_textual": None, "aprobado": None},
        ]
        esperadas = ["P1"]
        atrasado, faltantes, desaprobadas = compute_alumno_atrasado(califs, esperadas, _DEFAULT_UMBRAL)
        assert desaprobadas == []
        assert faltantes == []
        # atrasado=False because no faltantes and no desaprobadas
        assert atrasado is False


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

    def test_boolean_rule_overrides_umbral(self):
        """Task 2.7: aprobado=True nota baja → aprobado; aprobado=False nota alta → atrasado.

        Dataset: two alumnos, each with one activity.
        - alumno_a: nota=30 (< umbral=60) but aprobado=True → should be counted as aprobado
        - alumno_b: nota=90 (>= umbral=60) but aprobado=False → should be counted as atrasado
        Old umbral-based rule would invert both counts. New boolean rule fixes this.
        """
        alumno_a = uuid.uuid4()
        alumno_b = uuid.uuid4()
        califs = [
            {"entrada_padron_id": alumno_a, "actividad": "P1", "aprobado": True, "nota_numerica": 30, "nota_textual": None},
            {"entrada_padron_id": alumno_b, "actividad": "P1", "aprobado": False, "nota_numerica": 90, "nota_textual": None},
        ]
        result = compute_metricas_materia(califs, _DEFAULT_UMBRAL)
        assert result["total_alumnos"] == 2
        assert result["aprobados"] == 1  # alumno_a (aprobado=True despite nota<umbral)
        assert result["atrasados"] == 1  # alumno_b (aprobado=False despite nota>=umbral)

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

    def test_parity_metricas_and_per_alumno_classification(self):
        """Task 6.1/6.2: compute_metricas_materia counts must match per-alumno boolean rule.

        Dataset without faltantes (all activities have rows) to isolate the aprobado rule.
        We simulate what get_alumnos_clasificados would count via compute_alumno_atrasado
        directly and verify it matches compute_metricas_materia aggregates.

        This is the "bug original" scenario: a mix of aprobado=True/False with notes that
        would have given opposite results under the old umbral-based rule.
        """
        alumno1 = uuid.uuid4()
        alumno2 = uuid.uuid4()
        alumno3 = uuid.uuid4()
        # alumno1: aprobado=True, nota baja → aprobado (new rule)
        # alumno2: aprobado=False, nota alta → atrasado (new rule)
        # alumno3: aprobado=True, nota alta → aprobado
        califs = [
            {"entrada_padron_id": alumno1, "actividad": "P1", "aprobado": True, "nota_numerica": 30, "nota_textual": None},
            {"entrada_padron_id": alumno1, "actividad": "P2", "aprobado": True, "nota_numerica": 35, "nota_textual": None},
            {"entrada_padron_id": alumno2, "actividad": "P1", "aprobado": False, "nota_numerica": 90, "nota_textual": None},
            {"entrada_padron_id": alumno2, "actividad": "P2", "aprobado": False, "nota_numerica": 85, "nota_textual": None},
            {"entrada_padron_id": alumno3, "actividad": "P1", "aprobado": True, "nota_numerica": 80, "nota_textual": None},
            {"entrada_padron_id": alumno3, "actividad": "P2", "aprobado": True, "nota_numerica": 90, "nota_textual": None},
        ]
        actividades = ["P1", "P2"]

        # Per-alumno classification via compute_alumno_atrasado (same logic as get_alumnos_clasificados)
        from collections import defaultdict
        alumnos_by_ep: dict = defaultdict(list)
        for c in califs:
            alumnos_by_ep[c["entrada_padron_id"]].append(c)

        manual_aprobados = 0
        manual_atrasados = 0
        for ep_id, ep_califs in alumnos_by_ep.items():
            atrasado, _, _ = compute_alumno_atrasado(ep_califs, actividades, _DEFAULT_UMBRAL)
            if atrasado:
                manual_atrasados += 1
            else:
                manual_aprobados += 1

        # Aggregate via compute_metricas_materia
        result = compute_metricas_materia(califs, _DEFAULT_UMBRAL)

        assert result["aprobados"] == manual_aprobados
        assert result["atrasados"] == manual_atrasados
        assert result["aprobados"] == 2   # alumno1 + alumno3
        assert result["atrasados"] == 1   # alumno2


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
