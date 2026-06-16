## ADDED Requirements

### Requirement: Acceso restringido por permiso estructura:gestionar

Todos los endpoints de ABM de fechas académicas (`/api/v1/fechas-academicas`) MUST exigir el permiso `estructura:gestionar`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada, nunca desde la URL, body o headers. Fail-closed: sin el permiso, la respuesta MUST ser 403.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario cuyos roles no incluyen `estructura:gestionar` invoca cualquier endpoint de fechas académicas
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: Usuario autorizado accede
- **WHEN** un usuario con rol COORDINADOR o ADMIN (que tienen `estructura:gestionar`) invoca un endpoint de fechas académicas
- **THEN** la operación se ejecuta acotada al `tenant_id` de su sesión

### Requirement: CRUD de FechaAcademica por dictado × periodo

El sistema SHALL permitir alta, edición, listado tabular, vista calendario y baja (soft delete) de fechas académicas. Cada fecha está asociada a un `dictado_id` (FK → Dictado). La combinación `(tenant_id, dictado_id, tipo, numero)` MUST ser única entre las fechas vivas. El campo `periodo` (texto, ej: "2026-1") SHALL agrupar las fechas de un período académico para consultas.

#### Scenario: Alta de fecha académica
- **WHEN** un administrador crea una fecha académica con dictado, tipo (Parcial/TP/Coloquio/Recuperatorio), número, periodo, fecha y título válidos
- **THEN** el sistema persiste la fecha con `tenant_id` de la sesión

#### Scenario: Combinación tipo+numero duplicada en mismo dictado
- **WHEN** se intenta crear una fecha con el mismo `(dictado_id, tipo, numero)` que una fecha viva del mismo dictado y tenant
- **THEN** el sistema rechaza la operación con error de validación (422)

#### Scenario: Listado tabular por dictado × periodo
- **WHEN** un administrador lista fechas académicas filtrando por dictado y periodo
- **THEN** el sistema retorna las fechas vivas del dictado y periodo especificados, ordenadas por fecha ascendente

#### Scenario: Vista calendario por dictado × periodo
- **WHEN** un administrador solicita la vista calendario para un dictado y periodo
- **THEN** el sistema retorna las fechas vivas agrupadas por mes, con fecha, tipo y título

#### Scenario: Actualización de fecha académica
- **WHEN** un administrador actualiza la fecha, título o tipo de una fecha académica existente
- **THEN** los cambios se persisten y se registran en el audit log

#### Scenario: Soft delete de fecha académica
- **WHEN** un administrador elimina una fecha académica
- **THEN** el registro se marca como eliminado (no se borra físicamente)

### Requirement: Generación de fragmento de contenido para LMS

El sistema SHALL generar un fragmento de contenido formateado (markdown) con las fechas académicas de un dictado × periodo, listo para copiar y publicar en el aula virtual del LMS (F5.4). El fragmento SHALL incluir tipo, número, fecha y título de cada evaluación, agrupadas por tipo de evaluación.

#### Scenario: Fragmento generado exitosamente
- **WHEN** un administrador solicita el fragmento LMS para un dictado y periodo con fechas registradas
- **THEN** el sistema retorna un bloque de texto markdown con las fechas agrupadas por tipo (Parciales, TPs, Coloquios) ordenadas por fecha

#### Scenario: Fragmento sin fechas registradas
- **WHEN** un administrador solicita el fragmento LMS para un dictado y periodo sin fechas registradas
- **THEN** el sistema retorna un mensaje indicando que no hay fechas cargadas para ese período

### Requirement: Aislamiento multi-tenant de fechas académicas

Toda operación sobre fechas académicas MUST estar acotada al `tenant_id` de la sesión. Un tenant MUST NOT poder leer, modificar ni eliminar fechas de otro tenant.

#### Scenario: Listado acotado al tenant
- **WHEN** un administrador lista fechas académicas
- **THEN** solo se devuelven las fechas cuyo `tenant_id` coincide con el de su sesión

#### Scenario: Acceso a fecha de otro tenant rechazado
- **WHEN** un administrador intenta obtener, editar o eliminar una fecha por ID que pertenece a otro tenant
- **THEN** el sistema responde 404 (no encontrada en su scope) y no realiza la operación

### Requirement: Auditoría de mutaciones de fechas académicas

Las operaciones de mutación (alta, edición y baja) sobre fechas académicas SHALL registrarse en el log de auditoría con atribución al actor real de la sesión.

#### Scenario: Alta genera registro de auditoría
- **WHEN** un administrador da de alta una fecha académica
- **THEN** se crea un registro en el audit log atribuido al actor de la sesión con código `FECHA_ACADEMICA_CARGAR`
