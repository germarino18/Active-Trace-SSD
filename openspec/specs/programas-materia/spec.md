## ADDED Requirements

### Requirement: Acceso restringido por permiso estructura:gestionar

Todos los endpoints de ABM de programas de materia (`/api/v1/programas`) MUST exigir el permiso `estructura:gestionar`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada, nunca desde la URL, body o headers. Fail-closed: sin el permiso, la respuesta MUST ser 403.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario cuyos roles no incluyen `estructura:gestionar` invoca cualquier endpoint de programas
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: Usuario autorizado accede
- **WHEN** un usuario con rol COORDINADOR o ADMIN (que tienen `estructura:gestionar`) invoca un endpoint de programas
- **THEN** la operación se ejecuta acotada al `tenant_id` de su sesión

### Requirement: ABM de ProgramaMateria por dictado

El sistema SHALL permitir alta, edición, listado, obtención por ID, y baja (soft delete) de programas de materia. Cada programa está asociado a un `dictado_id` único (FK → Dictado). El par `(tenant_id, dictado_id)` MUST ser único entre los programas vivos (no eliminados). El campo `referencia_archivo` SHALL ser un puntero opaco al archivo almacenado.

#### Scenario: Alta de programa con archivo
- **WHEN** un administrador sube un archivo de programa con título y asociado a un dictado existente
- **THEN** el sistema guarda el archivo, persiste el registro con `referencia_archivo`, `titulo`, `dictado_id`, `tenant_id` y `cargado_at`, y retorna el programa creado

#### Scenario: Dictado duplicado rechazado
- **WHEN** se intenta crear un programa para un `dictado_id` que ya tiene un programa vivo en el mismo tenant
- **THEN** el sistema rechaza la operación con error de validación (422) y no crea el registro

#### Scenario: Listado de programas por dictado
- **WHEN** un administrador lista programas filtrando por dictado
- **THEN** el sistema retorna solo los programas vivos cuyo `dictado_id` coincide con el filtro y `tenant_id` con la sesión

#### Scenario: Obtención de programa por ID
- **WHEN** un administrador solicita un programa por su ID
- **THEN** el sistema retorna el programa si existe y pertenece al tenant de la sesión

#### Scenario: Actualización de título y archivo
- **WHEN** un administrador actualiza el título y/o archivo de un programa existente
- **THEN** el nuevo archivo reemplaza al anterior y `cargado_at` se actualiza

#### Scenario: Soft delete de programa
- **WHEN** un administrador elimina un programa
- **THEN** el registro se marca como eliminado (no se borra físicamente) y el archivo referenciado se conserva

### Requirement: Aislamiento multi-tenant de programas

Toda operación sobre programas MUST estar acotada al `tenant_id` de la sesión. Un tenant MUST NOT poder leer, modificar ni eliminar programas de otro tenant.

#### Scenario: Listado acotado al tenant
- **WHEN** un administrador lista programas
- **THEN** solo se devuelven los programas cuyo `tenant_id` coincide con el de su sesión

#### Scenario: Acceso a programa de otro tenant rechazado
- **WHEN** un administrador intenta obtener, editar o eliminar un programa por ID que pertenece a otro tenant
- **THEN** el sistema responde 404 (no encontrado en su scope) y no realiza la operación

### Requirement: Auditoría de mutaciones de programas

Las operaciones de mutación (alta, edición y baja) sobre programas SHALL registrarse en el log de auditoría con atribución al actor real de la sesión.

#### Scenario: Alta genera registro de auditoría
- **WHEN** un administrador da de alta un programa
- **THEN** se crea un registro en el audit log atribuido al actor de la sesión con código `PROGRAMA_CARGAR`
