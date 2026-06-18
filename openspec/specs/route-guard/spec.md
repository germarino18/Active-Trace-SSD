## ADDED Requirements

### Requirement: Route guard checks authentication
The system SHALL protect routes by verifying the user has a valid session before rendering the page.

#### Scenario: Authenticated user can access protected route
- **WHEN** a user with a valid session navigates to a protected route
- **THEN** the `AuthGuard` renders the child component

#### Scenario: Unauthenticated user is redirected to login
- **WHEN** a user without a valid session navigates to a protected route
- **THEN** the `AuthGuard` redirects to the login page
- **THEN** the original URL is preserved in the query string (`?redirect=/original-path`)

### Requirement: Route guard checks permissions
The system SHALL restrict access to routes based on required permissions.

#### Scenario: User with permission can access route
- **WHEN** a user with the required permission navigates to a permission-protected route
- **THEN** the `AuthGuard` renders the child component

#### Scenario: User without permission sees forbidden page
- **WHEN** a user without the required permission navigates to a permission-protected route
- **THEN** the `AuthGuard` renders a "403 Forbidden" page with a message "No tiene permisos para acceder a esta sección"
- **THEN** a "Volver al inicio" link is shown

#### Scenario: Menu items hidden without permission
- **WHEN** the sidebar menu is rendered
- **THEN** menu items whose required permissions the user lacks SHALL be hidden
- **THEN** the user SHALL NOT see links to routes they cannot access

### Requirement: Guest-only routes redirect to home
The system SHALL redirect authenticated users away from guest-only pages (login, forgot password).

#### Scenario: Authenticated user on login page
- **WHEN** an authenticated user navigates to the login page
- **THEN** the `GuestGuard` redirects to the home page
