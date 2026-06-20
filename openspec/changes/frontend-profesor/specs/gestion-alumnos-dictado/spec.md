## ADDED Requirements

### Requirement: Alta y baja individual de alumno en un dictado
El sistema SHALL permitir al PROFESOR agregar un alumno individual al padrón de un dictado y quitar un alumno individual del padrón. Ambas operaciones MUST exigir el permiso `padron:gestionar-alumno` (fail-closed: sin permiso, 403) y MUST estar acotadas al `tenant_id` de la sesión. La baja MUST ser soft delete, nunca hard delete. Cada operación MUST registrarse en auditoría derivada de la sesión.

#### Scenario: Agregar alumno al dictado
- **WHEN** un PROFESOR con `padron:gestionar-alumno` agrega un alumno a un dictado de su tenant
- **THEN** el alumno queda incorporado al padrón del dictado y se registra el evento en auditoría

#### Scenario: Quitar alumno del dictado
- **WHEN** el PROFESOR quita un alumno del dictado
- **THEN** el sistema marca la entrada del padrón como eliminada por soft delete, sin borrarla físicamente

#### Scenario: Sin permiso es rechazado
- **WHEN** un usuario sin `padron:gestionar-alumno` intenta agregar o quitar un alumno
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: Dictado de otro tenant
- **WHEN** se intenta gestionar un alumno en un dictado de otro tenant
- **THEN** el sistema responde 404 y no realiza ninguna operación

### Requirement: Export de plantilla CSV precargada con el padrón
El sistema SHALL permitir descargar un archivo CSV base de un dictado, precargado con una fila por alumno del padrón vigente (incluyendo `alumno_id`, `nombre` y `apellido`) y columnas vacías para que el profesor complete las calificaciones offline y las suba por el flujo de importación existente. El export MUST estar acotado al `tenant_id` de la sesión. Por ser sólo lectura, no genera auditoría.

#### Scenario: Descarga de plantilla con alumnos
- **WHEN** un PROFESOR solicita la plantilla CSV de un dictado de su tenant
- **THEN** el sistema responde un CSV descargable con una fila por alumno del padrón vigente y columnas para completar calificaciones

#### Scenario: Plantilla acotada al tenant
- **WHEN** se solicita la plantilla de un dictado de otro tenant
- **THEN** el sistema responde 404 y no entrega datos

### Requirement: Frontend de gestión de alumnos del dictado
El frontend SHALL ofrecer un tab de alumnos en el panel del dictado que permita agregar un alumno, quitar un alumno y ver su información, además de descargar la plantilla CSV. Las operaciones MUST realizarse vía hooks de servicio contra los endpoints correspondientes.

#### Scenario: Gestión de alumnos desde la UI
- **WHEN** el PROFESOR abre el tab de alumnos de un dictado
- **THEN** puede agregar un alumno, quitar un alumno, ver su información y descargar la plantilla CSV precargada
