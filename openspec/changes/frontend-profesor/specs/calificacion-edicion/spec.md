## ADDED Requirements

### Requirement: Edición individual de calificación por el profesor
El sistema SHALL permitir al PROFESOR editar una calificación individual modificando su `nota` (numérica o textual) y su estado `aprobado`. La operación MUST exigir el permiso `calificaciones:editar` (fail-closed: sin permiso, 403) y MUST estar acotada al `tenant_id` de la sesión. La identidad del autor MUST derivarse de la sesión JWT. El cambio MUST registrarse en auditoría. El cuerpo de la petición MUST rechazar campos no declarados (`extra='forbid'`).

#### Scenario: Editar nota y aprobado
- **WHEN** un PROFESOR con `calificaciones:editar` modifica la nota y el estado aprobado de una calificación de un dictado de su tenant
- **THEN** el sistema persiste los nuevos valores y registra el cambio en auditoría derivado de su sesión

#### Scenario: Sin permiso es rechazado
- **WHEN** un usuario sin `calificaciones:editar` intenta editar una calificación
- **THEN** el sistema responde 403 y no modifica nada

#### Scenario: Calificación de otro tenant
- **WHEN** se intenta editar una calificación que no pertenece al tenant de la sesión
- **THEN** el sistema responde 404 y no modifica nada

#### Scenario: Cuerpo con campos no declarados
- **WHEN** la petición de edición incluye un campo no declarado en el schema
- **THEN** el sistema rechaza la petición por validación

### Requirement: Frontend de edición de calificación
El frontend SHALL permitir al PROFESOR ver el listado de actividades con las notas por alumno y su estado aprobado, y editar la nota y el aprobado de un alumno. La edición MUST hacerse vía formulario validado y persistir mediante el endpoint de edición.

#### Scenario: Listado de actividades con notas
- **WHEN** el PROFESOR abre el tab de calificaciones de un dictado
- **THEN** se muestra el listado de actividades con las notas por alumno y el estado aprobado

#### Scenario: Edición desde la UI
- **WHEN** el PROFESOR edita la nota y el aprobado de un alumno y confirma
- **THEN** el frontend persiste el cambio y refleja el nuevo valor
