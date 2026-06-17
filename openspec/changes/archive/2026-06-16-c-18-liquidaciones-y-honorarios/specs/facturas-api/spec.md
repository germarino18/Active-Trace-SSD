## ADDED Requirements

### Requirement: ABM de facturas de docentes facturadores (F10.5)

El sistema SHALL permitir a FINANZAS gestionar facturas presentadas por docentes que trabajan bajo modalidad de facturación independiente (facturador=true). Las facturas se gestionan por separado de la liquidación general.

#### Endpoints

| Método | Ruta | Permiso | Descripción |
|--------|------|---------|-------------|
| `GET` | `/api/v1/facturas` | `facturas:gestionar` | Listar facturas con filtros |
| `POST` | `/api/v1/facturas` | `facturas:gestionar` | Crear factura |
| `PATCH` | `/api/v1/facturas/{id}` | `facturas:gestionar` | Actualizar factura |
| `DELETE` | `/api/v1/facturas/{id}` | `facturas:gestionar` | Soft delete factura |
| `POST` | `/api/v1/facturas/{id}/abonar` | `facturas:gestionar` | Marcar como abonada |

### Requirement: Listado de facturas con filtros

El sistema SHALL permitir listar facturas con filtros por docente, estado, período y rango de fechas.

#### Scenario: Listar todas las facturas
- **WHEN** `GET /api/v1/facturas`
- **THEN** devuelve todas las facturas del tenant ordenadas por `cargada_at` descendente

#### Scenario: Filtrar por docente
- **WHEN** `GET /api/v1/facturas?usuario_id=X`
- **THEN** devuelve solo las facturas del docente X

#### Scenario: Filtrar por estado
- **WHEN** `GET /api/v1/facturas?estado=Pendiente`
- **THEN** devuelve solo facturas pendientes

#### Scenario: Filtrar por período
- **WHEN** `GET /api/v1/facturas?periodo=2026-06`
- **THEN** devuelve solo facturas de ese período

#### Scenario: Filtrar por rango de carga
- **WHEN** `GET /api/v1/facturas?desde=2026-01-01&hasta=2026-06-30`
- **THEN** devuelve facturas cargadas en ese rango de fechas

### Requirement: Creación de factura

El sistema SHALL permitir registrar una factura presentada por un docente facturador.

#### Scenario: Crear factura exitosa
- **WHEN** `POST /api/v1/facturas` con `{usuario_id, periodo: "2026-06", detalle: "Honorarios junio 2026", referencia_archivo: "facturas/docente_x_jun2026.pdf", tamano_kb: 245.5}`
- **THEN** el sistema crea la factura con `estado=Pendiente, cargada_at=ahora`
- **AND** responde 201

#### Scenario: Crear factura para docente no facturador
- **WHEN** se intenta crear factura para un usuario con `facturador=false`
- **THEN** el sistema responde 422 Unprocessable Entity: "El usuario no está configurado como facturador"

### Requirement: Cambio de estado Pendiente→Abonada

El sistema SHALL permitir marcar una factura como abonada, registrando la fecha de pago.

#### Scenario: Abonar factura exitoso
- **WHEN** `POST /api/v1/facturas/{id}/abonar`
- **THEN** la factura cambia a `estado=Abonada`
- **AND** `abonada_at` se setea a la fecha/hora actual
- **AND** responde 200

#### Scenario: Abonar factura ya abonada
- **GIVEN** factura con `estado=Abonada`
- **WHEN** se intenta abonar nuevamente
- **THEN** el sistema responde 409 Conflict

### Requirement: Soft delete de facturas

Las facturas siguen el patrón de soft delete del proyecto.

#### Scenario: Eliminar factura
- **WHEN** `DELETE /api/v1/facturas/{id}`
- **THEN** el sistema aplica soft delete

### Requirement: Aislamiento multi-tenant en facturas

Facturas de diferentes tenants NO son visibles entre sí.

#### Scenario: Aislamiento
- **GIVEN** tenant A tiene facturas registradas
- **WHEN** usuario del tenant B lista facturas
- **THEN** no aparecen las facturas del tenant A
