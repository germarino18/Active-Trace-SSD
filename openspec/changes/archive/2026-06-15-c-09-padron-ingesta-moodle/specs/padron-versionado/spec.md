## ADDED Requirements

### Requirement: VersionPadron model with activa flag per dictado

El sistema SHALL proveer una tabla `version_padron` que represente una versión del padrón de alumnos para un dictado. Solo una versión por `dictado_id` puede tener `activa=true` en simultáneo. La tabla SHALL usar `BaseMixin`, `TenantMixin`, y `soft_delete` no aplica (se conserva histórico). `activa` SHALL ser booleano con default `true`. `cargado_por` SHALL ser UUID FK → `users.id`.

#### Scenario: Crear primera versión de un dictado
- **WHEN** se crea un `VersionPadron` para un `dictado_id` que no tiene ninguna versión previa
- **THEN** la versión se persiste con `activa=true`

#### Scenario: Activar nueva versión desactiva la anterior
- **WHEN** se crea una nueva `VersionPadron` con `activa=true` para un `dictado_id` que ya tiene una versión activa
- **THEN** la versión anterior pasa a `activa=false` y la nueva queda como única activa

#### Scenario: Versiones históricas son accesibles
- **WHEN** se consultan versiones de un dictado
- **THEN** tanto la versión activa como las inactivas se devuelven (con indicador de activa)

#### Scenario: Aislamiento multi-tenant de versiones
- **WHEN** se listan versiones de padrón
- **THEN** solo se devuelven versiones cuyo `tenant_id` coincide con el de la sesión

### Requirement: EntradaPadron model con email cifrado

El sistema SHALL proveer una tabla `entrada_padron` que almacene cada fila del padrón (un alumno por fila), vinculada a `version_id`. La tabla SHALL usar `BaseMixin`, `TenantMixin`. `usuario_id` SHALL ser FK → `users.id` nullable (el alumno puede no tener cuenta aún). `email` SHALL almacenarse cifrado AES-256. Sin soft delete: las entradas se crean en masa al importar y se conservan históricamente con su versión.

#### Scenario: Entrada sin usuario_id (alumno sin cuenta)
- **WHEN** se importa un padrón con un alumno que no tiene `usuario_id` en el sistema
- **THEN** la `EntradaPadron` se persiste con `usuario_id=null` y el resto de datos del alumno

#### Scenario: Email cifrado en reposo
- **WHEN** una `EntradaPadron` se persiste con un email
- **THEN** el valor en la columna `email` de la BD NO es el texto plano del email

#### Scenario: Entradas accesibles por versión
- **WHEN** se consultan entradas por `version_id`
- **THEN** solo se devuelven las entradas de esa versión, acotadas al `tenant_id` de la sesión
