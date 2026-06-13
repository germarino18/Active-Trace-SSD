## ADDED Requirements

### Requirement: Acceso restringido por permiso estructura:gestionar
Todos los endpoints de ABM de estructura académica (`/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias`, `/api/admin/dictados`) MUST exigir el permiso `estructura:gestionar`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada, nunca desde la URL, body o headers. Fail-closed: sin el permiso, la respuesta MUST ser 403.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario cuyos roles no incluyen `estructura:gestionar` invoca cualquier endpoint de estructura académica
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: Usuario ADMIN accede
- **WHEN** un usuario con rol ADMIN (que tiene `estructura:gestionar`) invoca un endpoint de estructura académica
- **THEN** la operación se ejecuta acotada al `tenant_id` de su sesión

### Requirement: ABM de Carrera con unicidad de código por tenant
El sistema SHALL permitir alta, edición, baja (soft delete), listado y cambio de estado (Activa/Inactiva) de carreras. El par `(tenant_id, codigo)` MUST ser único entre las carreras vivas (no eliminadas). Una carrera nace en estado Activa.

#### Scenario: Alta de carrera
- **WHEN** un administrador crea una carrera con código y nombre válidos
- **THEN** la carrera se persiste con `tenant_id` de la sesión y estado Activa

#### Scenario: Código duplicado en el mismo tenant
- **WHEN** se intenta crear una carrera con un `codigo` que ya existe (viva) en el mismo tenant
- **THEN** el sistema rechaza la operación con un error de validación (422) y no crea el registro

#### Scenario: Reúso de código tras baja
- **WHEN** una carrera fue dada de baja (soft delete) y se crea otra con el mismo `codigo`
- **THEN** la operación es exitosa porque la unicidad sólo cuenta registros vivos

#### Scenario: Cambio de estado a Inactiva
- **WHEN** un administrador cambia el estado de una carrera a Inactiva
- **THEN** la carrera queda Inactiva y se conserva (no se borra físicamente)

### Requirement: ABM de Materia con unicidad de código por tenant
El sistema SHALL permitir alta, edición, baja (soft delete), listado y cambio de estado (Activa/Inactiva) de materias del catálogo único del tenant. El par `(tenant_id, codigo)` MUST ser único entre las materias vivas. Una materia es sólo definición de catálogo; su puesta en cursado se modela como `Dictado`.

#### Scenario: Alta de materia
- **WHEN** un administrador crea una materia con código y nombre válidos
- **THEN** la materia se persiste con `tenant_id` de la sesión y estado Activa

#### Scenario: Código de materia duplicado
- **WHEN** se intenta crear una materia con un `codigo` ya existente (vivo) en el mismo tenant
- **THEN** el sistema rechaza la operación con error de validación (422)

### Requirement: ABM de Cohorte con unicidad por carrera y regla de carrera activa
El sistema SHALL permitir alta, edición, baja, listado y cambio de estado de cohortes asociadas a una carrera. El par `(tenant_id, carrera_id, nombre)` MUST ser único entre las cohortes vivas. Una carrera Inactiva MUST NOT admitir cohortes abiertas (`vig_hasta` nulo).

#### Scenario: Alta de cohorte en carrera activa
- **WHEN** un administrador crea una cohorte (con nombre, año, vigencia) sobre una carrera Activa
- **THEN** la cohorte se persiste asociada a esa carrera y al `tenant_id` de la sesión

#### Scenario: Nombre de cohorte duplicado dentro de la carrera
- **WHEN** se intenta crear una cohorte con un `nombre` que ya existe (vivo) para la misma `(tenant_id, carrera_id)`
- **THEN** el sistema rechaza la operación con error de validación (422)

#### Scenario: Cohorte abierta sobre carrera inactiva rechazada
- **WHEN** se intenta crear una cohorte abierta (`vig_hasta` nulo) sobre una carrera Inactiva
- **THEN** el sistema rechaza la operación con error de validación (422)

### Requirement: ABM de Dictado con unicidad y consistencia carrera-cohorte
El sistema SHALL permitir alta, edición, baja, listado y cambio de estado de dictados (instancia de una materia en una carrera × cohorte concreta, ADR-006). La terna `(tenant_id, materia_id, carrera_id, cohorte_id)` MUST ser única entre los dictados vivos. El `carrera_id` del dictado MUST coincidir con el `carrera_id` de la cohorte referida. NO se MUST crear un dictado sobre una materia, carrera o cohorte Inactiva.

#### Scenario: Alta de dictado consistente
- **WHEN** un administrador crea un dictado referenciando una materia Activa, una carrera Activa y una cohorte Activa de esa misma carrera
- **THEN** el dictado se persiste con estado Activo y `tenant_id` de la sesión

#### Scenario: Terna duplicada rechazada
- **WHEN** se intenta crear un dictado con la misma terna `(materia_id, carrera_id, cohorte_id)` que un dictado vivo del tenant
- **THEN** el sistema rechaza la operación con error de validación (422)

#### Scenario: Inconsistencia carrera-cohorte rechazada
- **WHEN** se intenta crear un dictado cuyo `carrera_id` no coincide con el `carrera_id` de la `cohorte_id` referida
- **THEN** el sistema rechaza la operación con error de validación (422)

#### Scenario: Dictado sobre entidad inactiva rechazado
- **WHEN** se intenta crear un dictado donde la materia, la carrera o la cohorte referida está Inactiva
- **THEN** el sistema rechaza la operación con error de validación (422)

### Requirement: Aislamiento multi-tenant de la estructura académica
Toda operación de lectura y escritura sobre carreras, cohortes, materias y dictados MUST estar acotada al `tenant_id` de la sesión. Un tenant MUST NOT poder leer, modificar ni eliminar entidades de otro tenant, ni referenciar entidades de otro tenant al crear dictados o cohortes.

#### Scenario: Listado acotado al tenant
- **WHEN** un administrador lista carreras (o cohortes/materias/dictados)
- **THEN** sólo se devuelven las entidades cuyo `tenant_id` coincide con el de su sesión

#### Scenario: Acceso a entidad de otro tenant rechazado
- **WHEN** un administrador intenta obtener, editar o eliminar una entidad por id que pertenece a otro tenant
- **THEN** el sistema responde 404 (no encontrada en su scope) y no realiza la operación

### Requirement: Auditoría de mutaciones de estructura académica
Las operaciones de mutación (alta, edición, baja y cambio de estado) sobre la estructura académica SHALL registrarse en el log de auditoría con atribución al actor real de la sesión.

#### Scenario: Alta genera registro de auditoría
- **WHEN** un administrador da de alta una carrera, cohorte, materia o dictado
- **THEN** se crea un registro en el audit log atribuido al actor de la sesión
