## 1. Estructura de módulo y tipos

- [x] 1.1 Crear directorio `frontend/src/features/inbox/` con subdirectorios `pages/`, `hooks/`, `services/`, `types/`
- [x] 1.2 Definir tipos en `types/inbox.types.ts`: `HiloResumen` (`id`, `remitente_id`, `remitente_nombre`, `asunto`, `ultimo_mensaje`, `ultima_fecha`, `no_leido`), `Mensaje` (`id`, `remitente_id`, `remitente_nombre`, `contenido`, `fecha_hora`), `ResponderPayload` (`contenido: string`)

## 2. Service de API

- [x] 2.1 Crear `services/inbox.service.ts` con tres funciones: `getHilos(): Promise<HiloResumen[]>`, `getHilo(id: string): Promise<Mensaje[]>`, `responder(id: string, payload: ResponderPayload): Promise<Mensaje>`
- [x] 2.2 Todas las funciones apuntan al cliente Axios centralizado en `@/shared/services/api` con prefijo `/api/v1/inbox`

## 3. Hooks TanStack Query

- [x] 3.1 Crear `hooks/useInbox.ts`: `useQuery` con `queryKey: ['inbox', 'hilos']` y `queryFn: getHilos`. Expone `{ hilos, unreadCount, isLoading, error, refetch }` donde `unreadCount = hilos.filter(h => h.no_leido).length`
- [x] 3.2 Crear `hooks/useHilo.ts`: `useQuery` con `queryKey: ['inbox', 'hilo', id]` y `queryFn: () => getHilo(id)`. Expone `{ mensajes, isLoading, error }`
- [x] 3.3 Crear `hooks/useResponder.ts`: `useMutation` con `mutationFn: ({ id, payload }) => responder(id, payload)`. En `onSuccess` invalida `['inbox', 'hilo', id]` y `['inbox', 'hilos']`

## 4. InboxPage

- [x] 4.1 Crear `pages/InboxPage.tsx` (<200 LOC) usando `useInbox`. Spinner durante carga, `EmptyState` para error y bandeja vacía
- [x] 4.2 Renderizar lista de hilos: avatar con inicial, nombre del remitente, asunto, preview, fecha formateada con `es-AR`. Fondo resaltado y badge "Nuevo" si `no_leido: true`
- [x] 4.3 Cada hilo es un `Link` a `/inbox/:id`

## 5. HiloPage

- [x] 5.1 Crear `pages/HiloPage.tsx` (<200 LOC) que recibe `id` de `useParams()` y usa `useHilo(id)`
- [x] 5.2 Renderizar mensajes en orden cronológico: nombre del remitente, contenido, fecha formateada
- [x] 5.3 Integrar formulario de respuesta con React Hook Form + Zod: campo `contenido` requerido, máximo 2000 caracteres. Botón "Enviar" deshabilitado mientras `isPending` o contenido vacío
- [x] 5.4 Al submit exitoso: limpiar el formulario. En 404 de la API: mostrar `EmptyState` con botón "Volver a mensajes"

## 6. Router

- [x] 6.1 Registrar ruta `/inbox` → `InboxPage` con `RouteGuard` requiriendo `inbox:acceder`
- [x] 6.2 Registrar ruta `/inbox/:id` → `HiloPage` con `RouteGuard` requiriendo `inbox:acceder`

## 7. Sidebar

- [x] 7.1 Agregar ítem "Mensajes" (ruta `/inbox`, permiso `inbox:acceder`, icono `mail`) a las secciones de sidebar para TUTOR, PROFESOR, COORDINADOR y ADMIN
- [x] 7.2 Conectar el badge numérico del ítem con `useInbox().unreadCount` — mostrar solo si `unreadCount > 0`

## 8. Tests

- [x] 8.1 Test de `useInbox`: verifica que `unreadCount` se calcula correctamente (2 no-leídos de 3 hilos → 2; todos leídos → 0)
- [x] 8.2 Test de `InboxPage`: renderiza lista con hilos, muestra badge "Nuevo" solo en hilos no leídos, muestra `EmptyState` cuando la lista está vacía
- [x] 8.3 Test de `HiloPage`: renderiza mensajes en orden cronológico, deshabilita botón con contenido vacío, invalida queryKey tras respuesta exitosa
- [x] 8.4 Test de validación Zod: rechaza `contenido` vacío y `contenido` > 2000 chars
