## ADDED Requirements

### Requirement: Filtro por estado activa/inactiva en listados de estructura académica
Los endpoints `GET /api/admin/carreras`, `GET /api/admin/cohortes`, `GET /api/admin/materias` y `GET /api/admin/dictados` SHALL aceptar un query param opcional `activa: Optional[bool]`. Cuando se proporciona, el listado SHALL filtrar solo entidades con ese estado. Cuando no se proporciona, SHALL devolver todas (comportamiento actual).

#### Scenario: Filtrar carreras activas
- **WHEN** un ADMIN invoca `GET /api/admin/carreras?activa=true`
- **THEN** solo se devuelven carreras con estado Activa

#### Scenario: Sin filtro devuelve todas
- **WHEN** un ADMIN invoca `GET /api/admin/carreras` sin `activa`
- **THEN** se devuelven todas las carreras del tenant (comportamiento existente)

### Requirement: Filtro por búsqueda textual en listados de estructura académica
Los endpoints `GET /api/admin/carreras`, `GET /api/admin/cohortes`, `GET /api/admin/materias` y `GET /api/admin/dictados` SHALL aceptar un query param opcional `q: Optional[str]`. Cuando se proporciona, el listado SHALL filtrar entidades cuyo `nombre` (o `codigo`) contenga el término (ILIKE / case-insensitive).

#### Scenario: Buscar carrera por nombre
- **WHEN** un ADMIN invoca `GET /api/admin/carreras?q=ingenieria`
- **THEN** se devuelven solo carreras cuyo nombre contiene "ingenieria" (case-insensitive)

### Requirement: Vigencia temporal en Dictado
El modelo `Dictado` SHALL exponer los campos opcionales `vig_desde: Optional[date]` y `vig_hasta: Optional[date]` que definen el período de validez del dictado. Estos campos SHALL ser editables vía `PUT /api/admin/dictados/{id}` y visibles en `GET /api/admin/dictados/{id}`. Un dictado sin fechas de vigencia se considera siempre vigente.

#### Scenario: Crear dictado con vigencia
- **WHEN** un ADMIN crea un dictado con `vig_desde = "2026-03-01"` y `vig_hasta = "2026-12-31"`
- **THEN** el dictado se persiste con esas fechas de vigencia

#### Scenario: Actualizar vigencia de dictado
- **WHEN** un ADMIN actualiza `vig_hasta` de un dictado existente
- **THEN** el dictado refleja la nueva fecha de vigencia
