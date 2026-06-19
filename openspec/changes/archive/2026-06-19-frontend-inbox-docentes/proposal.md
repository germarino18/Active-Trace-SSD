## Why

Los roles docentes (TUTOR, PROFESOR, COORDINADOR, ADMIN) carecen actualmente de una bandeja de mensajes en el frontend, aunque el backend ya expone `/api/v1/inbox/*` (C-20). Sin este change, los mensajes internos no son accesibles para los destinatarios docentes, bloqueando el flujo de mensajería interna F3.4 / F11.2.

## What Changes

- Nueva feature `features/inbox/` con páginas `InboxPage` (bandeja de hilos) y `HiloPage` (vista de conversación y respuesta).
- Tres hooks TanStack Query: `useInbox`, `useHilo`, `useResponder`.
- Ítem "Mensajes" en el sidebar para los roles TUTOR, PROFESOR, COORDINADOR, ADMIN con badge de no-leídos.
- Ruta `/inbox` y `/inbox/:id` registradas en el router principal.
- El patrón visual y de datos reutiliza `AlumnoInboxPage.tsx` (bandeja de alumno ya existente), adaptado para el API `/api/v1/inbox/hilos` de docentes.

## Capabilities

### New Capabilities

- `inbox-docentes-frontend`: Bandeja de mensajes internos (`InboxPage`) y vista de hilo con respuesta (`HiloPage`) para roles docentes, con hooks de fetch y sidebar integrado.

### Modified Capabilities

- `sidebar-role-sections`: Se agrega la sección "Mensajes" con enlace a `/inbox` y badge de no-leídos para roles TUTOR, PROFESOR, COORDINADOR, ADMIN.

## Impact

- **Frontend**: nuevo módulo `features/inbox/` (pages, hooks, services, types). Modificación de sidebar y router.
- **API consumida**: `GET /api/v1/inbox/hilos`, `GET /api/v1/inbox/hilos/:id`, `POST /api/v1/inbox/hilos/:id/responder` (ya disponibles por C-20).
- **Sin cambios de backend**: este change es exclusivamente frontend.
- **Dependencias**: C-21 (shell + auth + router base), C-20 (API inbox backend).
