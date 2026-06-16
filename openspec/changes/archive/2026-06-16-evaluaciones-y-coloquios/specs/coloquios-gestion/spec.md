## ADDED Requirements

### Requirement: Acceso restringido por permiso coloquios:gestionar
Todos los endpoints de gestión de convocatorias de coloquio MUST exigir el permiso `coloquios:gestionar`. Los de consulta y métricas MUST exigir `coloquios:ver`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada, nunca desde la URL, body o headers. Fail-closed: sin el permiso, la respuesta MUST ser 403.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario cuyos roles no incluyen `coloquios:gestionar` invoca un endpoint de gestión de convocatorias
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: COORDINADOR con coloquios:gestionar crea convocatoria
- **WHEN** un COORDINADOR con permiso `coloquios:gestionar` invoca el endpoint de creación
- **THEN** la operación se ejecuta acotada al `tenant_id` de su sesión

### Requirement: ABM de convocatorias de coloquio (Evaluacion)
El sistema SHALL permitir la creación, edición, listado y cierre de convocatorias de coloquio. Cada `Evaluacion` SHALL contener: `dictado_id` (FK → Dictado), `tipo` (Parcial | TP | Coloquio | Recuperatorio), `instancia` (denominación libre, ej. "Coloquio Final"), `dias_disponibles` (entero, ventana de inscripción en días), `cupo_maximo` (entero, cupo global), y `estado` (Activa | Cerrada). Al crearse, SHALL tener estado Activa.

#### Scenario: Crear convocatoria de coloquio
- **WHEN** un COORDINADOR crea una convocatoria con `dictado_id` válido, `tipo = "Coloquio"`, `instancia = "Coloquio Final"`, `dias_disponibles = 10`, `cupo_maximo = 30`
- **THEN** se crea la Evaluacion con estado Activa, y se registra auditoría con código `COLOQUIO_CREAR`

#### Scenario: Crear convocatoria con datos inválidos es rechazado
- **WHEN** un COORDINADOR crea una convocatoria sin `dictado_id` o con `cupo_maximo = 0`
- **THEN** el sistema rechaza la operación con error de validación (422)

#### Scenario: Editar convocatoria activa
- **WHEN** un COORDINADOR edita `dias_disponibles` o `cupo_maximo` de una convocatoria en estado Activa
- **THEN** los campos se actualizan; si ya hay reservas, el nuevo cupo debe ser >= cantidad de reservas activas, de lo contrario se rechaza (422)

#### Scenario: Cerrar convocatoria activa
- **WHEN** un COORDINADOR cambia el estado de una convocatoria de Activa a Cerrada
- **THEN** la convocatoria queda Cerrada; no se admiten nuevas reservas ni cancelaciones; se registra auditoría

#### Scenario: Cerrar convocatoria ya cerrada es idempotente
- **WHEN** un COORDINADOR intenta cerrar una convocatoria ya en estado Cerrada
- **THEN** el sistema responde exitosamente sin cambios (200, sin error)

#### Scenario: Listar convocatorias activas con métricas
- **WHEN** un COORDINADOR lista las convocatorias del tenant
- **THEN** el sistema devuelve una lista con: materia (desde dictado), instancia, estado, cupo_maximo, cantidad de reservas activas, cupos libres (cupo_maximo - reservas activas), y cantidad de resultados registrados

#### Scenario: Aislamiento multi-tenant en listado
- **WHEN** se listan convocatorias de dos tenants distintos
- **THEN** cada tenant ve solo sus propias convocatorias, sin solapamiento

### Requirement: Importar padrón de alumnos a una convocatoria
El sistema SHALL permitir importar alumnos habilitados para una convocatoria específica de coloquio. La importación SHALL ser un flujo separado del padrón general (C-09). Se SHALL poder importar desde una lista de `user_id` (alumnos). Si un alumno ya está importado, la operación SHALL ser idempotente (no duplicar).

#### Scenario: Importar alumnos a convocatoria activa
- **WHEN** un COORDINADOR importa una lista de 20 `user_id` (todos ALUMNOS válidos) a una convocatoria Activa
- **THEN** los 20 alumnos quedan asociados a la convocatoria y se registra auditoría con código `COLOQUIO_IMPORTAR_ALUMNOS`

#### Scenario: Importar alumno ya existente es idempotente
- **WHEN** un COORDINADOR importa una lista donde algunos `user_id` ya están importados
- **THEN** no se duplican; la operación completa exitosamente

#### Scenario: Importar a convocatoria Cerrada es rechazado
- **WHEN** un COORDINADOR intenta importar alumnos a una convocatoria en estado Cerrada
- **THEN** el sistema rechaza la operación con error 422

### Requirement: Panel de métricas de coloquios
El sistema SHALL exponer un endpoint de métricas globales de coloquios del tenant, accesible con permiso `coloquios:ver`. SHALL devolver: total de alumnos cargados (importados al menos una vez), cantidad de instancias activas, reservas activas totales, notas registradas totales.

#### Scenario: Consultar métricas
- **WHEN** un COORDINADOR consulta el panel de métricas
- **THEN** el sistema devuelve los 4 contadores (convocados, instancias activas, reservas activas, notas registradas) acotados al tenant

#### Scenario: Aislamiento multi-tenant en métricas
- **WHEN** dos tenants consultan las métricas simultáneamente
- **THEN** cada tenant ve solo sus propios contadores

### Requirement: Auditoría de acciones de coloquios
El sistema SHALL registrar en el AuditLog cada acción significativa sobre coloquios con su código estandarizado:
- `COLOQUIO_CREAR` — creación de convocatoria
- `COLOQUIO_IMPORTAR_ALUMNOS` — importación de padrón de alumnos
- `COLOQUIO_CERRAR` — cierre de convocatoria

#### Scenario: Creación auditable
- **WHEN** un COORDINADOR crea una nueva convocatoria
- **THEN** el audit log contiene una entrada con `codigo = "COLOQUIO_CREAR"`, el `actor_id` del COORDINADOR y el `detalle` con el id de la evaluación creada

#### Scenario: Consultas no auditan
- **WHEN** un COORDINADOR consulta el listado de convocatorias o el panel de métricas
- **THEN** NO se registra ninguna entrada en el audit log
