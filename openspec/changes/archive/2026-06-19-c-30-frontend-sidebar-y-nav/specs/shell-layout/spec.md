## MODIFIED Requirements

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
