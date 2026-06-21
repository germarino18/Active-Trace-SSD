## ADDED Requirements

### Requirement: Padrón read paths exclude soft-deleted entries
The system SHALL exclude soft-deleted padrón entries (`deleted_at IS NOT NULL`) from every padrón read path. `EntradaPadronRepository.find_by_version()` and `EntradaPadronRepository.count_by_version()` SHALL apply the soft-delete filter in addition to the tenant scope, exactly as `BaseRepository.find_by_id` and `find_all` do. Soft-deleted calificaciones SHALL continue to persist by design; only the requirement that they no longer be listed is added here.

#### Scenario: Soft-deleted alumno disappears from the padrón list
- **WHEN** a PROFESOR removes an alumno (single or bulk baja, setting `deleted_at`) and the padrón is read again
- **THEN** `find_by_version` SHALL NOT return that entry
- **AND** the alumnos list, the actividades view, and the atrasados view SHALL NOT show that alumno

#### Scenario: Count reflects the removal
- **WHEN** an alumno entry is soft-deleted
- **THEN** `count_by_version` SHALL return a count that excludes the soft-deleted entry

#### Scenario: Non-deleted entries are unaffected
- **WHEN** the padrón contains both active and soft-deleted entries
- **THEN** `find_by_version` and `count_by_version` SHALL return exactly the active entries, scoped to the tenant
- **AND** entries belonging to another tenant SHALL never be returned

#### Scenario: Regression test runs against a real database
- **WHEN** the regression test for this fix is written
- **THEN** it SHALL use a real or ephemeral test database (NO database mocks)
- **AND** it SHALL fail (RED) against the pre-fix code that omits the soft-delete filter, and pass (GREEN) once the filter is applied to both methods
