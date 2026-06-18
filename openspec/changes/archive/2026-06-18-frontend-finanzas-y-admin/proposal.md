## Why

C-21 (shell + auth) y C-22 (PROFESOR workspace) y C-23 (COORDINADOR workspace) cubren todos los roles operativos. Restan los roles FINANZAS y ADMIN, que requieren funcionalidades no cubiertas: liquidación de honorarios, grilla salarial, gestión de facturas, administración de la estructura académica, usuarios del tenant, y paneles de auditoría. Sin este cambio, estos roles no pueden operar en el frontend.

## What Changes

Se agregan dos nuevos feature modules al frontend:

### FINANZAS
- **Vista de liquidaciones del período**: tabla segmentada (general / NEXO / factura) con KPIs (total docentes, total a pagar, etc.), desglose por docente con detalle de rol, comisiones, salario base, plus aplicables y total.
- **Cierre de liquidación**: acción que convierte la liquidación en inmutable.
- **Historial de liquidaciones**: acceso a liquidaciones cerradas de períodos anteriores.
- **Grilla salarial**: gestión de salario base por rol (PROFESOR/TUTOR/NEXO/COORDINADOR) con vigencia, y gestión de plus con clave única, rol, descripción y vigencia.
- **Gestión de facturas**: ABM de comprobantes de docentes que facturan, con filtros (docente, estado, fechas), carga de archivo adjunto y cambio de estado pendiente/abonada.

### ADMIN
- **Estructura académica**: ABM de carreras, cohortes y materias con estados (activo/inactivo).
- **Usuarios del tenant**: listado con filtros, creación y edición de usuarios, asignación de roles.
- **Panel de auditoría**: log completo de auditoría con filtros por fecha, usuario, materia, tipo de acción; panel de métricas de uso del sistema.

## Capabilities

### New Capabilities
- `liquidaciones-frontend`: Vista de liquidaciones del período con segmentación, KPIs, cierre e historial
- `grilla-salarial-frontend`: Gestión de salario base por rol y plus adicionales con vigencia temporal
- `facturas-frontend`: ABM de comprobantes de docentes que facturan con carga de archivo y cambio de estado
- `estructura-academica-frontend`: ABM de carreras, cohortes y materias con cambio de estado
- `usuarios-tenant-frontend`: Gestión de usuarios del tenant con asignación de roles
- `auditoria-frontend`: Panel de log completo de auditoría con filtros
- `metricas-frontend`: Panel de métricas de uso del sistema

### Modified Capabilities
- *(ninguna — son todas capacidades nuevas de frontend)*

## Impact

- **Nuevos feature modules**: `features/finanzas/` y `features/admin/` con estructura `{components,hooks,services,types,pages}`
- **Nuevas rutas**: bajo `AuthGuard / AppLayout` para FINANZAS y ADMIN
- **Sidebar**: nuevos items con permisos `liquidaciones:*`, `facturas:*`, `estructura:*`, `usuarios:*`, `auditoria:*`
- **Sin cambios en backend**: consume endpoints existentes de C-06, C-07, C-18, C-19
- **Sin cambios en shared**: reutiliza componentes compartidos existentes
