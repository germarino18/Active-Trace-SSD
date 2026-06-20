## ADDED Requirements

### Requirement: Actividad como entidad de primera clase por dictado
El sistema SHALL modelar `Actividad` como entidad propia asociada a un `dictado_id`, con `nombre`, `tipo`, `fecha_limite`, `tenant_id` y los mixins de auditoría y soft delete del proyecto. La introducción MUST ser aditiva: `Calificacion.actividad : String` se mantiene y se agrega `Calificacion.actividad_id : FK → Actividad` nullable. El esquema MUST aplicarse en una única migración Alembic aditiva. Toda Actividad MUST estar acotada al `tenant_id` de la sesión.

#### Scenario: Actividad pertenece a un dictado y tenant
- **WHEN** se crea una Actividad
- **THEN** queda asociada al `dictado_id` indicado y al `tenant_id` de la sesión, con su `nombre`, `tipo` y `fecha_limite`

#### Scenario: Calificaciones existentes siguen funcionando
- **WHEN** existen calificaciones previas con `actividad_id` nulo
- **THEN** el sistema las sigue tratando por su string `actividad` sin error

### Requirement: CRUD de Actividad sin notas
El sistema SHALL permitir al PROFESOR crear una Actividad sin calificaciones todavía, listar las actividades de un dictado, editar su `fecha_limite` y darla de baja por soft delete. Estas operaciones MUST exigir el permiso `actividades:gestionar` (fail-closed: sin permiso, 403) y MUST estar acotadas al `tenant_id` de la sesión. El borrado MUST ser soft delete, nunca hard delete.

#### Scenario: Crear actividad sin calificaciones
- **WHEN** un PROFESOR con `actividades:gestionar` crea una actividad con nombre, tipo y fecha límite en un dictado de su tenant
- **THEN** el sistema crea la actividad sin requerir ninguna calificación asociada

#### Scenario: Listar actividades del dictado
- **WHEN** el PROFESOR lista las actividades de un dictado de su tenant
- **THEN** el sistema devuelve sólo las actividades vivas (no soft-deleted) de ese dictado

#### Scenario: Editar fecha límite
- **WHEN** el PROFESOR edita la `fecha_limite` de una actividad existente
- **THEN** el sistema persiste la nueva fecha y registra el cambio en auditoría

#### Scenario: Soft delete de actividad
- **WHEN** el PROFESOR da de baja una actividad
- **THEN** el sistema la marca como eliminada por soft delete y deja de listarla, sin borrarla físicamente

#### Scenario: Sin permiso es rechazado
- **WHEN** un usuario sin `actividades:gestionar` intenta crear, editar o borrar una actividad
- **THEN** el sistema responde 403 y no realiza ninguna operación

### Requirement: Calificaciones del profesor pueblan actividad string y actividad_id
El sistema SHALL garantizar que, cuando el PROFESOR carga o edita calificaciones asociadas a una Actividad, ambas columnas `Calificacion.actividad` (igual a `Actividad.nombre`) y `Calificacion.actividad_id` queden pobladas y consistentes.

#### Scenario: Carga consistente de ambas columnas
- **WHEN** el PROFESOR registra una calificación contra una Actividad
- **THEN** la calificación queda con `actividad_id` apuntando a esa Actividad y `actividad` igual a su `nombre`
