## Why

The entire backend (20 changes, C-01 through C-20) is complete and deployed. There is no frontend — the platform cannot be used by end users. C-21 is the foundation frontend shell: scaffolding, authentication flow, layout, route guards, and HTTP client. Without it, no subsequent frontend feature (C-22 through C-24) can be built or tested.

## What Changes

- **Greenfield React 18 + TypeScript + Vite project** under `frontend/` with feature-based modules structure
- **Centralized Axios HTTP client** with auth interceptors and transparent token refresh
- **Auth screens**: Login (email + password + tenant), 2FA verification, Forgot Password, Reset Password
- **Auth guard** component that protects routes based on session presence and permission requirements
- **Layout shell** with responsive sidebar, top header, breadcrumbs, and user menu
- **Permission-based navigation menu** that adapts to the current user's roles
- **Logout flow** that revokes the session server-side and clears local state
- **TanStack Query** for server state management (auth queries, user profile)
- **React Hook Form + Zod** for form validation on auth screens
- **Docker Compose** integration for frontend dev server alongside the existing backend
- A full test suite covering login render, auth flow (mocked), guard redirects, and transparent refresh

### What is OUT of scope (deferred to C-22, C-23, C-24)
- Domain feature pages (students, courses, commissions, calendar, etc.)
- Dashboard widgets or metrics
- CRUD tables and management interfaces
- Any backend changes

## Capabilities

### New Capabilities

- `auth`: Login, 2FA, password recovery, logout, session management with JWT tokens (access + refresh rotation)
- `shell-layout`: Responsive layout with sidebar, header, breadcrumbs, user menu
- `route-guard`: Role/permission-based route protection with redirect to login or forbidden page
- `http-client`: Centralized Axios instance with transparent refresh, 401 interception, request/response typing

### Modified Capabilities

*(None — first frontend change, no existing specs to modify)*

## Impact

- New `frontend/` directory with full React 18 + TypeScript + Vite scaffold
- New Docker Compose service for the frontend dev server
- New GitHub Actions workflow (or updated existing) for frontend lint/test/build
- No backend changes required — consumes existing endpoints as-is
- Dependencies added: React 18, TanStack Query v5, React Hook Form, Zod, Axios, Tailwind CSS v4, react-router-dom v6
