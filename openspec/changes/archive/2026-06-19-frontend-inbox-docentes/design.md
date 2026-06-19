## Context

El backend C-20 ya expone tres endpoints de mensajería interna: `GET /api/v1/inbox/hilos`, `GET /api/v1/inbox/hilos/:id` y `POST /api/v1/inbox/hilos/:id/responder`. El frontend tiene una implementación análoga para alumnos en `features/alumno/pages/AlumnoInboxPage.tsx`. El módulo docente replica ese patrón adaptando las rutas de API y ubicándolo en su propia feature.

El sidebar actual soporta secciones por rol (spec `sidebar-role-sections`); se agrega el ítem "Mensajes" a las secciones de TUTOR, PROFESOR, COORDINADOR y ADMIN.

## Goals / Non-Goals

**Goals:**
- `InboxPage`: lista de hilos para docentes, con indicador de no-leídos.
- `HiloPage`: vista de conversación (mensajes cronológicos) y formulario de respuesta.
- Hooks `useInbox`, `useHilo`, `useResponder` encapsulando fetch y mutation.
- Ítem "Mensajes" en sidebar con badge de no-leídos para los cuatro roles docentes.
- Rutas `/inbox` y `/inbox/:id` registradas en el router.

**Non-Goals:**
- Creación de nuevos hilos (no es parte de F3.4; la generación la hace el sistema o coordinación vía otro flujo).
- Paginación de hilos (scope inicial: todos los hilos del usuario; se pagina en un change posterior si es necesario).
- Notificaciones push o WebSocket (fuera de scope).
- Cambios de backend.

## Decisions

### D1: Estructura de feature independiente (`features/inbox/`)
Alternativas: (a) co-ubicar con `features/alumno/` reutilizando páginas, (b) feature propia.

Se elige **(b)** porque los roles docentes son distintos, el service apunta a `/api/v1/inbox/` (diferente del servicio de alumno), y mantener módulos separados respeta el límite de 200 LOC por componente sin mezclar audiencias.

### D2: Tres hooks especializados en lugar de un hook genérico
`useInbox` → lista de hilos; `useHilo(id)` → mensajes del hilo; `useResponder(id)` → mutation de respuesta. Este patrón espeja TanStack Query con `queryKey` predecibles y permite invalidación precisa tras la respuesta.

### D3: Badge de no-leídos en sidebar via `useInbox`
El sidebar llama a `useInbox` para obtener `count` de hilos con `no_leido: true`. Alternativa descartada: endpoint dedicado de conteo. Se prefiere reutilizar el hook ya montado para evitar una llamada extra.

### D4: Reutilizar visual de `AlumnoInboxPage` directamente
El diseño de lista de hilos y la vista de hilo siguen el mismo sistema de tokens (`--primary`, `--outline-variant`, `EmptyState`, `Badge`) para mantener consistencia con el design system Obsidian sin duplicar estilos.

## Risks / Trade-offs

- **Stale badge count**: el badge en el sidebar usa el cache de `useInbox`; si el usuario responde en `HiloPage`, la invalidación de `['inbox', 'hilos']` actualiza el conteo. Riesgo bajo: TanStack Query refresca al hacer focus.
- **Rutas sin guard de permiso**: las rutas `/inbox` y `/inbox/:id` deben protegerse con `inbox:acceder` vía el `RouteGuard` existente. Si se omite, un alumno con la URL podría acceder aunque no vería datos (el backend los rechaza con 403).
