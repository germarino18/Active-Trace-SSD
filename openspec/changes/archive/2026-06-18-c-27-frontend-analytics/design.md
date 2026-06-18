## Context

activia-trace ya dispone de endpoints de auditoría (`/api/v1/auditoria/`) y análisis (`/api/admin/analisis/`) que proveen datos de acciones, comunicaciones, atrasados por dictado y reportes de materia. También existe un panel de métricas frontend (C-19) con gráficos de acciones-por-día y estados de comunicación usando datos de esos endpoints.

Sin embargo, no hay:
- Visibilidad **longitudinal** de atrasados a través del tiempo (por cohorte)
- Distribución de notas agregada
- Predicción de abandono (ni siquiera basada en reglas)
- Exportación a PDF/Excel desde los dashboards

Este diseño cubre backend (4 nuevos endpoints) y frontend (feature module completo con Recharts + exportación client-side).

## Goals / Non-Goals

**Goals:**
- 4 nuevos endpoints GET en `/api/admin/analytics/` con filtros y datos agregados
- Página `/admin/analytics` lazy-loaded con dashboard de tendencias (2 charts) + tabla de predicción + botones de exportación
- Algoritmo de predicción rule-based (sin ML, sin dependencias externas)
- Export PDF client-side y Excel client-side usando librerías npm ligeras
- Sidebar item agrupado bajo "Administración" con permiso `auditoria:ver`

**Non-Goals:**
- NO se implementa ML real ni modelos entrenados
- NO se persisten predicciones en DB (se calculan on-the-fly)
- NO se agregan migrations de base de datos (los datos fuente ya existen)
- NO se implementa un motor de reportes server-side
- NO se modifican endpoints existentes de analisis ni auditoria

## Decisions

### D1 — Nuevo router separado vs ampliar router existente
**Decisión**: Crear `backend/app/api/v1/routers/analytics.py` con prefix `/api/admin/analytics`.
**Rationale**: Los endpoints de analytics son consultas agregadas de solo lectura, distintas de los análisis por dictado en `analisis.py` y de las métricas de auditoría en `auditoria.py`. Separarlos mantiene cohesión y ≤500 LOC por archivo.
**Alternativa**: Extender `analisis.py` — se descartó porque mezcla responsabilidades (análisis por materia vs analytics multi-cohorte).

### D2 — Algoritmo de predicción rule-based en service layer
**Decisión**: Lógica en `AnalyticsService.predict_abandono()` con reglas:
- ALTO: ≥3 materias con atrasos activos + promedio general < umbral (configurable, default 60%)
- MEDIO: 1-2 materias con atrasos O promedio < umbral
- BAJO: sin atrasos y promedio ≥ umbral
**Rationale**: Sin ML, sin dependencias externas, sin persistencia. Se calcula on-the-fly desde datos existentes. El umbral se pasa como query param opcional (default 60).
**Alternativa**: Persistir scores en DB — se descartó porque agrega complejidad sin valor inmediato (el cálculo es liviano).

### D3 — Recharts como librería de gráficos
**Decisión**: `recharts` sobre `nivo`, `chart.js`, `d3` directo.
**Rationale**: Recharts es declarativo (React puro), tiene buena compatibilidad con React 19, y es la opción más usada en el ecosistema React-Admin que activia-trace implementa. Además ya está familiarizado el equipo.
**Alternativa**: D3 directo — más flexible pero más verboso y sin tipado React nativo.

### D4 — Export PDF client-side con html2canvas + jsPDF
**Decisión**: Captura del DOM del dashboard con `html2canvas` y lo inyecta en `jsPDF`.
**Rationale**: No requiere backend de generación de PDF, funciona offline, y el dashboard es lo suficientemente simple para que el render DOM sea estable. La exportación incluye metadata (filtros aplicados, fecha de generación) sobreimpresa en el PDF.
**Alternativa**: Generar PDF server-side con ReportLab — más control pero agrega latencia y complejidad innecesaria para este alcance.

### D5 — Export Excel con SheetJS (xlsx)
**Decisión**: `xlsx` (SheetJS Community Edition) para exportar datos tabulares a `.xlsx`.
**Rationale**: Librería madura, sin dependencias, genera archivos binarios reales (no CSV falsos con extensión .xlsx). Los datos se exportan desde el estado actual del hook (datos ya cacheados por TanStack Query).
**Alternativa**: `exceljs` — más pesada y orientada a server-side.

### D6 — Permiso `auditoria:ver` para analytics
**Decisión**: Los endpoints de analytics usan `require_permission(Perm.AUDITORIA_VER)`.
**Rationale**: Analytics es una extensión del panel de métricas existente (C-19), que ya usa ese permiso. No se justifica un permiso nuevo porque analytics es solo-lectura sobre datos ya accesibles.

### D7 — snake_case en backend, camelCase en frontend
**Decisión**: Endpoints siguen snake_case en Python (convención del proyecto) y TypeScript consume las respuestas directamente. Los tipos frontend mapean los campos snake_case a propiedades TypeScript con el mismo nombre (sin transformación).
**Rationale**: Consistencia con el código existente y con la convención del stack.

## Risks / Trade-offs

- **[R1] Rendimiento en consultas multi-cohorte**: Los queries de atrasados-por-cohorte cruzan varias tablas. Si el volumen de datos es grande (>50k alumnos), los endpoints pueden lentificar. **Mitigación**: índices DB en `(cohorte_id, fecha)` para entregas; límite de 12 meses en la serie temporal.
- **[R2] html2canvas en dashboards complejos**: Si el dashboard tiene muchos charts, la captura puede ser lenta o renderizar incompleta. **Mitigación**: el dashboard tiene máximo 2 charts + 1 tabla, lo cual es manejable. Si es necesario, se puede usar opción `scale: 2` para calidad.
- **[R3] SheetJS en archivos grandes**: xlsx puede consumir mucha memoria con datasets grandes. **Mitigación**: la exportación solo incluye los datos visibles en pantalla (ya paginados/filtrados), no datasets completos.
- **[R4] Sin persistencia de predicciones**: Cada request recalcula el riesgo. Si muchos usuarios consultan simultáneamente, puede generar carga repetitiva. **Mitigación**: cache TanStack Query en frontend con staleTime 30s. Si es necesario en el futuro, se puede agregar un materialized view.
