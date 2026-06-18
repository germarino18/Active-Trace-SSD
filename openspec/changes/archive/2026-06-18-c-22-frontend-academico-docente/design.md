## Context

The PROFESOR role's frontend module is the second frontend change after C-21 (shell + auth). The backend exposes REST endpoints for grades (C-10), analysis (C-11), and communications (C-12). The frontend must consume these endpoints through the existing Axios client, which already handles auth tokens and transparent refresh. The feature-based module structure, Tailwind CSS v4 design tokens, and permission-based sidebar are already established by C-21.

## Goals / Non-Goals

**Goals:**
- Feature pages for the PROFESOR role under `features/academico/` following the C-21 conventions
- Grade import page: file upload (CSV/XLSX), activity preview table, activity selection toggles, threshold percentage input
- Overdue students view: filtered table with student name, email, commission, pending activities, current grade vs threshold
- Ranking view: table sorted by approved activity count
- Final grades view: aggregated final score per student with export-ready display
- Quick reports: summary metrics card (total students, at-risk count, avg completion)
- Uncorrected deliveries: cross-reference table of submitted vs graded, with export button
- Communication panel: student multi-select, preview modal with backend-generated content, send with queue status tracking
- Follow-up monitor: filterable table with inputs for student name, commission, activity, minimum completion
- New sidebar menu items for PROFESOR requiring `calificaciones:*`, `atrasados:*`, `comunicacion:*` permissions
- Routes under `AuthGuard / AppLayout` with param-based materia selection
- Tests covering: import flow, overdue table rendering, communication preview, status tracking

**Non-Goals:**
- COORDINADOR/ADMIN features (C-23, C-24)
- E2E tests
- Backend changes
- Real-time WebSocket connections (status tracking uses polling via TanStack Query `refetchInterval`)
- File drag-and-drop upload (uses standard `<input type="file">`)

## Decisions

### 1. Feature module structure: `features/academico/`
- **Decision**: A single `features/academico/` module with sub-folders `{components,hooks,services,types,pages}`. Each sub-feature (import, atrasados, comunicacion, monitor) gets its own files within those folders.
- **Rationale**: Follows the C-21 convention (`features/auth/`, `features/layout/`). The domain is cohesive (all PROFESOR academic features) — splitting into separate modules would duplicate shared types (Materia, Alumno, Calificacion).
- **Alternatives considered**: Separate feature modules per sub-feature (too granular for this domain's interconnected types).

### 2. Component tree and routing
- **Decision**: `MateriaLayout` component wraps sub-pages with a materia selector header + tab navigation. Routes:
  ```
  /materias/:id                   → Redirect to /materias/:id/importar
  /materias/:id/importar          → ImportarCalificacionesPage
  /materias/:id/atrasados         → VistaAtrasadosPage (with sub-tabs: atrasados, ranking, notas-finales, reportes)
  /materias/:id/comunicar         → ComunicacionAtrasadosPage
  /materias/:id/monitor           → MonitorSeguimientoPage
  /materias/:id/entregas-pendientes → EntregasSinCorregirPage
  ```
- **Rationale**: Materia context is global to all PROFESOR actions. A shared param `:id` avoids re-selecting the materia on every page.
- **Alternatives considered**: Flat routes without materia param (requires a global "selected materia" context — adds complexity without benefit).

### 3. API service layer
- **Decision**: Each sub-feature gets a dedicated service file (`services/importar.service.ts`, `services/atrasados.service.ts`, etc.) that calls the existing typed API helpers (`get`, `post`, `patch` from `shared/services/api.ts`).
- **Rationale**: Keeps API calls organized by domain. The existing `api.ts` provides the base client with auth interceptor — no need for a second Axios instance.
- **Key endpoints consumed**:
  - `POST /api/v1/materias/{id}/importar-calificaciones` — upload + preview
  - `POST /api/v1/materias/{id}/configurar-umbral` — set threshold
  - `GET /api/v1/materias/{id}/atrasados` — overdue list
  - `GET /api/v1/materias/{id}/ranking` — ranking
  - `GET /api/v1/materias/{id}/notas-finales` — final grades
  - `GET /api/v1/materias/{id}/reportes-rapidos` — quick reports
  - `POST /api/v1/materias/{id}/detectar-entregas` — uncorrected detection
  - `GET /api/v1/materias/{id}/entregas-pendientes` — pending deliveries
  - `GET /api/v1/materias/{id}/entregas-pendientes/export` — export
  - `POST /api/v1/materias/{id}/comunicaciones/preview` — message preview
  - `POST /api/v1/comunicaciones/enviar` — send
  - `GET /api/v1/comunicaciones/{id}/status` — status tracking
  - `GET /api/v1/materias/{id}/monitor` — monitor data

### 4. File upload handling
- **Decision**: Use `FormData` with Axios `multipart/form-data` for grade import. A custom hook `useFileUpload` manages file state, upload progress, and error handling.
- **Rationale**: Axios handles `FormData` natively. A dedicated hook keeps upload logic reusable (later C-23 may need similar upload for padron import).
- **Alternatives considered**: react-dropzone (adds dependency for marginal benefit over native `<input type="file">`).

### 5. Status tracking: polling-based
- **Decision**: Communication status tracking uses TanStack Query's `refetchInterval` (3s polling) on `GET /api/v1/comunicaciones/{id}/status` while any message is in a non-terminal state (Pendiente/Enviando).
- **Rationale**: WebSocket support is not yet in the backend. Polling is simple and reliable for the expected volume (tens of messages, not thousands). TanStack Query handles deduplication and caching.
- **Alternatives considered**: SSE (EventSource) — backend does not expose SSE endpoints; WebSocket — deferred to future infra changes.

### 6. Shared types
- **Decision**: Define domain types (`Materia`, `Alumno`, `Calificacion`, `Actividad`, `Comunicacion`, `MensajeStatus`) in `features/academico/types/` with a barrel export.
- **Rationale**: Centralized types prevent duplication across the 5 sub-features. Models mirror the backend API response shapes.
- **Pattern**: Each type interface uses read-only fields where appropriate and follows the backend's `snake_case` property naming.

### 7. Sidebar menu integration
- **Decision**: Extend the `MenuItem[]` configuration in `features/layout/` with a PROFESOR group that appears when the user has `calificaciones:*` or `atrasados:*` permissions. Items link to `/materias` (materia selection page) and sub-routes.
- **Rationale**: Follows the existing permission-based menu pattern from C-21. The menu checks the user's JWT-contained permissions at render time.

### 8. Styling
- **Decision**: All new components use Tailwind utility classes exclusively, following the Obsidian theme tokens defined in C-21 (`bg-surface`, `border-outline-variant`, `text-on-surface`, `text-primary`).
- **Pattern**: Data tables use `bg-surface-container-lowest` with `border-outline-variant`, sorted columns, and row hover highlight. Cards use `bg-surface-container-lowest rounded-xl border border-outline-variant p-md`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Large file uploads timeout the Vite proxy | Configure Axios `timeout` to 120s for upload endpoints. Add upload progress indicator. |
| Polling creates excessive requests with many open communication panels | `refetchInterval` is set to 3000ms only when component is visible (via `document.visibilityState` check). Stop polling when all messages are terminal. |
| Materia param-based routing makes bookmarking fragile | Materia IDs are UUIDs — route `/materias/:id/importar` is stable and bookmarkable. Handle invalid UUIDs with a 404 redirect. |
| Five spec files in one feature module creates merge conflicts in `types/` | Single `types/index.ts` file. Conflicts are limited to adding new interfaces to the bottom. |
