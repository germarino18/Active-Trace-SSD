## 1. Feature Module Scaffolding and Types

- [x] 1.1 Create `features/academico/` directory structure: `{components,hooks,services,types,pages}`
- [x] 1.2 Define domain types in `features/academico/types/index.ts`: `Materia`, `Alumno`, `Calificacion`, `Actividad`, `Comunicacion`, `MensajeStatus`, `UmbralMateria`
- [x] 1.3 Define API response types: `ImportPreviewResponse`, `AtrasadosResponse`, `RankingResponse`, `NotasFinalesResponse`, `ReportesRapidosResponse`, `MonitorResponse`
- [x] 1.4 Add materia routes to `App.tsx` under `AuthGuard / AppLayout`: `/materias/:id` redirect, `/materias/:id/importar`, `/materias/:id/atrasados`, `/materias/:id/comunicar`, `/materias/:id/entregas-pendientes`, `/materias/:id/monitor`
- [x] 1.5 Create `MateriaLayout` component with materia selector header and tab navigation for sub-pages
- [x] 1.6 Update sidebar menu configuration with PROFESOR menu items requiring `calificaciones:*`, `atrasados:*`, `comunicacion:*` permissions

## 2. Importar Calificaciones — Service and Upload Hook

- [x] 2.1 Create `features/academico/services/importar.service.ts` with functions: `uploadCalificaciones(file, materiaId)`, `confirmarImportacion(materiaId, activityIds)`, `configurarUmbral(materiaId, porcentaje)`
- [x] 2.2 Create `features/academico/hooks/useFileUpload.ts` custom hook managing file state, upload progress, error handling, and FormData construction
- [x] 2.3 Create `features/academico/hooks/useImportarCalificaciones.ts` hook wrapping service calls with TanStack Query mutations
- [x] 2.4 Create `features/academico/pages/ImportarCalificacionesPage.tsx` with file upload area, activity preview table with selection toggles, threshold input, and confirm button
- [x] 2.5 Create `features/academico/components/ActivityPreviewTable.tsx` — table displaying detected activities with selection checkboxes
- [x] 2.6 Create `features/academico/components/ThresholdInput.tsx` — percentage input with validation (1-100)
- [x] 2.7 Create `features/academico/components/FileUploadArea.tsx` — styled drop/click upload area accepting `.csv` and `.xlsx`

## 3. Vista Atrasados — Overdue Students, Ranking, Final Grades, Reports

- [x] 3.1 Create `features/academico/services/atrasados.service.ts` with functions: `getAtrasados(materiaId)`, `getRanking(materiaId)`, `getNotasFinales(materiaId)`, `getReportesRapidos(materiaId)`
- [x] 3.2 Create `features/academico/hooks/useAtrasados.ts` — TanStack Query hooks for fetching overdue, ranking, final grades, and reports data
- [x] 3.3 Create `features/academico/pages/VistaAtrasadosPage.tsx` with four sub-tabs: Atrasados, Ranking, Notas Finales, Reportes
- [x] 3.4 Create `features/academico/components/TablaAtrasados.tsx` — sortable table of overdue students with visual highlighting
- [x] 3.5 Create `features/academico/components/TablaRanking.tsx` — ranked table sorted by approved count
- [x] 3.6 Create `features/academico/components/TablaNotasFinales.tsx` — final grades table with export-ready display
- [x] 3.7 Create `features/academico/components/ReportesRapidos.tsx` — metric cards (total students, at-risk, avg completion, activities)
- [x] 3.8 Create `features/academico/components/EmptyState.tsx` — reusable empty state component for "no data" scenarios
- [x] 3.9 Create `features/academico/components/LoadingState.tsx` — reusable loading skeleton for data tables

## 4. Entregas Sin Corregir — Detection and Export

- [x] 4.1 Create `features/academico/services/entregas.service.ts` with functions: `detectarEntregas(materiaId, file)`, `exportarEntregas(materiaId)`
- [x] 4.2 Create `features/academico/hooks/useEntregas.ts` — TanStack Query mutation for detection and query for results
- [x] 4.3 Create `features/academico/pages/EntregasSinCorregirPage.tsx` with upload area and results table
- [x] 4.4 Create `features/academico/components/TablaEntregasPendientes.tsx` — table of uncorrected deliveries
- [x] 4.5 Implement export trigger that downloads file via browser

## 5. Comunicacion Atrasados — Preview, Send, Status Tracking

- [x] 5.1 Create `features/academico/services/comunicacion.service.ts` with functions: `getPreview(materiaId, studentIds)`, `enviarComunicacion(materiaId, studentIds)`, `getStatus(comunicacionId)`
- [x] 5.2 Create `features/academico/hooks/useComunicacion.ts` — TanStack Query mutation for preview/send, query with `refetchInterval` for status tracking
- [x] 5.3 Create `features/academico/pages/ComunicacionAtrasadosPage.tsx` with student multi-select list, preview button, send button, and status tracking panel
- [x] 5.4 Create `features/academico/components/StudentMultiSelect.tsx` — list of overdue students with checkboxes
- [x] 5.5 Create `features/academico/components/PreviewComunicacionModal.tsx` — modal displaying generated subject and body per student
- [x] 5.6 Create `features/academico/components/TablaStatusComunicacion.tsx` — real-time status table with visual status badges
- [x] 5.7 Create `features/academico/components/StatusBadge.tsx` — colored badge for each status (Pendiente/Enviando/OK/Fallido/Cancelado)
- [x] 5.8 Implement polling stop logic when all messages are in terminal state

## 6. Monitor Seguimiento — Follow-up Monitor

- [x] 6.1 Create `features/academico/services/monitor.service.ts` with function: `getMonitorData(materiaId, filters)`
- [x] 6.2 Create `features/academico/hooks/useMonitor.ts` — TanStack Query hook with filter state
- [x] 6.3 Create `features/academico/pages/MonitorSeguimientoPage.tsx` with filter bar and results table
- [x] 6.4 Create `features/academico/components/FiltrosMonitor.tsx` — filter inputs: student name, commission dropdown, activity dropdown, minimum completion
- [x] 6.5 Create `features/academico/components/TablaMonitor.tsx` — student activity status results table

## 7. Tests

- [x] 7.1 Write test: `ImportarCalificacionesPage` renders upload area and handles file selection
- [x] 7.2 Write test: Import flow — mocked upload returns preview, user selects activities and confirms
- [x] 7.3 Write test: `TablaAtrasados` renders overdue students with correct data and highlighting
- [x] 7.4 Write test: `VistaAtrasadosPage` tab switching between atrasados, ranking, final grades, reports
- [x] 7.5 Write test: `PreviewComunicacionModal` renders generated preview content
- [x] 7.6 Write test: `ComunicacionAtrasadosPage` send flow with mocked API
- [x] 7.7 Write test: `TablaStatusComunicacion` displays correct status badges and polling stops at terminal state
- [x] 7.8 Write test: `MonitorSeguimientoPage` renders filters and applies them
- [x] 7.9 Write test: `MateriaLayout` renders tabs and navigates between sub-pages
- [x] 7.10 Write test: Empty states render correctly when no data
