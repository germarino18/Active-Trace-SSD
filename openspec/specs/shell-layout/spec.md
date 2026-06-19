## ADDED Requirements

### Requirement: Layout has a responsive sidebar
The system SHALL render a sidebar navigation panel that adapts to screen size.

#### Scenario: Desktop sidebar
- **WHEN** the viewport is wider than 1024px
- **THEN** the sidebar is visible as a fixed left panel (w-64)
- **THEN** the sidebar shows the application logo, navigation menu items, and user info at the bottom

#### Scenario: Mobile collapsed sidebar
- **WHEN** the viewport is 1024px or narrower
- **THEN** the sidebar is hidden by default
- **THEN** a hamburger button in the header toggles the sidebar visibility
- **THEN** clicking a menu item closes the sidebar on mobile

### Requirement: Layout has a top header bar
The system SHALL render a top header with breadcrumbs and user menu.

#### Scenario: Header elements
- **WHEN** the layout renders
- **THEN** the header shows breadcrumbs indicating the current page path
- **THEN** the header shows a user dropdown menu with the user's name and avatar (initials)
- **THEN** the user dropdown contains "Mi Perfil" and "Cerrar sesión" options

### Requirement: Sidebar menu adapts to user permissions
The system SHALL show or hide sidebar menu items based on the current user's roles and permissions. Items SHALL be organized into named sections (`SidebarSection[]`); a section is hidden in its entirety when all of its items fail the permission check.

#### Scenario: Menu filtered by permissions
- **WHEN** the sidebar renders
- **THEN** only menu items whose `requiredPermissions` are satisfied by the current user SHALL be shown
- **WHEN** a user has no matching permissions for any menu item in a section
- **THEN** that section header SHALL be hidden

#### Scenario: Items without requiredPermissions are always visible
- **WHEN** a `MenuItem` has no `requiredPermissions` field (or an empty array)
- **THEN** that item SHALL always be visible regardless of the current user's permissions

### Requirement: Breadcrumbs reflect current route
The system SHALL display breadcrumbs that show the navigation path from home to the current page.

#### Scenario: Breadcrumb rendering
- **WHEN** the user navigates to a page
- **THEN** breadcrumbs display the hierarchy of the current route, with each segment being a clickable link
- **THEN** the last segment (current page) is rendered as plain text, not a link

### Requirement: Layout shows a loading state on initial auth check
The system SHALL display a full-screen loading indicator while verifying the user's session on application load.

#### Scenario: Initial auth check loading
- **WHEN** the application loads and no session is yet verified
- **THEN** a centered spinner or skeleton is shown
- **WHEN** the auth check completes (session valid or not)
- **THEN** the loading state is replaced by the layout (authenticated) or login page (unauthenticated)

### Requirement: Layout shows a 404 page for unknown routes
The system SHALL display a "Page Not Found" page when the user navigates to a route that does not match any defined page.

#### Scenario: Unknown route
- **WHEN** the user navigates to a URL that does not match any route
- **THEN** a "404 — Página no encontrada" page is displayed
- **THEN** a "Volver al inicio" link is shown
