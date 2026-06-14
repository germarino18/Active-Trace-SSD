## ADDED Requirements

### Requirement: Asignacion links usuario, rol and academic context with validity
The system SHALL provide an `asignacion` table linking a `usuario` to a `rol` within an academic context, using BaseMixin, TenantMixin, SoftDeleteMixin and AuditMixin. Columns SHALL include `usuario_id` (FK → usuario), `rol` (one of ALUMNO|PROFESOR|TUTOR|COORDINADOR|NEXO|ADMIN|FINANZAS), nullable context `dictado_id`/`materia_id`/`carrera_id`/`cohorte_id` (all NULL means a tenant-global role), `comisiones` (list), `responsable_id` (FK → usuario, nullable), `desde` (date) and `hasta` (date, nullable = open). A user MAY have multiple asignaciones with different roles, contexts and periods.

#### Scenario: Tenant-global role assignment
- **WHEN** an asignacion is created with a `rol` and all context FKs NULL
- **THEN** it is persisted as a tenant-global role for that usuario

#### Scenario: Multiple roles per user
- **WHEN** a usuario has two asignaciones with different `rol` values, both vigente
- **THEN** both roles are present in the usuario's effective roles

#### Scenario: NEXO role is accepted with zero permissions
- **WHEN** an asignacion is created with `rol = NEXO`
- **THEN** it is persisted and resolves to zero permissions per the C-04 seed

### Requirement: estado_vigencia is derived, not stored
The system SHALL derive `estado_vigencia` (Vigente|Vencida) from dates and SHALL NOT store it as a column. An asignacion is Vigente when `desde <= today AND (hasta IS NULL OR today <= hasta)`, otherwise Vencida.

#### Scenario: Open-ended assignment is vigente
- **WHEN** an asignacion has `desde` in the past and `hasta` NULL
- **THEN** its derived `estado_vigencia` is Vigente

#### Scenario: Expired assignment is vencida
- **WHEN** an asignacion has `hasta` before today
- **THEN** its derived `estado_vigencia` is Vencida

### Requirement: Expired assignments are retained but grant no permissions
The system SHALL keep expired (Vencida) asignaciones in the historical record and SHALL NOT grant their roles when resolving effective permissions.

#### Scenario: Vencida does not authorize
- **WHEN** a usuario's only asignacion granting `rol = PROFESOR` is Vencida
- **THEN** the usuario's effective roles do NOT include PROFESOR

#### Scenario: Vencida is preserved
- **WHEN** an asignacion becomes Vencida
- **THEN** the row remains in the database (not deleted)

### Requirement: Asignacion is the source of truth for effective roles
The system SHALL compute a usuario's effective roles as the DISTINCT `rol` of its alive, Vigente asignaciones for the tenant. Context fields (dictado/materia/carrera/cohorte/comisiones) SHALL NOT narrow permission resolution in this change; RBAC remains tenant-global via the `rol_permiso` catalog.

#### Scenario: Effective roles come from vigente asignaciones
- **WHEN** resolving the effective roles of a usuario
- **THEN** the result is the DISTINCT set of `rol` from its alive Vigente asignaciones

#### Scenario: Context does not narrow permissions
- **WHEN** an asignacion has a `materia_id`/`carrera_id` context
- **THEN** the resolved permissions for that role are the same as the tenant-global ones

### Requirement: responsable_id models the supervisory hierarchy
The system SHALL allow an asignacion to reference a `responsable_id` (another usuario) to model who supervises the assigned person.

#### Scenario: Assignment with a responsible
- **WHEN** an asignacion is created with a `responsable_id` pointing to a usuario in the same tenant
- **THEN** the relationship is persisted and readable

### Requirement: CRUD for asignaciones gated by equipos:asignar
The system SHALL expose `/api/asignaciones` for create, read, update and soft-delete, gated by `require_permission("equipos:asignar")`, fail-closed. The permission `equipos:asignar` SHALL be added to the catalog and granted to COORDINADOR and ADMIN. Deletion SHALL be soft.

#### Scenario: Authorized caller manages asignaciones
- **WHEN** a caller with `equipos:asignar` creates an asignacion
- **THEN** it is persisted in the caller's tenant

#### Scenario: Caller without permission is rejected
- **WHEN** a caller lacking `equipos:asignar` calls any `/api/asignaciones` endpoint
- **THEN** the response is 403 Forbidden and no change is made

#### Scenario: equipos:asignar is seeded for the expected roles
- **WHEN** the catalog is inspected after migration
- **THEN** `equipos:asignar` exists and is granted to COORDINADOR and ADMIN
