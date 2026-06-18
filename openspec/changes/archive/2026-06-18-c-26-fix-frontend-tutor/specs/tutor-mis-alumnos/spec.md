## ADDED Requirements

### Requirement: TUTOR puede ver listado de sus alumnos asignados
El sistema DEBE mostrar al TUTOR una página con todos los alumnos que tiene asignados, agrupados por materia/comisión. Los datos se obtienen del endpoint `GET /api/v1/tutor/alumnos` (backend existente).

#### Scenario: TUTOR accede a Mis Alumnos
- **WHEN** un TUTOR navega a `/tutor/alumnos`
- **THEN** el sistema DEBE mostrar una tabla con: nombre, apellido, email, materia, comisión, estado
- **AND** los datos DEBEN corresponder solo a los alumnos asignados a ese TUTOR

#### Scenario: TUTOR sin alumnos asignados
- **WHEN** un TUTOR sin alumnos asignados navega a `/tutor/alumnos`
- **THEN** el sistema DEBE mostrar un EmptyState con mensaje "No tenés alumnos asignados"

#### Scenario: La página carga datos correctamente
- **WHEN** la página se monta
- **THEN** el sistema DEBE llamar a `GET /api/v1/tutor/alumnos`
- **AND** mostrar un spinner mientras carga

### Requirement: Los alumnos se muestran con datos de contacto
La tabla DEBE incluir columnas de nombre, apellido, email, materia, comisión, y un botón de acción (ej: "Ver detalle").

#### Scenario: TUTOR ve datos de contacto
- **WHEN** un TUTOR ve la lista de alumnos
- **THEN** cada fila DEBE mostrar nombre, apellido, email
- **AND** DEBE haber un botón "Ver detalle" que navegue a `/alumno/{id}`
