# Proposal: fix-regla-aprobado

## Why

Hay **dos definiciones contradictorias** de "aprobado / atrasado" conviviendo en el backend, y producen números inconsistentes para el MISMO alumno en la MISMA pantalla del profesor.

1. **Camino dashboard / métricas** — `backend/app/services/analisis/compute.py`:
   - `compute_alumno_atrasado` (línea ~23) clasifica una actividad como "desaprobada" por **umbral de nota** (`nota_numerica < umbral_pct`, con fallback por valor textual). El alumno es `atrasado` si tiene `faltantes` **o** `desaprobadas`. **Ignora la columna booleana `aprobado`.**
   - `compute_metricas_materia` (línea ~113) deriva `aprobados` = alumnos que NO son atrasado, usando la lógica de arriba.
   - Alimenta `GET /api/v1/profesor/dictados/{id}/metricas` (los StatCards del dashboard) y `get_dashboard` (`backend/app/services/profesor_service.py:99`, que **re-implementa el mismo loop inline**, líneas ~131-152).

2. **Camino panel de atrasados** — `backend/app/services/profesor_service.py:get_alumnos_clasificados` (líneas ~203-310): usa el campo booleano `calif.aprobado` **directamente** (`if not calif.aprobado: desaprobadas.append(...)`).

**Resultado:** el mismo alumno puede contarse como "aprobado" en el StatCard del dashboard y como "atrasado" en el panel de atrasados. El profesor ve cifras que no cierran entre sí.

Esto es una **regla de negocio codificada (RN)**, no un detalle de estilo: la definición de "aprobado" es contractual y gobierna métricas que se le muestran al profesor. Por eso se aísla como su propio change CRÍTICO, revisable de forma explícita.

## What Changes

**Decisión bloqueada — unificar sobre el campo booleano `aprobado`:**

Un alumno cuenta como **aprobado** si y solo si tiene una fila con `aprobado == True` en **TODAS** las actividades esperadas del dictado (es decir: sin faltantes y sin ninguna fila con `aprobado == False`). En cualquier otro caso es **atrasado**.

- **MODIFIED** `compute_alumno_atrasado` (`compute.py`): clasifica "desaprobada" por el booleano `aprobado` (`c["aprobado"] is False`) en lugar del umbral de nota. Mantiene la detección de `faltantes` igual (actividad esperada sin fila). El umbral (`umbral_pct`, `valores_aprobatorios`) deja de gobernar esta clasificación.
- **MODIFIED** `compute_metricas_materia` (`compute.py`): sigue derivando `aprobados`/`atrasados` desde `compute_alumno_atrasado`, por lo que hereda la nueva regla automáticamente. El StatCard del dashboard pasa a coincidir con `get_alumnos_clasificados`.
- **MODIFIED** `profesor_service.py:get_dashboard`: el loop inline duplicado (~131-152) ya invoca `compute_alumno_atrasado`, así que hereda la nueva regla; se reconcilia para no divergir (idealmente extrayendo el conteo a un helper compartido para no mantener dos copias del loop).
- **SIN CAMBIOS** `promedio_general` (promedio de notas numéricas) — solo cambia la clasificación aprobado/atrasado, no el cálculo de notas.
- **SIN CAMBIOS** `get_alumnos_clasificados` — ya es la fuente de verdad; el resto se alinea a ella. Se preserva su semántica de `subtipo` (`desaprobado` vs `atrasado_null`).

### Impacto en tests (TDD obligatorio)

Tests existentes que cambian (`backend/tests/test_analisis/unit/test_pure_functions.py`):
- `TestComputeAlumnoAtrasado::test_atrasado_by_umbral_numerico` (~L64) — hoy depende del umbral. Re-expresar: el alumno es atrasado por tener `aprobado=False`, no por nota.
- `TestComputeAlumnoAtrasado::test_atrasado_by_textual_outside_valores` (~L74) — idem, pasa a depender de `aprobado`.
- `TestComputeAlumnoAtrasado::test_not_atrasado_by_textual_in_valores` (~L83) — pasa a depender de `aprobado=True`.
- `TestComputeAlumnoAtrasado::test_mixed_faltante_and_desaprobada` (~L96) — re-anclar la desaprobación al booleano.
- `TestComputeMetricasMateria::test_basic_metrics` (~L262) — ya usa `aprobado`; verificar que sigue verde con la nueva regla.

Casos felices que NO cambian: `test_alumno_with_all_aprobadas_is_not_atrasado` (~L43), `test_atrasado_by_faltante` (~L54), `test_empty_calificaciones_all_faltantes` (~L91) — los faltantes se siguen detectando igual.

Tests nuevos a agregar (regla booleana, escritos PRIMERO en rojo):
- Fila con `aprobado=False` pero nota alta (`nota_numerica >= umbral`) → atrasado (antes daba aprobado).
- Fila con `aprobado=True` pero nota baja (`nota_numerica < umbral`) → aprobado (antes daba atrasado).
- Alumno con cero filas → atrasado (todas faltantes).
- Mix faltante + `aprobado=False` → atrasado, con desglose correcto.
- Paridad: `compute_metricas_materia` y `get_alumnos_clasificados` sobre el mismo dataset deben coincidir en `aprobados`/`atrasados`.

## Impact

- **Capabilities (delta-spec):** `analisis-atrasados` (MODIFIED — la regla de detección de atrasado deja de usar umbral de nota y pasa a usar el booleano `aprobado`). `metricas-frontend` NO se toca (es sobre métricas de uso del ADMIN, ajeno a esta regla).
- **Archivos a modificar:** `backend/app/services/analisis/compute.py`, `backend/app/services/profesor_service.py`, `backend/tests/test_analisis/unit/test_pure_functions.py` (+ posible nuevo test de paridad).
- **Endpoints afectados (comportamiento, no contrato):** `GET /api/v1/profesor/dictados/{id}/metricas`, dashboard del profesor. Los números cambian para alumnos cuyo `aprobado` booleano discrepaba del umbral de nota.
- **Governance: CRÍTICO** — cambio de regla de negocio. Esta propuesta hace la regla explícita y revisable; NO se implementa código en este change (solo artifacts). La implementación se aprueba aparte.
- **Riesgo / no-objetivo:** no se modifica el cálculo de `promedio_general`, ni el ranking (`compute_ranking_aprobadas`, que ya usa `aprobado`), ni la configuración de umbral (`configurar-umbral`) — el umbral sigue existiendo para otros usos (ej. mostrar nota), solo deja de gobernar la clasificación aprobado/atrasado.
