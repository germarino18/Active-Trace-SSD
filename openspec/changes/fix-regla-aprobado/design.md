# Design: fix-regla-aprobado

## Context

Existen dos implementaciones de la clasificación "aprobado vs atrasado":

- `compute.py::compute_alumno_atrasado` clasifica por **umbral de nota** y se usa para las **métricas agregadas** (StatCards del dashboard, `compute_metricas_materia`, y el loop inline de `get_dashboard`).
- `profesor_service.py::get_alumnos_clasificados` clasifica por el **booleano `aprobado`** y se usa para el **panel de atrasados** (la lista nominal de alumnos).

Ambas leen las mismas `Calificacion`, pero con criterios distintos. La columna `aprobado` es la decisión autorizada de aprobación de cada actividad (la setea la importación / corrección). El umbral de nota es derivado y puede no coincidir (ej. nota alta pero marcada no aprobada por el docente, o textual aprobada con número bajo).

`get_alumnos_clasificados` es la fuente de verdad: es la que el profesor usa para actuar sobre alumnos concretos. Las métricas deben coincidir con ella, no al revés.

## Goals / Non-Goals

**Goals**
- Una sola definición de "aprobado" en todo el backend, anclada al booleano `aprobado`.
- Las métricas agregadas (`compute_metricas_materia`, dashboard) coinciden alumno-por-alumno con `get_alumnos_clasificados`.
- Eliminar la divergencia del loop inline duplicado en `get_dashboard`.

**Non-Goals**
- No cambiar `promedio_general` (sigue siendo promedio de `nota_numerica`).
- No cambiar `compute_ranking_aprobadas` (ya cuenta por `aprobado`).
- No eliminar la entidad/config de umbral (`configurar-umbral`): el umbral sigue válido para otros usos; solo deja de gobernar esta clasificación.
- No tocar el contrato HTTP (mismos campos de respuesta); solo cambian los valores para alumnos con discrepancia.

## Decision

**Regla unificada (RN — "aprobado"):**

> Para un dictado con un conjunto de **actividades esperadas** `E`, un alumno está **APROBADO** sii, para toda actividad `a ∈ E`, existe una fila `Calificacion` del alumno para `a` con `aprobado == True`. En caso contrario está **ATRASADO**.

Descomposición por alumno (la que implementa `compute_alumno_atrasado`):
- `faltantes` = actividades de `E` sin ninguna fila del alumno.
- `desaprobadas` = actividades del alumno con fila cuyo `aprobado == False`.
- `is_atrasado = bool(faltantes) or bool(desaprobadas)`.

Esto reemplaza la rama actual que evalúa `nota_numerica < umbral_pct` / `nota_textual not in valores_aprobatorios`.

### Firma y comportamiento de `compute_alumno_atrasado`

Se conserva la firma `(alumno_calificaciones, actividades_esperadas, umbral) -> (bool, faltantes, desaprobadas)` para minimizar el blast radius en los llamadores. El parámetro `umbral` queda como argumento **no usado** por la clasificación (se puede mantener por compatibilidad de llamadas, o quitarse — decisión de implementación; si se quita, actualizar los 3 call sites). Nuevo cuerpo de la rama de desaprobadas:

```
desaprobadas = [c["actividad"] for c in alumno_calificaciones if c.get("aprobado") is False]
```

Tratamiento de `aprobado` ausente/None: una fila sin `aprobado` explícito NO se cuenta como desaprobada (consistente con `get_alumnos_clasificados`, que sólo marca desaprobado cuando `not calif.aprobado` sobre filas reales — aquí se usa `is False` para no confundir `None` con `False`). Documentar este matiz en el test.

### Reconciliación del loop inline en `get_dashboard`

El loop de `get_dashboard` (~L131-152) ya arma dicts `{actividad, nota_numerica, nota_textual, aprobado}` y llama a `compute_alumno_atrasado`, así que **hereda la nueva regla sin cambios de lógica**. Para evitar dos copias del armado del conteo, extraer un helper compartido — opción preferida:

- Reusar `compute_metricas_materia` (o un helper más fino `contar_atrasados(califs_dicts, actividades)`) en `get_dashboard`, pasándole los mismos dicts. Así `total_atrasados` del dashboard y `atrasados` de las métricas salen del mismo código.

### Paridad métricas ↔ panel

`compute_metricas_materia` deriva `actividades` como `{c["actividad"] for c in calificaciones}` (las actividades que aparecen en alguna calificación). `get_alumnos_clasificados` deriva las actividades de la tabla `Actividad` (con `fecha_limite`). Hay un matiz: `get_alumnos_clasificados` solo cuenta un faltante como `atrasado_null` si la actividad está **vencida** (`fecha_limite < hoy`); las métricas no conocen `fecha_limite`.

Para esta corrección, el **objetivo de paridad** es sobre la dimensión `aprobado` (que es el bug reportado: mismo alumno aprobado en un lado y atrasado en otro por criterio distinto). La diferencia por `fecha_limite` en faltantes es una asimetría preexistente de fuentes de datos, no parte de esta decisión bloqueada. El test de paridad debe construirse sobre un dataset **sin faltantes** (todas las actividades con fila) para aislar la regla de `aprobado` y garantizar coincidencia exacta. Se deja anotado como riesgo conocido (ver abajo) que la paridad total de faltantes requeriría que las métricas también consulten `Actividad`/`fecha_limite` — fuera de alcance aquí.

## Risks / Trade-offs

- **Cambio de números visibles**: alumnos con `aprobado=True` y nota baja pasan de "atrasado" a "aprobado", y viceversa. Es el objetivo, pero hay que comunicarlo en el archive (cambia el StatCard). Mitigación: la regla queda explícita y aprobada antes de implementar (governance CRÍTICO).
- **Asimetría de faltantes por `fecha_limite`**: métricas vs panel pueden seguir difiriendo en el conteo de faltantes no vencidos. Fuera de alcance; documentado como deuda. El bug reportado (criterio aprobado vs umbral) sí queda resuelto.
- **`umbral` huérfano en la firma**: si se deja sin uso, un lector futuro puede creer que aún gobierna. Mitigación: docstring explícito de que `umbral` ya no afecta la clasificación, o eliminarlo y actualizar los 3 call sites.

## Migration Plan

No hay migración de datos ni de schema. Es un cambio de lógica de servicio puro. La implementación (otro change/fase) sigue Strict TDD: primero los tests rojos de la regla booleana, luego el mínimo cambio en `compute.py`, luego reconciliar `get_dashboard`, refactor a helper compartido, y verificar paridad. Sin mocks de DB en los tests de integración (DB efímera).

## Open Questions

- ¿Se elimina el parámetro `umbral` de `compute_alumno_atrasado` o se conserva por compatibilidad? (Decisión menor de implementación; ambas válidas — el default propuesto es conservarlo con docstring que aclara que no afecta la clasificación.)
- ¿Se quiere, en un change futuro, alinear también las métricas a `Actividad.fecha_limite` para paridad total de faltantes? (Fuera de alcance de este change.)
