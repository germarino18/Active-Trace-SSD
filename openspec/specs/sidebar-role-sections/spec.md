## ADDED Requirements

### Requirement: Sidebar organizes items into role-based sections
The system SHALL group sidebar navigation items into named sections by role, using the `SidebarSection` type (`{ label?: string; items: MenuItem[] }`).

#### Scenario: Sections rendered with label
- **WHEN** a `SidebarSection` has a `label` field
- **THEN** the sidebar renders a visible section heading before that section's items

#### Scenario: Sections rendered without label
- **WHEN** a `SidebarSection` has no `label` field
- **THEN** the sidebar renders the items without a section heading

### Requirement: Empty sections are hidden
The system SHALL hide a section (including its label) when all of its items are invisible due to permission filtering.

#### Scenario: All items in section require missing permissions
- **WHEN** all `MenuItem` entries in a section have `requiredPermissions` that the current user does not hold
- **THEN** neither the section label nor any item from that section SHALL appear in the DOM

#### Scenario: At least one item is visible
- **WHEN** at least one `MenuItem` in a section has its permissions satisfied (or has no `requiredPermissions`)
- **THEN** the section label (if present) SHALL be rendered

### Requirement: ALUMNO section shows only student items
The system SHALL render a dedicated ALUMNO section containing: Dashboard, Mis Materias, Coloquios, Avisos, Programas, Calendario, Mensajes, Comunicaciones — all gated on `estado-academico:ver` or `evaluacion:reservar` or `inbox:ver` or `avisos:confirmar`.

#### Scenario: ALUMNO user sees student section
- **WHEN** the current user holds `estado-academico:ver` permission
- **THEN** the ALUMNO section items SHALL be visible
- **THEN** no DOCENTE, COORDINACIÓN, NEXO, FINANZAS, or ADMIN section items SHALL be visible

#### Scenario: Non-ALUMNO user does not see student section
- **WHEN** the current user does NOT hold `estado-academico:ver` permission
- **THEN** the ALUMNO section SHALL be entirely hidden

### Requirement: NEXO section shows read-only items scoped to career
The system SHALL render a NEXO section containing: Atrasados (nexo), Encuentros (nexo), Tareas (nexo) — each gated on `nexo:atrasados:ver`, `nexo:encuentros:ver`, `nexo:tareas:ver` respectively.

#### Scenario: NEXO user sees NEXO section
- **WHEN** the current user holds at least one `nexo:*:ver` permission
- **THEN** the NEXO section SHALL appear with only the items whose permissions are satisfied

#### Scenario: Non-NEXO user does not see NEXO section
- **WHEN** the current user holds no `nexo:*` permission
- **THEN** the NEXO section SHALL be entirely hidden

### Requirement: No duplicate items across sections
The system SHALL not render the same label or route more than once in the visible sidebar.

#### Scenario: No duplicate Dashboard items
- **WHEN** the sidebar renders for any user
- **THEN** at most one item with label "Dashboard" SHALL be visible
- **THEN** at most one item with label "Avisos" SHALL be visible
- **THEN** at most one item with label "Coloquios" SHALL be visible

### Requirement: ADMIN sees all operational views
The system SHALL show the ADMIN role all sidebar items from the Docente and Coordinación sections, in addition to the Admin section. ADMIN is not limited to structural/admin views only.

#### Scenario: ADMIN user sees docente and coordinación views
- **WHEN** the current user holds permissions such as `atrasados:ver`, `entregas:ver`, `guardias:gestionar`, `equipos:ver`, `tareas:ver`
- **THEN** the corresponding sidebar items SHALL be visible regardless of whether the user also has the ADMIN role

#### Scenario: ADMIN does not see ALUMNO section
- **WHEN** the current user does NOT hold `estado-academico:ver`
- **THEN** the ALUMNO section SHALL be entirely hidden even for ADMIN users

### Requirement: Sidebar permissions are role-agnostic capability strings
The system SHALL use permission strings that describe capabilities (`modulo:accion`), not the role that holds them. Permissions shared across multiple roles SHALL NOT carry a role prefix.

#### Scenario: Shared permissions have no role prefix
- **WHEN** a permission is held by more than one role (e.g., TUTOR and ADMIN)
- **THEN** the permission string SHALL be `entregas:ver`, `alumnos:ver`, or `guardias:gestionar` — not `tutor:entregas:ver`, `tutor:alumnos:ver`, or `tutor:guardias:gestionar`

#### Scenario: Role-scoped permissions carry a prefix only when scope differs
- **WHEN** a permission grants a genuinely different scope per role (e.g., NEXO has career-scoped read-only access)
- **THEN** a prefix MAY be used to distinguish the scope: `nexo:atrasados:ver`

### Requirement: Atrasados and Comunicación use correct routes
The system SHALL navigate to `/atrasados` and `/comunicacion` respectively. Both routes SHALL be registered in the router and render functional pages — not 404.

#### Scenario: Atrasados route
- **WHEN** a user with `atrasados:ver` clicks the "Atrasados" item in the sidebar
- **THEN** the router SHALL navigate to `/atrasados` and render `AtrasadosGeneralPage`

#### Scenario: Comunicación route
- **WHEN** a user with `comunicacion:ver` clicks the "Comunicación" item in the sidebar
- **THEN** the router SHALL navigate to `/comunicacion` and render `ComunicacionGeneralPage`

### Requirement: NEXO routes are registered and render stub pages
The system SHALL register `/nexo/atrasados`, `/nexo/encuentros`, `/nexo/tareas` as valid routes in the router. Each SHALL render a stub page (not 404) when accessed by a user with the corresponding NEXO permission.

#### Scenario: NEXO sidebar items do not produce 404
- **WHEN** a user with any `nexo:*:ver` permission clicks a NEXO sidebar item
- **THEN** the router SHALL navigate to the corresponding `/nexo/*` route and render a stub page without a 404 error

### Requirement: Secciones docentes incluyen ítem "Mensajes" con badge de no-leídos

Las secciones del sidebar correspondientes a TUTOR, PROFESOR, COORDINADOR y ADMIN SHALL incluir un ítem "Mensajes" que navega a `/inbox`, protegido con el permiso `inbox:acceder`. El ítem SHALL mostrar un badge numérico con el conteo de hilos `no_leido: true` cuando `unreadCount > 0`, obtenido de `useInbox().unreadCount`.

#### Scenario: Usuario con mensajes sin leer ve badge en sidebar
- **WHEN** el usuario tiene `inbox:acceder` y `useInbox().unreadCount > 0`
- **THEN** el ítem "Mensajes" en el sidebar muestra un badge con el número de hilos sin leer

#### Scenario: Usuario sin mensajes sin leer no ve badge
- **WHEN** el usuario tiene `inbox:acceder` y `useInbox().unreadCount === 0`
- **THEN** el ítem "Mensajes" en el sidebar no muestra badge

#### Scenario: Usuario sin permiso inbox:acceder no ve el ítem
- **WHEN** el usuario no tiene `inbox:acceder`
- **THEN** el ítem "Mensajes" no aparece en ninguna sección del sidebar

