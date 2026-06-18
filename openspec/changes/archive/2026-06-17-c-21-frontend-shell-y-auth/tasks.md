## 1. Project Scaffolding

- [x] 1.1 Initialize Vite project with React + TypeScript template in `frontend/`
- [x] 1.2 Install dependencies: react-router-dom, axios, @tanstack/react-query, react-hook-form, @hookform/resolvers, zod, tailwindcss v4
- [x] 1.3 Configure Tailwind CSS v4 with `@import "tailwindcss"` and design tokens
- [x] 1.4 Configure Vite proxy to forward `/api/*` to the backend dev server
- [x] 1.5 Create directory structure: `features/`, `shared/services/`, `shared/components/`, `shared/hooks/`, `shared/types/`
- [x] 1.6 Create base TypeScript types (`User`, `AuthTokens`, `ApiResponse<T>`, `Permissions`) in `shared/types/`
- [x] 1.7 Set up ESLint and tsconfig for the project conventions (no `any`, strict mode)

## 2. Shared HTTP Client

- [x] 2.1 Create Axios instance in `shared/services/api.ts` with base config (baseURL, timeout, default headers)
- [x] 2.2 Implement request interceptor to attach `Authorization: Bearer <token>` and `X-Tenant-ID` header
- [x] 2.3 Implement response interceptor with transparent refresh logic (single refresh queue for concurrent 401s)
- [x] 2.4 Create typed wrapper functions (`api.get<T>()`, `api.post<T>()`, `api.patch<T>()`, `api.delete<T>()`)
- [x] 2.5 Create auth-specific API service in `features/auth/services/auth.service.ts`

## 3. Auth Feature — Context and Hooks

- [x] 3.1 Create `AuthContext` with provider wrapping the app root
- [x] 3.2 Implement `useAuth` hook that exposes session state, login, logout, refresh functions
- [x] 3.3 Store access token in memory (React state inside AuthContext provider)
- [x] 3.4 Create TanStack Query hook `useCurrentUser` to fetch GET `/api/auth/me`
- [x] 3.5 Wire AuthContext to the HTTP client interceptor (token source for request interceptor)
- [x] 3.6 Implement initial auth check on app load (attempt refresh, fetch profile if valid)
- [x] 3.7 Create AuthGuard and GuestGuard components

## 4. Auth Feature — Login and 2FA Pages

- [x] 4.1 Create `LoginPage` in `features/auth/pages/LoginPage.tsx` with email + password + tenant fields
- [x] 4.2 Implement Zod schema for login form validation (email, password min length, tenant required)
- [x] 4.3 Integrate React Hook Form with Zod resolver on login form
- [x] 4.4 Handle login response: navigate to home on success, handle 2FA challenge flow, show errors
- [x] 4.5 Create `TwoFactorPage` with TOTP code input field
- [x] 4.6 Implement Zod schema for 2FA form (6-digit code required)
- [x] 4.7 Handle 2FA verification: submit challenge_token + code, navigate to home on success

## 5. Auth Feature — Password Recovery Pages

- [x] 5.1 Create `ForgotPasswordPage` with email + tenant fields and Zod validation
- [x] 5.2 Handle forgot password submission: POST `/api/auth/forgot`, show success message, link back to login
- [x] 5.3 Create `ResetPasswordPage` that reads the token from URL query params
- [x] 5.4 Implement password + confirmation fields with Zod validation (min length, match)
- [x] 5.5 Handle reset submission: POST `/api/auth/reset`, show success message, redirect to login

## 6. Layout and Navigation

- [x] 6.1 Create `AppLayout` component with sidebar + header + main content area
- [x] 6.2 Implement responsive sidebar (visible on desktop, toggleable on mobile via hamburger button)
- [x] 6.3 Create header component with user avatar (initials), name, and dropdown menu
- [x] 6.4 Implement breadcrumb component that reads route hierarchy from react-router
- [x] 6.5 Create sidebar menu with declarative `MenuItem[]` configuration
- [x] 6.6 Filter sidebar menu items based on user permissions (hide items without required permissions)
- [x] 6.7 Create loading spinner component for initial auth check
- [x] 6.8 Create NotFoundPage (404) and ForbiddenPage (403) components

## 7. App Shell and Routing

- [x] 7.1 Set up react-router with `createBrowserRouter` and nested routes
- [x] 7.2 Configure route tree: `GuestGuard → AuthPages` | `AuthGuard → AppLayout → DomainPages`
- [x] 7.3 Wire auth redirects: preserve `?redirect=` param and navigate after login
- [x] 7.4 Wire AuthContext provider at the app root level
- [x] 7.5 Wire TanStack Query provider at the app root level
- [x] 7.6 Create a placeholder home page (will be replaced by dashboard in C-22)

## 8. Logout Flow

- [x] 8.1 Implement logout handler: POST `/api/auth/logout` → clear in-memory token → navigate to login
- [x] 8.2 Add "Cerrar sesión" option to user dropdown in header
- [x] 8.3 Handle 401 interceptor: if refresh fails, trigger logout (clear tokens + redirect)

## 9. Tests

- [x] 9.1 Set up Vitest + React Testing Library with test configuration
- [x] 9.2 Write test: LoginPage renders all form fields (email, password, tenant)
- [x] 9.3 Write test: Login flow with mocked Axios — successful login navigates to home
- [x] 9.4 Write test: Login flow with mocked Axios — invalid credentials shows error
- [x] 9.5 Write test: Login flow with mocked Axios — 2FA required shows 2FA form
- [x] 9.6 Write test: TwoFactorPage — valid code submits challenge, invalid code shows error
- [x] 9.7 Write test: AuthGuard redirects to login when no session
- [x] 9.8 Write test: AuthGuard renders children when session exists
- [x] 9.9 Write test: AuthGuard shows forbidden page when user lacks required permission
- [x] 9.10 Write test: Axios interceptor transparent refresh on 401 (single refresh for concurrent requests)
- [x] 9.11 Write test: ForgotPassword — successful submission shows confirmation message
- [x] 9.12 Write test: ResetPassword — valid submission redirects to login

## 10. Docker and CI

- [x] 10.1 Create `frontend/Dockerfile.dev` with node:20-alpine + Vite dev server
- [x] 10.2 Update root `docker-compose.yml` to add the frontend service on port 5173
- [x] 10.3 Create `frontend/.dockerignore` excluding node_modules, dist
- [x] 10.4 Create or update GitHub Actions workflow for frontend lint + typecheck + test + build
