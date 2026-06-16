## ADDED Requirements

### Requirement: Acceso restringido por permiso encuentros:gestionar
Todos los endpoints de gestión de encuentros MUST exigir el permiso `encuentros:gestionar`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada, nunca desde la URL, body o headers. Fail-closed: sin el permiso, la respuesta MUST ser 403.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario cuyos roles no incluyen `encuentros:gestionar` invoca cualquier endpoint de encuentros
- **THEN** el sistema responde 403 y no realiza ninguna operación

#### Scenario: Docente con encuentros:gestionar accede
- **WHEN** un usuario con rol que incluye `encuentros:gestionar` (PROFESOR, COORDINADOR) invoca un endpoint de encuentros
- **THEN** la operación se ejecuta acotada al `tenant_id` de su sesión

### Requirement: ABM de SlotEncuentro con generación de instancias
El sistema SHALL permitir la creación, edición, listado y baja (soft delete) de slots de encuentro. Cada slot define una plantilla de recurrencia semanal con `dia_semana`, `hora`, `fecha_inicio`, `cant_semanas` (0 = encuentro único), `fecha_unica` (alternativa a recurrencia, nullable), `meet_url`, `titulo`, `vig_desde`, `vig_hasta` y `asignacion_id` (nullable, FK → Asignacion). Todos los slots SHALL referenciar un `dictado_id` (FK → Dictado) como contexto académico (ADR-006).  

Al crear un slot con `cant_semanas > 0`, el sistema MUST generar automáticamente N instancias de `InstanciaEncuentro` en el mismo momento, una por cada semana desde `fecha_inicio`, con estado `Programado`. Si `cant_semanas = 0`, `fecha_unica` MUST ser no nula y se genera una sola instancia.

#### Scenario: Crear slot recurrente
- **WHEN** un PROFESOR crea un slot con `cant_semanas = 14`, `dia_semana = "Lunes"`, `hora = "18:00"`, `fecha_inicio = "2026-03-15"`, `meet_url = "https://meet.example.com/aula"`, `dictado_id = <dictado_valido>`
- **THEN** se crea el slot y se generan 14 instancias de encuentro, una por cada lunes desde el 2026-03-15, todas con estado Programado

#### Scenario: Crear encuentro único (cant_semanas = 0)
- **WHEN** un PROFESOR crea un slot con `cant_semanas = 0`, `fecha_unica = "2026-05-20"`, `hora = "18:00"`, `titulo = "Clase de consulta"`
- **THEN** se crea el slot (sin recurrencia) y se genera una sola instancia con fecha 2026-05-20

#### Scenario: Slot con cant_semanas = 0 sin fecha_unica es rechazado
- **WHEN** se crea un slot con `cant_semanas = 0` y `fecha_unica = null`
- **THEN** el sistema rechaza la operación con error de validación (422)

#### Scenario: Slot con cant_semanas > 52 es rechazado
- **WHEN** se crea un slot con `cant_semanas > 52`
- **THEN** el sistema rechaza la operación con error de validación (422)

### Requirement: Edición de instancia de encuentro
El sistema SHALL permitir modificar individualmente cada `InstanciaEncuentro`. Campos editables: `estado` (Programado → Realizado | Cancelado), `meet_url`, `video_url` (nullable, disponible después de realizado), `comentario`. Una instancia Cancelada NO puede volver a Programado.

#### Scenario: Marcar encuentro como Realizado con video
- **WHEN** un PROFESOR edita una instancia en estado Programado, cambia estado a Realizado y agrega `video_url = "https://vimeo.com/123"` y `comentario = "Buena participación"`
- **THEN** la instancia queda con estado Realizado, video_url y comentario persistidos

#### Scenario: Cancelar instancia
- **WHEN** un PROFESOR cambia el estado de una instancia de Programado a Cancelado
- **THEN** la instancia queda Cancelada

#### Scenario: Reactivar instancia cancelada es rechazado
- **WHEN** un PROFESOR intenta cambiar una instancia en estado Cancelado a Realizado o Programado
- **THEN** el sistema rechaza la operación con error de validación (422)

### Requirement: Generación de bloque HTML para el LMS
El sistema SHALL generar un fragmento HTML con los encuentros programados de un dictado, ordenados por fecha. El bloque SHALL incluir: fecha, hora, título, enlace de videoconferencia, y enlace a grabación (si existe). La salida es texto plano HTML listo para copiar y pegar en el aula virtual.

#### Scenario: Generar bloque HTML de un dictado
- **WHEN** un PROFESOR solicita el bloque HTML para su dictado
- **THEN** el sistema devuelve un string con una tabla HTML que lista las instancias activas ordenadas por fecha, incluyendo solo aquellas con estado Programado o Realizado

### Requirement: Vista admin transversal de encuentros
El sistema SHALL exponer un endpoint que liste todos los encuentros del tenant, sin filtrar por dictado, accesible solo para COORDINADOR/ADMIN. SHALL soportar filtros opcionales: `dictado_id`, `estado`, `fecha_desde`, `fecha_hasta`.

#### Scenario: Admin lista todos los encuentros del tenant
- **WHEN** un ADMIN invoca GET /api/v1/encuentros sin filtros
- **THEN** el sistema devuelve todas las instancias de encuentro del tenant paginadas

#### Scenario: Coordinador filtra encuentros por estado
- **WHEN** un COORDINADOR invoca GET /api/v1/encuentros con `?estado=Realizado`
- **THEN** el sistema devuelve solo las instancias con estado Realizado del tenant

### Requirement: Consulta de encuentros por dictado
El sistema SHALL listar los encuentros filtrados por `dictado_id`, accesible para PROFESOR (solo su dictado) y COORDINADOR (cualquier dictado del tenant).

#### Scenario: Profesor lista encuentros de su dictado
- **WHEN** un PROFESOR invoca GET /api/v1/encuentros?dictado_id=<su_dictado>
- **THEN** el sistema devuelve las instancias de ese dictado que pertenecen al tenant del usuario

### Requirement: Aislamiento multi-tenant
Toda operación sobre slots e instancias MUST estar acotada al `tenant_id` de la sesión. Un tenant MUST NOT poder leer, modificar ni eliminar encuentros de otro tenant.

#### Scenario: Acceso a encuentro de otro tenant es 404
- **WHEN** un usuario intenta acceder a un encuentro por ID que pertenece a otro tenant
- **THEN** el sistema responde 404 (no encontrado en su scope)

### Requirement: Auditoría de mutaciones de encuentros
Las operaciones de mutación sobre slots e instancias SHALL registrarse en el log de auditoría. Códigos: `ENCUENTRO_CREAR` (alta de slot), `ENCUENTRO_EDITAR` (edición de instancia), `ENCUENTRO_CANCELAR` (cancelación de instancia).

#### Scenario: Alta de slot genera audit
- **WHEN** un PROFESOR crea un slot recurrente
- **THEN** se registra una entrada en audit log con acción `ENCUENTRO_CREAR`, atribuida al actor de la sesión, con detalle del dictado y cantidad de instancias generadas

#### Scenario: Edición de instancia genera audit
- **WHEN** un PROFESOR edita una instancia (estado, video_url, comentario)
- **THEN** se registra una entrada en audit log con acción `ENCUENTRO_EDITAR` y detalle del cambio
