## Context

The activia-trace backend is fully implemented (C-01 through C-20). There is no frontend. C-21 establishes the frontend foundation: a React 18 SPA with Vite, TypeScript, Tailwind CSS v4, and feature-based modules. The backend exposes REST endpoints at `/api/auth/*`, `/api/v1/*`, `/api/admin/*`, etc., all serving a JSON API. Authentication uses JWT (access + refresh token rotation) with optional TOTP 2FA. Authorization uses RBAC with `modulo:accion` permissions carried in the JWT.

## Goals / Non-Goals

**Goals:**
- Greenfield React 18 + Vite + TypeScript project under `frontend/`
- Feature-based directory structure: `features/{name}/{components,hooks,services,types,pages}`
- Centralized Axios HTTP client with transparent access token refresh via interceptor
- Auth pages: Login (email + password + tenant header), 2FA challenge, Forgot Password, Reset Password
- Route guard component (`AuthGuard`) that checks session + required permissions
- Layout shell (`AppLayout`) with responsive sidebar, top header, breadcrumbs, user dropdown
- Permission-driven sidebar menu that shows/hides items based on user roles
- Logout flow: POST `/api/auth/logout` → clear tokens → redirect to login
- Docker Compose service for the frontend dev server (port 5173) tied to the existing backend service
- Test suite covering: login page render, mocked auth flow, guard redirects (no session → login, no permission → forbidden), transparent token refresh

**Non-Goals:**
- Domain feature pages for students, courses, commissions, calendar, etc. (C-22, C-23, C-24)
- Dashboard widgets or metrics
- CRUD tables, data grids, or management interfaces
- Any backend changes or new API endpoints
- E2E tests (deferred until domain pages exist)

## Decisions

### 1. Routing: react-router-dom v6 with `createBrowserRouter`
- **Decision**: Use the data router API (`createBrowserRouter` + `<RouterProvider>`) for nested route layouts with guards.
- **Rationale**: Nested routes map naturally to AppLayout → Pages. Route-level `loader` functions can run auth checks before rendering. v6 is the de facto standard for React routing.
- **Alternatives considered**: TanStack Router (too new, smaller ecosystem); reach-router (merged into react-router).

### 2. Auth state: React context + TanStack Query for server state
- **Decision**: `AuthContext` holds the current session (access token, refresh token, user profile, roles). TanStack Query handles the `/api/auth/me` profile fetch. The context is the source of truth for session existence.
- **Rationale**: Auth state is truly global — every component needs it. TanStack Query manages caching and refetch of the user profile. The context is minimal (tokens + profile), updated only by auth actions (login, refresh, logout).
- **Alternatives considered**: Zustand (overkill for simple global auth state); Redux (explicitly ruled out by project conventions).

### 3. Token storage: memory (variable) with refresh persistence
- **Decision**: Access token lives in a JavaScript variable (not localStorage). Refresh token stored in an httpOnly cookie set by the backend.
- **Rationale**: Access tokens in localStorage are vulnerable to XSS. The backend already sets the refresh token as an httpOnly cookie on login/refresh responses — the frontend never touches it directly.
- **Risk**: Page reload loses the in-memory access token. Mitigation: the Axios interceptor calls the refresh endpoint on the first 401, which reads the httpOnly cookie, issues new tokens, and the app resumes transparently.

### 4. HTTP client: Axios with request/response interceptors
- **Decision**: A single Axios instance in `shared/services/api.ts` pre-configured with `baseURL`, `X-Tenant-ID` header, and two interceptors:
  - **Request interceptor**: Attaches `Authorization: Bearer <access_token>` from AuthContext.
  - **Response interceptor**: On 401, attempts a single transparent refresh (POST `/api/auth/refresh`), updates the access token, retries the original request. On 403 after refresh, or if refresh fails, clears session and redirects to login.
- **Rationale**: Axios is the project's chosen HTTP client. Interceptors are the standard pattern for cross-cutting token management. The refresh queue (single active refresh, queuing concurrent 401s) prevents race conditions.
- **Alternatives considered**: fetch API wrapper (lacks interceptor pattern, more boilerplate); ky (smaller but less ecosystem support for interceptors).

### 5. Permission model: JWT roles → frontend capability map
- **Decision**: The JWT payload includes the user's roles. A TypeScript `PermissionMap` type maps `modulo:accion` strings to boolean checks against the user's roles. The sidebar menu is a declarative array of `MenuItem` objects with a `requiredPermissions` field.
- **Rationale**: Re-resolving permissions from the server on every navigation would add latency. The role-to-permission mapping is deterministic (same roles → same permissions). The backend is the source of truth for the user's roles; the frontend's capability map is derived from them.

### 6. Forms: React Hook Form + Zod
- **Decision**: All auth forms (Login, 2FA, Forgot Password, Reset Password) use React Hook Form with Zod schema validation.
- **Rationale**: Project convention. Zod provides typed schemas with `safeParse` for validation. React Hook Form integrates via `@hookform/resolvers/zod`. Both are already in the stack.

### 7. Styling: Tailwind CSS v4 exclusively
- **Decision**: All styles use Tailwind utility classes. No CSS modules, no inline styles (except dynamic values), no styled-components.
- **Rationale**: Project convention. Tailwind v4 uses CSS-first configuration with `@import "tailwindcss"` and OKLCH color tokens.

