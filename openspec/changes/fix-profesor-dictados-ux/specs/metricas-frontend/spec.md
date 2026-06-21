## ADDED Requirements

### Requirement: Dictado métricas carry the dictado human name
The dictado métricas response (`GET /api/v1/profesor/dictados/{id}/metricas`) SHALL additionally expose `materia_nombre` and `cohorte_nombre`, resolved by joining `Dictado→Materia` and `Dictado→Cohorte`, so the PROFESOR dictado views can display a human dictado name. The join SHALL be tenant-scoped and read-only (no schema change); the existing métricas fields SHALL be preserved.

#### Scenario: Métricas response includes materia and cohorte names
- **WHEN** a PROFESOR requests métricas for one of their dictados
- **THEN** the response SHALL include `materia_nombre` and `cohorte_nombre` alongside the existing metric fields
- **AND** the names SHALL come from the dictado's related Materia and Cohorte within the same tenant

#### Scenario: Frontend type and hook expose the names
- **WHEN** the frontend reads the métricas response
- **THEN** the `DictadoMetricas` type SHALL include `materia_nombre` and `cohorte_nombre`
- **AND** a hook SHALL expose the dictado name (`Materia — Cohorte`) for the header and breadcrumb to consume
