from typing import Any

_DEFAULT_UMBRAL_PCT = 60
_DEFAULT_VALORES_APROBATORIOS = ["Satisfactorio", "Supera lo esperado"]


def resolve_umbral(umbral_materia) -> dict[str, Any]:
    if umbral_materia is None:
        return {
            "umbral_pct": _DEFAULT_UMBRAL_PCT,
            "valores_aprobatorios": list(_DEFAULT_VALORES_APROBATORIOS),
        }
    return {
        "umbral_pct": umbral_materia.umbral_pct,
        "valores_aprobatorios": (
            list(umbral_materia.valores_aprobatorios)
            if umbral_materia.valores_aprobatorios is not None
            else list(_DEFAULT_VALORES_APROBATORIOS)
        ),
    }


def compute_alumno_atrasado(
    alumno_calificaciones: list[dict],
    actividades_esperadas: list[str],
    umbral: dict[str, Any],
) -> tuple[bool, list[str], list[str]]:
    """Classify a student as atrasado or not based on the boolean `aprobado` field.

    Rules (RN — "aprobado", fix-regla-aprobado change):
    - faltantes: activities in `actividades_esperadas` with no calificacion row.
    - desaprobadas: calificacion rows where `aprobado is False` (strict identity;
      None and True are NOT counted as desaprobada).
    - is_atrasado: True if faltantes OR desaprobadas is non-empty.

    Note: the `umbral` parameter is retained for call-site compatibility with
    compute_metricas_materia, get_metricas_dictado, and get_dashboard, but it
    does NOT affect the classification outcome. The umbral still serves for
    other display-layer uses (e.g. showing note color), just not this rule.
    """
    actividades_con_calif = {c["actividad"] for c in alumno_calificaciones}
    faltantes = [a for a in actividades_esperadas if a not in actividades_con_calif]

    desaprobadas = [c["actividad"] for c in alumno_calificaciones if c.get("aprobado") is False]

    is_atrasado = bool(faltantes) or bool(desaprobadas)
    return is_atrasado, faltantes, desaprobadas


def compute_ranking_aprobadas(
    calificaciones: list[dict],
) -> list[dict]:
    from collections import defaultdict

    alumnos: dict = {}
    actividades_por_alumno: dict = defaultdict(set)

    for c in calificaciones:
        ep_id = c["entrada_padron_id"]
        if ep_id not in alumnos:
            alumnos[ep_id] = {
                "alumno_id": ep_id,
                "alumno_nombre": c.get("nombre", ""),
                "alumno_apellido": c.get("apellidos", ""),
                "aprobadas": 0,
                "total_actividades": 0,
            }
        actividades_por_alumno[ep_id].add(c["actividad"])
        if c.get("aprobado"):
            alumnos[ep_id]["aprobadas"] += 1

    for ep_id in alumnos:
        alumnos[ep_id]["total_actividades"] = len(actividades_por_alumno[ep_id])

    ranking = [a for a in alumnos.values() if a["aprobadas"] >= 1]
    ranking.sort(key=lambda x: (-x["aprobadas"], x["alumno_apellido"], x["alumno_nombre"]))
    return ranking


def compute_nota_final(
    calificaciones: list[dict],
) -> float | None:
    numericas = [c["nota_numerica"] for c in calificaciones if c.get("nota_numerica") is not None]
    if not numericas:
        return None
    return sum(float(n) for n in numericas) / len(numericas)


def detect_tps_sin_corregir(
    finalizaciones: list[dict],
    calificaciones: list[dict],
    es_textual: bool = True,
) -> list[dict]:
    if not es_textual:
        return []

    calif_set = {(c["entrada_padron_id"], c["actividad"]) for c in calificaciones}

    pendientes = []
    for f in finalizaciones:
        key = (f["entrada_padron_id"], f["actividad"])
        if key not in calif_set:
            pendientes.append({
                "alumno_id": f["entrada_padron_id"],
                "actividad": f["actividad"],
                "fecha_finalizacion": f.get("fecha"),
            })
    return pendientes


def compute_metricas_materia(
    calificaciones: list[dict],
    umbral: dict[str, Any],
) -> dict[str, Any]:
    if not calificaciones:
        return {
            "total_alumnos": 0,
            "aprobados": 0,
            "atrasados": 0,
            "total_actividades": 0,
            "promedio_general": None,
            "sin_datos": True,
        }

    from collections import defaultdict

    alumnos = defaultdict(list)
    for c in calificaciones:
        alumnos[c["entrada_padron_id"]].append(c)

    actividades = list({c["actividad"] for c in calificaciones})
    total_actividades = len(actividades)

    aprobados = 0
    atrasados = 0
    for ep_id, califs in alumnos.items():
        atrasado, _, _ = compute_alumno_atrasado(califs, actividades, umbral)
        if atrasado:
            atrasados += 1
        else:
            aprobados += 1

    notas = [float(c["nota_numerica"]) for c in calificaciones if c.get("nota_numerica") is not None]
    promedio = sum(notas) / len(notas) if notas else None

    return {
        "total_alumnos": len(alumnos),
        "aprobados": aprobados,
        "atrasados": atrasados,
        "total_actividades": total_actividades,
        "promedio_general": promedio,
        "sin_datos": False,
    }
