## ADDED Requirements

### Requirement: Equipo docente del profesor por dictado compartido
El sistema SHALL exponer, para un dictado dado, los compañeros de equipo docente del PROFESOR autenticado: otros usuarios con rol PROFESOR o TUTOR que tengan una `Asignacion` vigente al MISMO `dictado_id` (misma materia × carrera × cohorte), no sólo a la misma materia. La consulta MUST derivar el `tenant_id` de la sesión y MUST excluir asignaciones vencidas y soft-deleted. El usuario solicitante MUST tener una asignación vigente al dictado para verlo.

#### Scenario: Compañeros del mismo dictado
- **WHEN** un PROFESOR consulta el equipo docente de un dictado donde tiene asignación vigente
- **THEN** el sistema devuelve los PROFESOR/TUTOR con asignación vigente al mismo `dictado_id`, acotado a su tenant

#### Scenario: No incluye docentes de otra cohorte de la misma materia
- **WHEN** existe un docente asignado a la misma materia pero a otra cohorte (otro dictado)
- **THEN** ese docente no aparece en el equipo del dictado consultado

#### Scenario: Excluye asignaciones vencidas
- **WHEN** un docente tuvo una asignación al dictado que ya venció
- **THEN** ese docente no aparece en el equipo del dictado

#### Scenario: Aislamiento de tenant
- **WHEN** se consulta el equipo de un dictado de otro tenant
- **THEN** el sistema responde 404 y no entrega datos
