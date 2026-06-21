## ADDED Requirements

### Requirement: Bases de Datos seed dictado uses the actividad-row calificación format
The "Bases de Datos" dictado in `seed_dev.py` SHALL create proper `actividad` rows and link its calificaciones via `actividad_id`, mirroring the "Programación I" dictado's format, instead of inserting calificaciones with only the legacy `actividad` string and no `actividad_id`.

#### Scenario: Seeded Bases de Datos calificaciones reference actividad rows
- **WHEN** `seed_dev.py` is run
- **THEN** the "Bases de Datos" dictado SHALL have one or more `actividad` rows
- **AND** each of its calificaciones SHALL be linked to an actividad via `actividad_id`
- **AND** no calificación in that dictado SHALL rely solely on the legacy `actividad` string

#### Scenario: Both seed dictados share the same format
- **WHEN** the seeded data is inspected after running `seed_dev.py`
- **THEN** the "Bases de Datos" dictado and the "Programación I" dictado SHALL both use the actividad-row + `actividad_id` calificación format
