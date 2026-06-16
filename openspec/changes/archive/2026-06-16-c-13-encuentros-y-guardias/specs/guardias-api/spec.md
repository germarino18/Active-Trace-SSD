## ADDED Requirements

### Requirement: Acceso restringido por permiso encuentros:gestionar
Todos los endpoints de guardias MUST exigir el permiso `encuentros:gestionar`. La identidad y el `tenant_id` MUST resolverse exclusivamente desde la sesión JWT verificada. Fail-closed: sin el permiso, respuesta 403.

#### Scenario: Usuario sin permiso es rechazado
- **WHEN** un usuario sin `encuentros:gestionar` invoca un endpoint de guardias
- **THEN** el sistema responde 403

#### Scenario: Tutor registra guardia
- **WHEN** un TUTOR (con `encuentros:gestionar`) invoca POST /api/v1/guardias
- **THEN** la operación se ejecuta acotada a su tenant

### Requirement: Registro de guardia
El sistema SHALL permitir registrar una guardia. Campos: `asignacion_id` (FK → Asignacion, no nullable — quién cubre), `dictado_id` (FK → Dictado), `dia` (enum día de semana), `horario` (texto, ej: "14:00–14:45"), `estado` (Pendiente | Realizada | Cancelada), `comentarios` (texto nullable). `creada_at` se asigna automáticamente.

#### Scenario: Tutor registra guardia
- **WHEN** un TUTOR registra una guardia con `asignacion_id`, `dictado_id`, `dia = "Martes"`, `horario = "14:00–14:45"`
- **THEN** la guardia se persiste con estado Pendiente y `creada_at` con la fecha/hora actual

### Requirement: Consulta y filtro de guardias
El sistema SHALL listar guardias con filtros opcionales: `dictado_id`, `asignacion_id`, `estado`, `dia`, `fecha_desde`, `fecha_hasta`. TUTOR solo ve sus propias guardias (filtro por su `asignacion_id`). COORDINADOR/ADMIN ve todas las del tenant.

#### Scenario: Coordinador lista todas las guardias del tenant
- **WHEN** un COORDINADOR invoca GET /api/v1/guardias sin filtros
- **THEN** el sistema devuelve todas las guardias del tenant

#### Scenario: Tutor lista solo sus guardias
- **WHEN** un TUTOR invoca GET /api/v1/guardias
- **THEN** el sistema devuelve solo las guardias donde `asignacion_id` pertenece al usuario (filtro implícito)

### Requirement: Edición de guardia
El sistema SHALL permitir modificar `estado`, `comentarios` de una guardia existente. COORDINADOR/ADMIN puede editar cualquier guardia del tenant. TUTOR solo sus propias guardias.

#### Scenario: Coordinador cancela guardia
- **WHEN** un COORDINADOR cambia el estado de una guardia de Pendiente a Cancelada
- **THEN** la guardia queda Cancelada

#### Scenario: Tutor no puede editar guardia de otro tutor
- **WHEN** un TUTOR intenta editar una guardia cuyo `asignacion_id` pertenece a otro usuario
- **THEN** el sistema responde 404 (no encontrada en su scope)

### Requirement: Exportación de guardias
El sistema SHALL exportar el registro de guardias a formato CSV descargable, con los mismos filtros que la consulta. COORDINADOR/ADMIN puede exportar todo el tenant. TUTOR exporta solo sus guardias.

#### Scenario: Coordinador exporta guardias
- **WHEN** un COORDINADOR invoca GET /api/v1/guardias/export con filtros opcionales
- **THEN** el sistema devuelve un archivo CSV con las guardias filtradas

### Requirement: Aislamiento multi-tenant
Toda operación sobre guardias MUST estar acotada al `tenant_id` de la sesión.

#### Scenario: Acceso a guardia de otro tenant es 404
- **WHEN** un usuario intenta acceder a una guardia por ID que pertenece a otro tenant
- **THEN** el sistema responde 404

### Requirement: Auditoría de guardias
Las operaciones de mutación sobre guardias SHALL registrarse en el log de auditoría. Código: `GUARDIA_REGISTRAR`.

#### Scenario: Registro de guardia genera audit
- **WHEN** un TUTOR registra una guardia
- **THEN** se registra una entrada en audit log con acción `GUARDIA_REGISTRAR`, atribuida al actor de la sesión
