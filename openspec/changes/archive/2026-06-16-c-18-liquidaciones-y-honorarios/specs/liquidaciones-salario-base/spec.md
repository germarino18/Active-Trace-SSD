## ADDED Requirements

### Requirement: ABM de SalarioBase por rol con vigencia temporal (F10.4, RN-31)

El sistema SHALL permitir administrar la tabla SalarioBase: crear, listar, actualizar y eliminar (soft delete) registros de salario base por rol con fechas de vigencia. Cada registro define el monto base para un rol en un período.

#### Scenario: Crear SalarioBase exitoso
- **GIVEN** un usuario autenticado con permiso `liquidaciones:configurar-salarios`
- **WHEN** envía `POST /api/v1/liquidaciones/salarios-base` con `{rol: "PROFESOR", monto: 150000.00, desde: "2026-01-01", hasta: null}`
- **THEN** el sistema crea el registro y responde 201 con el SalarioBase creado
- **AND** el registro queda activo con vigencia abierta

#### Scenario: Crear SalarioBase rechazado sin permiso
- **WHEN** un usuario sin `liquidaciones:configurar-salarios` intenta crear un SalarioBase
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Listar SalarioBase por rol
- **WHEN** un usuario con permiso consulta `GET /api/v1/liquidaciones/salarios-base?rol=PROFESOR`
- **THEN** el sistema devuelve todos los registros de SalarioBase para PROFESOR ordenados por `desde` descendente

#### Scenario: Listar solo vigentes en fecha
- **WHEN** un usuario consulta `GET /api/v1/liquidaciones/salarios-base?vigente_en=2026-06-01`
- **THEN** el sistema devuelve solo los registros con `desde <= 2026-06-01 AND (hasta IS NULL OR hasta >= 2026-06-01)`

#### Scenario: Actualizar SalarioBase (solo campos editables)
- **WHEN** un usuario actualiza `PATCH /api/v1/liquidaciones/salarios-base/{id}` con `{monto: 160000.00}`
- **THEN** el sistema actualiza el registro y responde 200
- **AND** los campos `tenant_id`, `id`, `created_at` no se modifican

#### Scenario: Soft delete SalarioBase
- **WHEN** un usuario elimina `DELETE /api/v1/liquidaciones/salarios-base/{id}`
- **THEN** el sistema aplica soft delete (setea `deleted_at`)
- **AND** el registro deja de aparecer en consultas normales

### Requirement: Unicidad de vigencia por rol (RN-32)

El sistema SHALL garantizar que no existan dos SalarioBase con el mismo rol y vigencias superpuestas. Si se intenta crear uno que se solape con uno existente, se rechaza con 409 Conflict.

#### Scenario: Rechazar solapamiento de vigencias
- **GIVEN** existe SalarioBase para PROFESOR con `desde=2026-01-01, hasta=2026-12-31`
- **WHEN** se intenta crear otro SalarioBase para PROFESOR con `desde=2026-06-01, hasta=null`
- **THEN** el sistema responde 409 Conflict con mensaje "Ya existe un SalarioBase vigente para el rol PROFESOR en el período solicitado"

#### Scenario: Permitir solapamiento entre roles distintos
- **GIVEN** existe SalarioBase para PROFESOR con `desde=2026-01-01, hasta=null`
- **WHEN** se crea SalarioBase para TUTOR con `desde=2026-01-01, hasta=null`
- **THEN** el sistema responde 201 (roles distintos no compiten)

### Requirement: Aislamiento multi-tenant en SalarioBase

Los SalarioBase de un tenant NO son visibles para otros tenants.

#### Scenario: Aislamiento entre tenants
- **GIVEN** tenant A tiene SalarioBase para PROFESOR con monto 150000
- **WHEN** un usuario del tenant B lista SalarioBase
- **THEN** no aparece el registro del tenant A
