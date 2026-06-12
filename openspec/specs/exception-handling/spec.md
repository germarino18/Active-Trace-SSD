## ADDED Requirements

### Requirement: AppException base hierarchy
The system SHALL define an `AppException` base class that all domain exceptions inherit from, with `message: str`, `code: str`, and `details: dict | None` attributes.

#### Scenario: AppException with all fields
- **WHEN** raising `AppException(message="Something went wrong", code="app_error", details={"key": "value"})`
- **THEN** the exception carries message, code, and details accessible as attributes

### Requirement: Specialized exception subclasses
The system SHALL define the following exception subclasses:
- `NotFoundException` (code: "not_found", HTTP 404)
- `ForbiddenException` (code: "forbidden", HTTP 403)
- `TenantMismatchException` (code: "tenant_mismatch", HTTP 403)
- `ValidationException` (code: "validation_error", HTTP 422)

#### Scenario: NotFoundException with default code
- **WHEN** raising `NotFoundException(resource="User", id=some_uuid)`
- **THEN** the message is "User <uuid> not found" and code is "not_found"

#### Scenario: ForbiddenException raised
- **WHEN** raising `ForbiddenException(action="delete_user")`
- **THEN** the message includes the action and code is "forbidden"

#### Scenario: TenantMismatchException raised
- **WHEN** raising `TenantMismatchException()`
- **THEN** the message indicates tenant mismatch and code is "tenant_mismatch"

### Requirement: Global exception handlers return standardized JSON
The system SHALL register FastAPI exception handlers that catch `AppException` and return standardized JSON responses with appropriate HTTP status codes.

#### Scenario: NotFoundException returns 404 JSON
- **WHEN** a route raises `NotFoundException(resource="Tenant", id=some_uuid)`
- **THEN** the response is HTTP 404 with body `{"error": {"code": "not_found", "message": "Tenant <uuid> not found", "details": null}}`

#### Scenario: ValidationException returns 422 JSON
- **WHEN** a route raises `ValidationException(message="Invalid data", details={"field": "name"})`
- **THEN** the response is HTTP 422 with body containing error details

#### Scenario: Unhandled exception returns 500
- **WHEN** a route raises an unexpected Python exception (not AppException)
- **THEN** the response is HTTP 500 with a generic error message (no stack trace leaked)
