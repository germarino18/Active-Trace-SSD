## Why

El sistema necesita un módulo completo de liquidaciones y honorarios para que el rol FINANZAS pueda calcular, cerrar y auditar los pagos a docentes de forma precisa y trazable. Actualmente no existe ninguna funcionalidad para gestionar la grilla salarial, calcular haberes por período, ni administrar facturas de docentes monotributistas. Sin este módulo, la plataforma no puede operar como sistema de gestión académica integral.

## What Changes

- **Nuevo modelo de datos**: 6 entidades — `SalarioBase`, `SalarioPlus`, `ClavePlus`, `MateriaClavePlus`, `Liquidacion`, `Factura`.
- **Grilla salarial ABM con vigencia temporal** (SalarioBase por rol, SalarioPlus por grupo×rol, ClavePlus como catálogo de categorías de materias).
- **Cálculo automático de liquidación por período**: monto base vigente + suma de plus aplicables = total. Segmentación NEXO / factura / general con KPIs de cabecera.
- **Cierre de liquidación inmutable** (RN-22): una vez cerrada no puede modificarse; registro de auditoría `LIQUIDACION_CERRAR`.
- **Gestión de facturas** para docentes que facturan (RN-35): ABM de comprobantes, cambio de estado Pendiente→Abonada, docentes facturadores excluidos de la liquidación general.
- **Nuevos endpoints** bajo `/api/liquidaciones/*` y `/api/facturas/*` con guards `liquidaciones:*` (rol FINANZAS).
- **Migración Alembic 016** con las 6 nuevas tablas + índices + seed del permiso `liquidaciones:configurar-salarios` si no existe.

## Capabilities

### New Capabilities
- `liquidaciones-salario-base`: ABM de salario base por rol con vigencia temporal. Monto base según grilla vigente en el período.
- `liquidaciones-plus`: ABM de plus salarial por grupo y rol con vigencia temporal. Acumulación de múltiples plus.
- `liquidaciones-clave-plus`: Catálogo de claves de materias (ClavePlus) y su asignación a materias (MateriaClavePlus) con vigencia.
- `liquidaciones-calculo`: Lógica de negocio para calcular liquidación del período: selección de base vigente por rol, suma de plus aplicables según materias del docente, cálculo de total, segmentación NEXO/factura/general con KPIs de cabecera.
- `liquidaciones-api`: Endpoints REST para ver liquidaciones del período (F10.1), cerrar liquidación (F10.2, inmutable), historial (F10.3), y administración de grilla salarial (F10.4).
- `facturas-api`: Endpoints REST para ABM de facturas de docentes facturadores (F10.5), cambio de estado Pendiente→Abonada, listado con filtros.

### Modified Capabilities
- Ninguna. No se modifican requerimientos de capacidades existentes; se agregan capacidades nuevas.

## Impact

- **Backend**: Se agregan 6 modelos, ~6 schemas, ~6 repositorios, 2 servicios (LiquidacionService, FacturaService), 2 routers, 1 migración Alembic (016).
- **Permisos**: Se usan `Perm.LIQUIDACIONES_CERRAR` y `Perm.FACTURAS_GESTIONAR` ya seedeados en migración 003. Puede requerir seed de `Perm.LIQUIDACIONES_CONFIGURAR_SALARIOS` si no existe.
- **Auditoría**: Se usa `AccionAuditoria.LIQUIDACION_CERRAR` ya definido.
- **Modelo existente**: `Usuario.facturador` (booleano) ya existe y es usado para determinar exclusión por factura.
- **Dependencias**: Requiere `C-07 usuarios-y-asignaciones` (completado) — usa `Usuario`, `Asignacion`, `Dictado` y `Materia`.
- **No breaking**: No modifica APIs, modelos ni migraciones existentes.
