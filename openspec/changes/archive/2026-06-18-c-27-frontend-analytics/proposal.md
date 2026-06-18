## Why

El sistema de tracking académico ya dispone de datos operativos (atrasados, calificaciones, cohortes) y un panel de auditoría/métricas (C-19), pero carece de **visibilidad longitudinal y predictiva**. Los coordinadores y administradores necesitan detectar tendencias de atraso a lo largo del tiempo, identificar alumnos en riesgo de abandono, y exportar reportes ejecutivos sin depender de herramientas externas. Este cambio cierra esa brecha con dashboards analíticos livianos y exportación client-side.

## What Changes

- Nuevo router `/api/admin/analytics/` con 4 endpoints GET para tendencias, distribución de notas, predicción y dashboard resumen
- Nuevo feature module `frontend/src/features/analytics/` con página de dashboard, gráficos Recharts, tabla de predicción y exportación PDF/Excel
- Integración con sidebar (`/admin/analytics`, permiso `auditoria:ver`)
- Nuevas dependencias npm: `recharts`, `jspdf`, `html2canvas`, `xlsx`

## Capabilities

### New Capabilities
- `analytics-tendencias`: Trend dashboard showing atrasados-por-cohorte time series and nota distribution histogram, with filters by materia/carrera/cohorte/fecha. Consumes existing endpoints + new backend endpoints.
- `prediccion-abandono`: Basic dropout prediction (rule-based: ALTO/MEDIO/BAJO risk) displayed in a color-coded table with filters by cohorte/materia/risk level.
- `reportes-exportables`: Client-side export of dashboard data to PDF (html2canvas + jsPDF) and Excel (xlsx/SheetJS), including applied filters and generation timestamp.

### Modified Capabilities
<!-- No existing capabilities have requirement changes. -->

## Impact

- **Backend**: new `backend/app/api/v1/routers/analytics.py` (router), `backend/app/schemas/analytics.py` (Pydantic schemas), `backend/app/services/analytics_service.py` (service), `backend/app/repositories/analytics_repository.py` (repository)
- **Frontend**: new module `frontend/src/features/analytics/` (5 components, 1 hook, 1 service, 1 type file, 1 page)
- **Dependencies**: `recharts`, `jspdf`, `html2canvas`, `xlsx` added to `frontend/package.json`
- **Routing**: lazy-loaded route `/admin/analytics` added to `frontend/src/App.tsx`
- **Sidebar**: new nav item in `frontend/src/features/layout/components/AppLayout.tsx`
