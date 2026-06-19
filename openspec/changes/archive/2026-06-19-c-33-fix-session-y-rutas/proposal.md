## Why

El frontend presenta dos fallas críticas que bloquean la usabilidad diaria: la sesión se pierde al recargar la página porque el `tenantId` nunca se persiste (solo vive en un `useRef` en memoria), y cinco ítems del sidebar navegan a rutas inexistentes (`/atrasados`, `/comunicacion`, `/nexo/atrasados`, `/nexo/encuentros`, `/nexo/tareas`) entregando 404 al usuario. Ambos deben resolverse antes de cualquier demo o uso real.

## What Changes

- **Persistencia de tenant en cookie**: Al hacer login, guardar el `tenantId` en una cookie JS de sesión (`js-trace-tenant`). Al montar `AuthProvider`, leer la cookie y usarla en el `attemptRefresh` para restaurar la sesión sin pedir login al usuario.
- **Ruta `/atrasados`**: Nueva página standalone `AtrasadosGeneralPage` que lista los alumnos atrasados de todas las materias asignadas al docente, con filtro por materia.
- **Ruta `/comunicacion`**: Nueva página standalone `ComunicacionGeneralPage` que agrega las comunicaciones enviadas/pendientes del docente por materia, con acceso rápido al flujo de envío.
- **Rutas NEXO** (`/nexo/atrasados`, `/nexo/encuentros`, `/nexo/tareas`): Páginas stub con mensaje "En desarrollo — próximamente disponible" que previenen el 404 y dejan la navegación intacta.
- **Delta spec `auth`**: Actualizar escenario de montaje para reflejar que el tenant se lee de cookie y la sesión se restaura transparentemente.
- **Delta spec `sidebar-role-sections`**: Clarificar que `/atrasados` y `/comunicacion` son rutas reales registradas en el router.

## Capabilities

### New Capabilities
- `session-cookie-persistence`: Persistencia del tenantId entre reloads usando una cookie JS de corta duración (mismo scope que la sesión del browser), eliminando el re-login forzado.
- `atrasados-general-view`: Vista consolidada de alumnos atrasados para el docente, sin necesitar seleccionar materia primero.
- `comunicacion-general-view`: Vista consolidada de comunicaciones del docente agrupadas por materia.
- `nexo-stubs`: Páginas placeholder para el rol NEXO que evitan el 404 mientras las vistas reales se implementan en un change futuro.

### Modified Capabilities
- `auth`: El escenario de montaje del `AuthProvider` cambia: ahora lee el tenant de cookie antes de intentar refresh.
- `sidebar-role-sections`: Las rutas `/atrasados` y `/comunicacion` dejan de ser referencias muertas y se convierten en rutas reales registradas.

## Impact

- **Frontend**: `AuthContext.tsx`, `App.tsx` (nuevas rutas), 4 archivos de páginas nuevas (`AtrasadosGeneralPage`, `ComunicacionGeneralPage`, 3 stubs NEXO), dependencia `js-cookie` (o native `document.cookie`).
- **Backend**: Sin cambios. Los endpoints existentes (`/api/v1/calificaciones/atrasados`, `/api/v1/comunicaciones/`) ya exponen la data necesaria.
- **Tests**: Tests unitarios para la lógica de cookie en `AuthContext`, tests de rutas nuevas.
- **Sin breaking changes**: Los flujos existentes por materia (`/materias/:id/atrasados`) se mantienen intactos.
