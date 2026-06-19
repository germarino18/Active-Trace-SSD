## ADDED Requirements

### Requirement: InboxPage lista hilos del docente

`InboxPage` SHALL mostrar la bandeja de hilos de mensajes del usuario autenticado (TUTOR, PROFESOR, COORDINADOR, ADMIN), consumiendo `GET /api/v1/inbox/hilos`. Cada hilo SHALL mostrar: avatar con inicial del remitente, nombre del remitente, asunto, preview del último mensaje, fecha y badge "Nuevo" si `no_leido: true`. Los hilos SHALL estar ordenados por `ultima_fecha` descendente (el backend ya los devuelve ordenados).

#### Scenario: Hilos cargados con mensajes sin leer
- **WHEN** el usuario tiene hilos con `no_leido: true`
- **THEN** `InboxPage` muestra cada hilo con badge "Nuevo" y fondo resaltado con `--primary` al 3%

#### Scenario: Todos los hilos leídos
- **WHEN** el usuario tiene hilos pero todos tienen `no_leido: false`
- **THEN** `InboxPage` muestra los hilos sin badge y con fondo normal

#### Scenario: Bandeja vacía
- **WHEN** el usuario no tiene hilos
- **THEN** `InboxPage` muestra `EmptyState` con icon="mail" y título "No tenés mensajes"

#### Scenario: Error de carga
- **WHEN** la llamada a `GET /api/v1/inbox/hilos` falla
- **THEN** `InboxPage` muestra `EmptyState` con icon="error", título "Error al cargar mensajes" y botón "Reintentar"

#### Scenario: Clic en un hilo navega a HiloPage
- **WHEN** el usuario hace clic en cualquier hilo de la lista
- **THEN** el router navega a `/inbox/:id` donde `:id` es el `id` del hilo

---

### Requirement: HiloPage muestra mensajes y permite responder

`HiloPage` SHALL mostrar todos los mensajes del hilo identificado por `:id`, consumiendo `GET /api/v1/inbox/hilos/:id`. Los mensajes SHALL estar ordenados cronológicamente (ascendente). La página SHALL incluir un formulario de respuesta con campo `contenido` (textarea, máximo 2000 caracteres). Al enviar, SHALL llamar a `POST /api/v1/inbox/hilos/:id/responder`.

#### Scenario: Mensajes cargados correctamente
- **WHEN** el usuario accede a `/inbox/:id` y el hilo existe
- **THEN** `HiloPage` muestra todos los mensajes del hilo en orden cronológico

#### Scenario: Cada mensaje muestra remitente y fecha
- **WHEN** se renderizan los mensajes del hilo
- **THEN** cada mensaje muestra `remitente_nombre`, `contenido` y `fecha_hora` formateada en es-AR

#### Scenario: Envío de respuesta exitoso
- **WHEN** el usuario escribe una respuesta y envía el formulario
- **THEN** `useResponder` llama a `POST /api/v1/inbox/hilos/:id/responder` con `{ contenido }`
- **THEN** al recibir 201, se invalida el queryKey `['inbox', 'hilo', id]` para refrescar los mensajes
- **THEN** el textarea queda vacío

#### Scenario: Respuesta con contenido vacío
- **WHEN** el usuario intenta enviar el formulario con textarea vacío
- **THEN** el botón "Enviar" está deshabilitado o Zod/RHF muestra error de validación

#### Scenario: Respuesta con más de 2000 caracteres
- **WHEN** el usuario escribe más de 2000 caracteres en el textarea
- **THEN** el formulario muestra error de validación y no envía la petición

#### Scenario: Hilo no encontrado (404)
- **WHEN** la API devuelve 404 para el `:id` solicitado
- **THEN** `HiloPage` muestra `EmptyState` con mensaje "Mensaje no encontrado" y botón para volver a `/inbox`

---

### Requirement: Hook useInbox expone lista de hilos y conteo de no-leídos

`useInbox` SHALL encapsular `useQuery` con `queryKey: ['inbox', 'hilos']` y `queryFn` apuntando a `GET /api/v1/inbox/hilos`. SHALL exponer `{ hilos, unreadCount, isLoading, error, refetch }` donde `unreadCount` es el número de hilos con `no_leido: true`.

#### Scenario: unreadCount correcto
- **WHEN** la API devuelve 3 hilos, 2 con `no_leido: true`
- **THEN** `useInbox().unreadCount` es `2`

#### Scenario: unreadCount es 0 cuando todos leídos
- **WHEN** todos los hilos tienen `no_leido: false`
- **THEN** `useInbox().unreadCount` es `0`

---

### Requirement: Rutas /inbox e /inbox/:id protegidas por permiso inbox:acceder

Las rutas `/inbox` y `/inbox/:id` SHALL estar registradas en el router y protegidas con el permiso `inbox:acceder` usando el `RouteGuard` existente. Un usuario sin ese permiso SHALL ser redirigido a la página 403.

#### Scenario: Usuario con permiso accede a /inbox
- **WHEN** el usuario tiene `inbox:acceder` y navega a `/inbox`
- **THEN** `InboxPage` se renderiza correctamente

#### Scenario: Usuario sin permiso es redirigido
- **WHEN** el usuario no tiene `inbox:acceder` y navega a `/inbox`
- **THEN** el `RouteGuard` redirige a la página 403
