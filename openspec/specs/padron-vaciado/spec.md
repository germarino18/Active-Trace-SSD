## ADDED Requirements

### Requirement: Vaciado scope-isolated de datos de dictado (RN-04)

El sistema SHALL permitir vaciar los datos de padrón de un dictado, con alcance restringido: para PROFESOR, solo los datos que ese profesor cargó en ese dictado; para COORDINADOR, todos los datos del dictado. La operación SHALL eliminar todas las `EntradaPadron` de todas las versiones del dictado (no solo la activa), y todas las `VersionPadron` del dictado. SHALL registrar `PADRON_VACIAR` en audit log con `filas_afectadas`. Gated por `padron:vaciar`.

#### Scenario: Profesor vacía sus propios datos
- **WHEN** un PROFESOR invoca vaciar para un dictado donde está asignado como docente
- **THEN** se eliminan ÚNICAMENTE las versiones de padrón que ese profesor cargó (`cargado_por = usuario_id`), y el audit log registra la acción con las filas afectadas
- **THEN** si la versión activa era del profesor y se eliminó, el dictado queda sin padrón activo

#### Scenario: Coordinador vacía cualquier dictado
- **WHEN** un COORDINADOR invoca vaciar para un dictado de su tenant
- **THEN** se eliminan TODAS las versiones de padrón del dictado (todas las versiones de todos los cargadores)
- **THEN** el audit log registra la acción con las filas afectadas totales

#### Scenario: Vaciado rechazado sin permiso
- **WHEN** un usuario sin `padron:vaciar` intenta vaciar un dictado
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Profesor intenta vaciar dictado no asignado
- **WHEN** un PROFESOR invoca vaciar para un dictado donde NO está asignado
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Vaciado no afecta otros dictados
- **WHEN** se vacía un dictado
- **THEN** los datos de padrón de otros dictados del mismo tenant NO se modifican
