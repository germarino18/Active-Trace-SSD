## ADDED Requirements

### Requirement: TenantContext propagates tenant_id through request chain
The system SHALL provide a `TenantContext` class using Python `contextvars` to propagate the current tenant UUID across async boundaries without requiring a FastAPI Request object.

#### Scenario: Set and get tenant in same context
- **WHEN** setting a tenant UUID via `TenantContext.set(uuid)` in the same async context
- **THEN** `TenantContext.get()` returns that same UUID

#### Scenario: Tenant isolation between concurrent contexts
- **WHEN** setting tenant A in one coroutine and tenant B in another concurrent coroutine
- **THEN** each coroutine sees only its own tenant UUID, with no cross-contamination

#### Scenario: Reset clears tenant context
- **WHEN** calling `TenantContext.reset()` after setting a tenant
- **THEN** `TenantContext.get()` returns None

#### Scenario: Default value is None
- **WHEN** querying `TenantContext.get()` before any set() call
- **THEN** None is returned

### Requirement: FastAPI dependency resolves tenant_id from context/header
The system SHALL provide a `get_tenant_id()` FastAPI dependency that returns the current tenant UUID, resolving from:
1. `TenantContext` if already set (e.g., by middleware)
2. `X-Tenant-ID` header as fallback (until JWT provides tenant in C-03)

#### Scenario: Tenant resolved from context
- **WHEN** `TenantContext.set(uuid)` was called before the dependency runs
- **THEN** `get_tenant_id()` returns that UUID

#### Scenario: Tenant resolved from header fallback
- **WHEN** TenantContext has no value AND request has `X-Tenant-ID` header with a valid UUID
- **THEN** `get_tenant_id()` returns the UUID from the header

#### Scenario: Missing tenant raises TenantMismatchException
- **WHEN** TenantContext has no value AND no `X-Tenant-ID` header is present
- **THEN** `get_tenant_id()` raises a TenantMismatchException

### Requirement: Tenant middleware sets context from authenticated session
The system SHALL provide a FastAPI middleware that extracts the tenant_id from the authenticated session (JWT in C-03, header for now) and sets it in TenantContext before the request handler runs.

#### Scenario: Middleware sets tenant context
- **WHEN** a request arrives with a valid tenant identifier
- **THEN** the middleware sets TenantContext before the route handler executes

#### Scenario: Middleware resets tenant context after request
- **WHEN** a request completes (success or failure)
- **THEN** the middleware resets TenantContext to None, preventing leakage to the next request
