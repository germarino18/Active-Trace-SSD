## Why

Los envíos masivos de comunicaciones que requieren aprobación (RN-17) ya tienen soporte completo en el backend (`C-12 comunicaciones-api`), pero el frontend no expone ningún panel para que el COORDINADOR o ADMIN pueda revisar, aprobar o rechazar esos lotes pendientes. Sin este panel, los mensajes quedan bloqueados en estado **Pendiente** indefinidamente y el flujo FL-04 queda incompleto.

## What Changes

- Nueva página `AprobacionComunicacionesPage` en `features/coordinacion/pages/` que lista todos los lotes de comunicaciones en estado **Pendiente de aprobación**.
- Por cada lote: botón "Ver preview" (reutiliza `PreviewComunicacionModal` existente), botón "Aprobar lote" y botón "Rechazar lote".
- Aprobación / rechazo individual por destinatario dentro de un lote (expandible).
- Nueva entrada en el sidebar para COORDINADOR/ADMIN: "Aprobar Comunicaciones" → `/comunicaciones/aprobar` (icono de bandeja con badge numérico con cantidad de lotes pendientes).
- Hook `useAprobacionComunicaciones` con TanStack Query para fetch y mutaciones (`comunicacion:aprobar`).
- Route guard: sólo usuarios con `comunicacion:aprobar`.

## Capabilities

### New Capabilities
- `aprobacion-comunicaciones-frontend`: Panel frontend para revisión y aprobación/rechazo de lotes de comunicaciones masivas pendientes (F3.3 / FL-04 Parte B).

### Modified Capabilities
- `ui-coordinacion`: Se agrega la sección "Aprobar Comunicaciones" al sidebar y a la estructura de rutas del rol COORDINADOR.

## Impact

- **Frontend**: `features/coordinacion/pages/AprobacionComunicacionesPage.tsx`, `features/coordinacion/hooks/useAprobacionComunicaciones.ts`, `features/coordinacion/services/aprobacionService.ts`, actualización del sidebar y router.
- **Backend API consumida**: `GET /api/comunicaciones/lotes?estado=pendiente`, `POST /api/comunicaciones/lotes/{lote_id}/aprobar`, `POST /api/comunicaciones/lotes/{lote_id}/cancelar`, endpoints individuales de `C-12`.
- **Dependencias**: `C-21` (shell layout + router + sidebar), `C-12` (comunicaciones-api).
- **Sin cambios de schema** ni migraciones — solo frontend.