### 8. Docker: dev-only service
- **Decision**: A `Dockerfile.dev` using `node:20-alpine` with Vite dev server (HMR). The `docker-compose.yml` adds a `frontend` service mapped to port 5173, with the Vite proxy forwarding `/api/*` to the backend service.
- **Rationale**: Avoids CORS issues in development by proxying through Vite. Production image deferred to later changes.

## Visual Design: Obsidian — High-Contrast Dark

**North Star**: *"Precision in Darkness"* — developer-grade dark UI. Near-black surfaces, high-contrast text, precise accent colors. Clean, fast-feeling, and functional.

### Design Tokens (Tailwind v4 `@theme`)

**Source**: `docs/design/stitch-obsidian/` — generated by Stitch (Google MCP). Contains 8 screen mockups with HTML/CSS code and `screen.png` screenshots.

```css
@theme {
  /* Backgrounds */
  --color-background: #09090b;           /* True near-black */
  --color-surface: #0c0c0f;
  --color-surface-dim: #0c0c0f;
  --color-surface-bright: #18181b;
  --color-surface-container-lowest: #09090b;
  --color-surface-container-low: #0f0f12;
  --color-surface-container: #121215;
  --color-surface-container-high: #18181b;
  --color-surface-container-highest: #1e1e22;
  --color-surface-variant: #18181b;

  /* Primary — Soft Violet */
  --color-primary: #a78bfa;
  --color-primary-container: #7c3aed;
  --color-on-primary: #0a0012;
  --color-on-primary-container: #ede9fe;
  --color-primary-fixed: #ede9fe;
  --color-primary-fixed-dim: #c4b5fd;
  --color-inverse-primary: #5b21b6;

  /* Tertiary — Emerald Green (success) */
  --color-tertiary: #34d399;
  --color-tertiary-container: #065f46;
  --color-on-tertiary: #001a12;
  --color-on-tertiary-container: #bbf7d0;

  /* Secondary — Zinc grays */
  --color-secondary: #71717a;
  --color-secondary-container: #27272a;

  /* Semantic */
  --color-error: #ef4444;               /* Errors only — no decorative use */
  --color-error-container: #3b1111;
  --color-outline: #52525b;
  --color-outline-variant: #27272a;     /* Default border color */
  --color-on-surface: #fafafa;          /* Primary text — high contrast */
  --color-on-surface-variant: #a1a1aa;  /* Secondary text */

  /* Typography */
  --font-family-sans: 'Geist', sans-serif;

  /* Border radius */
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;

  /* Spacing */
  --spacing-gutter: 24px;
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 24px;
  --spacing-lg: 40px;
  --spacing-xl: 64px;
}
```

### Component Patterns

- **Sidebar**: 280px fixed left, `bg-surface-container-lowest`, `border-r border-outline-variant`. Active nav item = `text-primary` + `border-r-4 border-primary` + `bg-surface-container-low`.
- **Header**: Sticky top, `bg-background/80 backdrop-blur-md`, `border-b border-outline-variant`, h-16. Search bar, notification bell, user avatar.
- **Cards**: `bg-surface-container-lowest`, `border border-outline-variant`, `rounded-xl`, `p-md`. Hover: `translateY(-2px)` with `0.3s ease`.
- **Grid**: 12-column bento layout (`grid grid-cols-12 gap-6`).
- **Buttons**: Primary = `bg-primary text-on-primary rounded-xl`. Ghost = transparent, visible on hover.
- **Inputs**: `bg-surface-container border border-outline-variant rounded-lg`, violet focus ring (`focus:ring-2 focus:ring-primary`).
- **Borders over shadows**: Separation achieved with `1px solid #27272a`, never shadows.
- **Scrollbar**: Custom thin (`4px`), `#52525b` thumb, transparent track.

### Stitch mockup reference screens

| Screen | File |
|--------|------|
| Dashboard (dark) | `docs/design/stitch-obsidian/dashboard_principal_dark/code.html` |
| Professor Panel | `docs/design/stitch-obsidian/panel_del_profesor/code.html` |
| Admin Management | `docs/design/stitch-obsidian/gesti_n_de_administrador/code.html` |
| Student Dashboard | `docs/design/stitch-obsidian/mi_carrera_y_materias_alumno/code.html` |
| Nexo Portal | `docs/design/stitch-obsidian/portal_nexo_consultas/code.html` |
| Results & Analytics | `docs/design/stitch-obsidian/resultados_y_anal_ticas_dark/code.html` |
| Exam Tracking | `docs/design/stitch-obsidian/seguimiento_de_ex_menes_dark/code.html` |
| Design System Guide | `docs/design/stitch-obsidian/obsidian/DESIGN.md` |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Page reload loses in-memory access token | Refresh interceptor transparently recovers it from the httpOnly cookie. UX impact: a brief loading state on first request after reload. |
| Concurrent 401s cause multiple refresh calls | Axios interceptor uses a promise queue: the first 401 triggers refresh, subsequent 401s wait on the same promise, then retry. |
| Permission map drifts from backend | The permission check is a function `hasPermission(userRoles, required)` — if the server denies a request (403), the interceptor redirects to Forbidden regardless of frontend state. Server is always authoritative. |
| Tailwind v4 CSS-first config is new to the team | Document the v4 migration pattern (`@import "tailwindcss"` + `@theme` block) in the project's design conventions. |
| No E2E tests in C-21 | All auth scenarios are covered by unit tests with mocked Axios. E2E tests require a running backend instance and are deferred to C-24. |
