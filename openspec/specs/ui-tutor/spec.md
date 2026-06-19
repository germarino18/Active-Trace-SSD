## ADDED Requirements

### Requirement: Alumnos asignados al tutor
`TutorAlumnosPage` SHALL mostrar la lista de alumnos bajo tutoría del usuario autenticado. Cada alumno SHALL mostrar: nombre, legajo, carrera, y un indicador de estado académico (al día / en riesgo). Permite navegar al detalle de cada alumno.

#### Scenario: Lista de alumnos
- **WHEN** el tutor tiene alumnos asignados
- **THEN** se muestran en tabla o lista con indicador visual de estado

#### Scenario: Alumno en riesgo
- **WHEN** un alumno tiene promedio por debajo del umbral o actividades atrasadas
- **THEN** se muestra badge "En riesgo" en color error del DS

#### Scenario: Sin alumnos asignados
- **WHEN** el tutor no tiene alumnos
- **THEN** se muestra `EmptyState` con mensaje descriptivo

---

### Requirement: Guardias del tutor
`GuardiasListPage` SHALL mostrar las guardias asignadas al tutor (fecha, horario, aula/virtual, estado). MUST diferenciar guardias futuras de pasadas visualmente.

#### Scenario: Guardias próximas
- **WHEN** hay guardias programadas en el futuro
- **THEN** se listan primero y con badge "Próxima"

#### Scenario: Sin guardias
- **WHEN** no hay guardias asignadas
- **THEN** se muestra `EmptyState` con mensaje apropiado

---

### Requirement: Entregas sin corregir del tutor
`TutorEntregasSinCorregirPage` SHALL listar las entregas de los alumnos asignados al tutor que no tienen corrección. Equivalente al tab de entregas del flujo académico pero scoped al tutor.

#### Scenario: Con entregas pendientes
- **WHEN** existen entregas sin corregir de alumnos del tutor
- **THEN** se listan con alumno, materia, actividad, y fecha de entrega

#### Scenario: Sin pendientes
- **WHEN** no hay entregas sin corregir
- **THEN** se muestra `EmptyState` con mensaje positivo
