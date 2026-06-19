## MODIFIED Requirements

### Requirement: Atrasados and Comunicación use correct routes
The system SHALL navigate to `/atrasados` and `/comunicacion` respectively when the user clicks those sidebar items. Both routes SHALL be registered in the router and render functional pages — not 404.

#### Scenario: Atrasados route
- **WHEN** a user with `atrasados:ver` clicks the "Atrasados" item in the sidebar
- **THEN** the router SHALL navigate to `/atrasados`
- **THEN** the system SHALL render `AtrasadosGeneralPage` (not a 404)

#### Scenario: Comunicación route
- **WHEN** a user with `comunicacion:ver` clicks the "Comunicación" item in the sidebar
- **THEN** the router SHALL navigate to `/comunicacion`
- **THEN** the system SHALL render `ComunicacionGeneralPage` (not a 404)

## ADDED Requirements

### Requirement: NEXO routes are registered and render stub pages
The system SHALL register `/nexo/atrasados`, `/nexo/encuentros`, `/nexo/tareas` as valid routes in the router. Each SHALL render a stub page (not 404) when accessed by a user with the corresponding NEXO permission.

#### Scenario: NEXO sidebar items do not produce 404
- **WHEN** a user with any `nexo:*:ver` permission clicks a NEXO sidebar item
- **THEN** the router SHALL navigate to the corresponding `/nexo/*` route
- **THEN** the page SHALL render without a 404 error
