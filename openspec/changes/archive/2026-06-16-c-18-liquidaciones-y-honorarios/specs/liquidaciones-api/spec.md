## ADDED Requirements

### Requirement: Vista de liquidaciones del período (F10.1)

El sistema SHALL exponer endpoints REST para consultar liquidaciones del período con segmentación y KPIs.

#### Endpoints

| Método | Ruta | Permiso | Descripción |
|--------|------|---------|-------------|
| `GET` | `/api/v1/liquidaciones` | `liquidaciones:ver` | Vista segmentada del período |
| `GET` | `/api/v1/liquidaciones/historial` | `liquidaciones:ver` | Historial de liquidaciones cerradas |
| `POST` | `/api/v1/liquidaciones/calcular` | `liquidaciones:calcular` | Calcular/recalcular período |
| `POST` | `/api/v1/liquidaciones/{id}/cerrar` | `liquidaciones:cerrar` | Cerrar liquidación inmutable |
| `GET` | `/api/v1/liquidaciones/salarios-base` | `liquidaciones:configurar-salarios` | Listar SalarioBase |
| `POST` | `/api/v1/liquidaciones/salarios-base` | `liquidaciones:configurar-salarios` | Crear SalarioBase |
| `PATCH` | `/api/v1/liquidaciones/salarios-base/{id}` | `liquidaciones:configurar-salarios` | Actualizar SalarioBase |
| `DELETE` | `/api/v1/liquidaciones/salarios-base/{id}` | `liquidaciones:configurar-salarios` | Soft delete SalarioBase |
| `GET` | `/api/v1/liquidaciones/salarios-plus` | `liquidaciones:configurar-salarios` | Listar SalarioPlus |
| `POST` | `/api/v1/liquidaciones/salarios-plus` | `liquidaciones:configurar-salarios` | Crear SalarioPlus |
| `PATCH` | `/api/v1/liquidaciones/salarios-plus/{id}` | `liquidaciones:configurar-salarios` | Actualizar SalarioPlus |
| `DELETE` | `/api/v1/liquidaciones/salarios-plus/{id}` | `liquidaciones:configurar-salarios` | Soft delete SalarioPlus |
| `GET` | `/api/v1/liquidaciones/claves-plus` | `liquidaciones:configurar-salarios` | Listar ClavePlus |
| `POST` | `/api/v1/liquidaciones/claves-plus` | `liquidaciones:configurar-salarios` | Crear ClavePlus |
| `PATCH` | `/api/v1/liquidaciones/claves-plus/{id}` | `liquidaciones:configurar-salarios` | Actualizar ClavePlus |
| `DELETE` | `/api/v1/liquidaciones/claves-plus/{id}` | `liquidaciones:configurar-salarios` | Soft delete ClavePlus |
| `GET` | `/api/v1/liquidaciones/materias-clave-plus` | `liquidaciones:configurar-salarios` | Listar MateriaClavePlus |
| `POST` | `/api/v1/liquidaciones/materias-clave-plus` | `liquidaciones:configurar-salarios` | Crear MateriaClavePlus |
| `DELETE` | `/api/v1/liquidaciones/materias-clave-plus/{id}` | `liquidaciones:configurar-salarios` | Soft delete MateriaClavePlus |

### Requirement: Cierre de liquidación inmutable (F10.2, RN-22)

El sistema SHALL permitir cerrar una liquidación individual. Una vez cerrada, NO puede modificarse.

#### Scenario: Cierre exitoso con auditoría
- **WHEN** `POST /api/v1/liquidaciones/{id}/cerrar` con permiso `liquidaciones:cerrar`
- **THEN** la Liquidacion cambia a `estado=Cerrada`
- **AND** se registra un AuditLog con `accion=LIQUIDACION_CERRAR, detalle={liquidacion_id, usuario_id, periodo, total}`
- **AND** responde 200 con la liquidación actualizada

#### Scenario: Cierre de liquidación ya cerrada
- **GIVEN** una Liquidacion con `estado=Cerrada`
- **WHEN** se intenta cerrar nuevamente
- **THEN** el sistema responde 409 Conflict

#### Scenario: Cierre rechazado sin permiso
- **WHEN** un usuario sin `liquidaciones:cerrar` intenta cerrar
- **THEN** el sistema responde 403 Forbidden

### Requirement: Protección de liquidación cerrada

Cualquier intento de modificar una liquidación cerrada es rechazado a nivel de servicio.

#### Scenario: Update rechazado
- **WHEN** se intenta `PATCH /api/v1/liquidaciones/{id}` con estado Cerrada
- **THEN** el sistema responde 409 Conflict: "No se puede modificar una liquidación cerrada"

### Requirement: Grilla salarial ABM (F10.4)

El sistema SHALL exponer endpoints CRUD para SalarioBase y SalarioPlus con soft delete, siguiendo el patrón del proyecto.

#### Scenario: CRUD completo de SalarioBase
- **WHEN** se crea, lista, actualiza y elimina un SalarioBase
- **THEN** cada operación funciona según el patrón del proyecto (Create→201, List→200, Update→200, Delete→200 con soft delete)

#### Scenario: CRUD completo de SalarioPlus
- **WHEN** se crea, lista, actualiza y elimina un SalarioPlus
- **THEN** cada operación funciona según el patrón del proyecto

### Requirement: Permisos

Todos los endpoints de liquidaciones SHALL estar protegidos por RBAC.

| Endpoint | Permiso Requerido | Roles que lo tienen (seed) |
|----------|-------------------|---------------------------|
| `GET /api/v1/liquidaciones` | `liquidaciones:ver` | FINANZAS, ADMIN |
| `POST /api/v1/liquidaciones/calcular` | `liquidaciones:calcular` | FINANZAS |
| `POST /api/v1/liquidaciones/{id}/cerrar` | `liquidaciones:cerrar` | FINANZAS |
| `* /api/v1/liquidaciones/salarios-base` | `liquidaciones:configurar-salarios` | FINANZAS |
| `* /api/v1/liquidaciones/salarios-plus` | `liquidaciones:configurar-salarios` | FINANZAS |
| `* /api/v1/liquidaciones/claves-plus` | `liquidaciones:configurar-salarios` | FINANZAS |
| `* /api/v1/liquidaciones/materias-clave-plus` | `liquidaciones:configurar-salarios` | FINANZAS |
