## ADDED Requirements

### Requirement: Dictado con vigencia temporal configurable
El modelo `Dictado` SHALL soportar los campos `vig_desde: Optional[Date]` y `vig_hasta: Optional[Date]`. La vigencia define el período durante el cual el dictado está activo para cursado. Un dictado sin fechas de vigencia se considera vigente. La vigencia NO afecta la eliminación lógica — un dictado puede estar fuera de vigencia pero no eliminado (soft delete independiente).

#### Scenario: Dictado con vigencia acotada
- **WHEN** un ADMIN crea un dictado con `vig_desde = "2026-03-01"` y `vig_hasta = "2026-12-15"`
- **THEN** el dictado se persiste y sus fechas de vigencia son visibles en la respuesta

#### Scenario: Dictado sin vigencia (siempre vigente)
- **WHEN** un ADMIN crea un dictado sin especificar `vig_desde` ni `vig_hasta`
- **THEN** el dictado se persiste y se considera vigente

#### Scenario: Vigencia no bloquea estado del dictado
- **WHEN** un dictado tiene `vig_hasta` en el pasado y estado Activo
- **THEN** el dictado sigue siendo visible y editable (vigencia y estado son conceptos independientes)

### Requirement: Consulta de dictados vigentes por fecha
El endpoint `GET /api/admin/dictados` SHALL aceptar un query param opcional `vigente: Optional[bool]`. Cuando `vigente=true`, SHALL devolver solo dictados cuya fecha actual está entre `vig_desde` y `vig_hasta` (o que no tienen fechas definidas).

#### Scenario: Filtrar dictados vigentes
- **WHEN** un ADMIN invoca `GET /api/admin/dictados?vigente=true`
- **THEN** solo se devuelven dictados sin vigencia o con fecha actual dentro del rango
