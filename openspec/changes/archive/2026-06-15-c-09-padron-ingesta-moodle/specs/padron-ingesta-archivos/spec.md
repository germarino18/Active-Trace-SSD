## ADDED Requirements

### Requirement: Import de padrón desde archivo .xlsx/.csv con preview

El sistema SHALL permitir importar un padrón de alumnos desde archivos `.xlsx` o `.csv` en un flujo de dos pasos: (1) preview que parsea y valida el archivo sin persistir, (2) confirm que persiste los datos creando una nueva `VersionPadron` activa y desactivando la anterior. Los datos esperados por fila son: nombre, apellidos, email (cifrado al persistir), comisión, regional. El endpoint SHALL estar gated por `padron:importar`. Para PROFESOR, el `dictado_id` debe corresponder a sus asignaciones; para COORDINADOR, cualquier dictado del tenant.

#### Scenario: Preview de archivo válido
- **WHEN** un usuario con `padron:importar` sube un archivo `.xlsx` o `.csv` con columnas válidas (nombre, apellidos, email, comision, regional) para un dictado al que está autorizado
- **THEN** el sistema devuelve un resumen con cantidad de filas, columnas detectadas, las primeras N filas como muestra, y un token de preview. NO persiste ningún registro.

#### Scenario: Preview de archivo con errores de parseo
- **WHEN** el archivo subido tiene filas con datos inválidos (email mal formado, columnas faltantes)
- **THEN** el sistema devuelve errores de validación por fila indicando la naturaleza del error y NO genera token de preview

#### Scenario: Preview rechazado sin permiso
- **WHEN** un usuario sin `padron:importar` intenta previsualizar un archivo
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Preview rechazado por dictado no autorizado (PROFESOR)
- **WHEN** un PROFESOR intenta previsualizar un archivo para un dictado al que no está asignado
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Confirm de importación exitoso
- **WHEN** un usuario envía un token de preview válido para confirmar la importación
- **THEN** el sistema crea una nueva `VersionPadron` con `activa=true`, persiste todas las `EntradaPadron`, desactiva la versión anterior del mismo dictado, registra `PADRON_CARGAR` en audit log, y devuelve la versión creada con conteo de filas

#### Scenario: Confirm con token expirado o inválido
- **WHEN** un usuario envía un token de preview que no existe o expiró
- **THEN** el sistema responde 422 con error de validación y no persiste nada

#### Scenario: Confirm detecta versión más nueva
- **WHEN** entre el preview y el confirm otro usuario activó una versión más nueva para el mismo dictado
- **THEN** el sistema responde 409 Conflict indicando que el padrón fue modificado y solicitando re-preview

### Requirement: Aislamiento multi-tenant en importación

Toda importación de padrón SHALL estar acotada al `tenant_id` de la sesión. Un tenant NO MUST poder importar datos para dictados de otro tenant.

#### Scenario: Importación a dictado de otro tenant rechazada
- **WHEN** un usuario intenta importar un padrón para un `dictado_id` que pertenece a otro tenant
- **THEN** el sistema responde 404 (dictado no encontrado) y no realiza la operación
