## ADDED Requirements

### Requirement: ABM de evaluaciones
El sistema SHALL exponer CRUD de evaluaciones bajo `/api/v1/evaluaciones`, gated por `estructura:gestionar`. Una evaluación SHALL tener: tipo (`parcial`, `tp`, `coloquio`), instancia (número), fecha, título opcional, materia_id, cohorte_id. SHALL permitir alta, edición, listado y baja lógica.

#### Scenario: Crear evaluación
- **WHEN** un ADMIN crea una evaluación con tipo "parcial", instancia 1, fecha y materia_id
- **THEN** la evaluación se persiste asociada al tenant del usuario

#### Scenario: Listar evaluaciones por materia
- **WHEN** un ADMIN invoca `GET /api/v1/evaluaciones?materia_id={id}`
- **THEN** se devuelven solo las evaluaciones de esa materia en el tenant
