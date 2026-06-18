## ADDED Requirements

### Requirement: Vista de estado académico por materia
El sistema SHALL mostrar al alumno el detalle de sus calificaciones y actividades por materia.

#### Scenario: Vista muestra calificaciones y actividades
- **WHEN** el alumno autenticado accede a `/alumno/materias/:id`
- **THEN** el sistema MUST mostrar: nombre de la materia, lista de actividades con nota y estado (aprobado/desaprobado/pendiente), promedio general, indicador de condición (regular/libre/promovido)
- **AND** el sistema MUST consumir los endpoints existentes de `C-10`/`C-11`

#### Scenario: Vista sin calificaciones muestra estado vacío
- **WHEN** el alumno accede a una materia sin calificaciones cargadas
- **THEN** el sistema MUST mostrar "Aún no hay calificaciones para esta materia"

#### Scenario: Vista rechaza acceso a materia no asignada
- **WHEN** el alumno accede a una materia a la que no está asignado
- **THEN** el sistema MUST redirigir a 403 Forbidden

### Requirement: Listado de materias del alumno
El sistema SHALL listar las materias en las que el alumno está inscripto.

#### Scenario: Listado muestra materias del período
- **WHEN** el alumno autenticado accede a `/alumno/materias`
- **THEN** el sistema MUST mostrar una lista con todas las materias del período actual
- **AND** cada item MUST incluir: nombre, profesor, estado general (indicador visual)
