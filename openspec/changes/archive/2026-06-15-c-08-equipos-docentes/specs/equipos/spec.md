## ADDED Requirements

### Requirement: Acceso a operaciones de equipo restringido por equipos:asignar
Todos los endpoints de coordinación de equipos (consulta del tenant, asignación masiva, clonado, vigencia en bloque y export) bajo `/api/equipos/*` MUST exigir el permiso `equipos:asignar`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada, nunca desde la URL, body o headers. Fail-closed: sin el permiso, la respuesta MUST ser 403 y no se realiza ninguna operación.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario cuyos roles no incluyen `equipos:asignar` invoca un endpoint de coordinación de equipos
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: COORDINADOR accede acotado a su tenant
- **WHEN** un usuario con `equipos:asignar` (COORDINADOR o ADMIN) invoca un endpoint de coordinación de equipos
- **THEN** la operación se ejecuta acotada al `tenant_id` de su sesión

### Requirement: Vista mis-equipos del docente acotada a su sesión
El sistema SHALL exponer un endpoint que devuelve las asignaciones del usuario autenticado, derivado EXCLUSIVAMENTE de su sesión JWT. El `usuario_id` MUST tomarse de `current_user`, nunca de un parámetro de la petición. Por defecto devuelve sólo las asignaciones VIGENTES (estado derivado por fechas), incluyendo rol, materia, carrera, cohorte, comisiones, vigencia y estado. El endpoint SHALL admitir filtros por estado, materia, rol, carrera y cohorte. No requiere `equipos:asignar`: basta una sesión válida.

#### Scenario: Docente ve sólo lo propio
- **WHEN** un docente autenticado consulta mis-equipos
- **THEN** el sistema devuelve únicamente asignaciones cuyo `usuario_id` coincide con el de su sesión y cuyo `tenant_id` es el de su sesión

#### Scenario: No expone asignaciones de otros docentes
- **WHEN** el docente A consulta mis-equipos y existen asignaciones del docente B en el mismo tenant
- **THEN** la respuesta no incluye ninguna asignación de B

#### Scenario: Por defecto sólo vigentes
- **WHEN** el docente tiene asignaciones vigentes y vencidas y consulta mis-equipos sin filtro de estado
- **THEN** el sistema devuelve sólo las vigentes (estado derivado por fechas)

### Requirement: Consulta filtrada de asignaciones del tenant
El sistema SHALL permitir a un usuario con `equipos:asignar` listar las asignaciones vivas del tenant con filtros por materia, carrera, cohorte, usuario, rol y responsable. El listado MUST estar acotado al `tenant_id` de la sesión y excluir asignaciones eliminadas (soft delete).

#### Scenario: Listado acotado al tenant
- **WHEN** un coordinador lista asignaciones aplicando filtros
- **THEN** el sistema devuelve sólo asignaciones vivas del `tenant_id` de su sesión que matchean los filtros

#### Scenario: Excluye eliminadas
- **WHEN** existen asignaciones soft-deleted que matchean los filtros
- **THEN** el sistema no las incluye en el resultado

### Requirement: Asignación masiva de docentes
El sistema SHALL permitir asignar un bloque de N docentes a una misma combinación materia × carrera × cohorte × rol con una vigencia (`desde`/`hasta`) común, en una única operación transaccional. Todos los `usuario_id` y el contexto académico MUST validarse contra el `tenant_id` de la sesión; una referencia ajena al tenant MUST tratarse como inexistente (404). Si la operación falla la validación de cualquier ítem, MUST abortarse por completo sin crear ninguna asignación. Un docente que ya tiene una asignación viva equivalente (mismo contexto + rol) MUST omitirse y reportarse como ya existente, sin duplicar. La operación SHALL generar un único evento de auditoría `ASIGNACION_MODIFICAR` con el número de filas afectadas.

#### Scenario: Alta en bloque exitosa
- **WHEN** un coordinador asigna varios docentes válidos a materia × carrera × cohorte × rol con vigencia
- **THEN** el sistema crea una asignación por docente con el `tenant_id` de la sesión y la vigencia indicada, en una sola transacción

#### Scenario: Docente ya asignado se omite sin duplicar
- **WHEN** uno de los docentes del bloque ya tiene una asignación viva con el mismo contexto y rol
- **THEN** el sistema no crea un duplicado para ese docente y lo reporta como ya existente

#### Scenario: Referencia a otro tenant
- **WHEN** el bloque incluye un `usuario_id` o un contexto que no pertenece al tenant de la sesión
- **THEN** el sistema responde 404 y no crea ninguna asignación

#### Scenario: Auditoría de la operación masiva
- **WHEN** una asignación masiva se aplica con éxito
- **THEN** el sistema registra un único evento `ASIGNACION_MODIFICAR` con las filas afectadas, derivado de la sesión del autor

### Requirement: Clonado de equipo entre períodos
El sistema SHALL permitir clonar un equipo docente de un contexto origen (materia × carrera × cohorte) hacia un destino (misma materia × carrera × nueva cohorte). El clonado MUST duplicar únicamente las asignaciones VIGENTES del origen, preservando `usuario_id`, `rol`, `responsable_id` y `comisiones`, cambiando el contexto al destino y aplicando las fechas de vigencia del nuevo período. Una asignación viva equivalente ya existente en el destino MUST omitirse (no duplicar). La operación MUST ser transaccional y acotada al `tenant_id` de la sesión, y SHALL generar un único evento de auditoría `ASIGNACION_MODIFICAR`.

#### Scenario: Clonado de equipo vigente
- **WHEN** un coordinador clona un equipo origen con asignaciones vigentes hacia una nueva cohorte con fechas nuevas
- **THEN** el sistema crea en el destino una asignación por cada asignación vigente del origen, con el nuevo contexto y las nuevas fechas

#### Scenario: No clona asignaciones vencidas
- **WHEN** el equipo origen tiene asignaciones vencidas además de vigentes
- **THEN** el sistema clona sólo las vigentes y deja afuera las vencidas

#### Scenario: No duplica lo ya presente en destino
- **WHEN** una asignación equivalente (mismo usuario + rol + contexto) ya existe viva en el destino
- **THEN** el sistema no la duplica

#### Scenario: Aislamiento de tenant en el clonado
- **WHEN** el origen o el destino no pertenecen al tenant de la sesión
- **THEN** el sistema responde 404 y no clona nada

### Requirement: Modificación de vigencia del equipo en bloque
El sistema SHALL permitir actualizar las fechas de vigencia (`desde` y/o `hasta`) de todas las asignaciones vivas de un equipo (materia × carrera × cohorte) en una sola operación, acotada al `tenant_id` de la sesión y transaccional. La operación SHALL generar un único evento de auditoría `ASIGNACION_MODIFICAR` con las filas afectadas.

#### Scenario: Actualización de vigencia en bloque
- **WHEN** un coordinador modifica la vigencia de un equipo con nuevas fechas
- **THEN** el sistema actualiza `desde`/`hasta` de todas las asignaciones vivas de ese equipo en su tenant, en una sola transacción

#### Scenario: Auditoría de la modificación de vigencia
- **WHEN** la modificación de vigencia en bloque se aplica con éxito
- **THEN** el sistema registra un único evento `ASIGNACION_MODIFICAR` con las filas afectadas

### Requirement: Exportación del equipo a archivo
El sistema SHALL permitir exportar el detalle de un equipo (materia × carrera × cohorte) a un archivo descargable CSV que incluya, por asignación: docente, rol, materia, carrera, cohorte, vigencia (`desde`/`hasta`) y estado de vigencia derivado. El export MUST estar acotado al `tenant_id` de la sesión. Por ser una operación de sólo lectura, no genera auditoría.

#### Scenario: Export descargable del equipo
- **WHEN** un coordinador exporta un equipo de su tenant
- **THEN** el sistema responde un archivo CSV descargable con una fila por asignación del equipo y las columnas de detalle

#### Scenario: Export acotado al tenant
- **WHEN** se solicita exportar un equipo de otro tenant
- **THEN** el sistema responde 404 y no entrega datos
