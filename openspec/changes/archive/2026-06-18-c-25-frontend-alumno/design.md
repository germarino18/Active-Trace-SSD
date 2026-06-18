## Context

El frontend actual está organizado en **módulos por feature**: `academico/` (PROFESOR), `coordinacion/` (COORDINADOR), `finanzas/` (FINANZAS), `admin/` (ADMIN), `auth/` (público). Todos comparten el mismo shell (`AppLayout`, `Sidebar`, `AuthGuard`, `GuestGuard`) definido en `C-21`.

El backend ya expone todos los endpoints necesarios para el alumno:
- **Estado académico** (`C-10/C-11`): calificaciones, atrasados, ranking, notas finales
- **Coloquios** (`C-14`): convocatorias activas, reservas, cancelación
- **Avisos** (`C-15`): avisos por scope + acknowledgment
- **Programas** (`C-17`): programas por materia
- **Mensajería** (`C-20`): hilos y mensajes
- **Comunicaciones** (`C-12`): comunicaciones recibidas
- **Perfil** (`C-20`): datos propios (ya existe `/profile`)

Lo que **no existe** es un endpoint consolidado para el dashboard del alumno — hoy cada feature se consulta por separado. Este change agrega ese endpoint y construye toda la capa de presentación.

## Goals / Non-Goals

**Goals:**
- Crear el feature module `alumno/` siguiendo la misma estructura que los módulos existentes
- Dashboard consolidado con cards de materia + progreso + indicadores de estado
- Vista de estado académico detallado por materia
- Flujo completo de reserva de coloquios (listar → reservar → cancelar)
- Tablón de avisos con acknowledgment
- Listado de programas + fechas académicas
- Bandeja de mensajes internos (inbox)
- Historial de comunicaciones recibidas
- Sidebar con items visibles solo para ALUMNO

**Non-Goals:**
- SSO con Moodle (se deja para iteración futura, RF-47)
- Notificaciones push web (RF-50, futuro)
- App móvil (Fase 3+)
- Chat en tiempo real (Fase 3+)

## Decisions

### D1: Feature module `alumno/` autocontenido
**Decisión**: Crear `frontend/src/features/alumno/` con la misma estructura que los demás features: `pages/`, `components/`, `hooks/`, `services/`, `types/`.

**Rationale**: Consistencia con la arquitectura existente. Cada feature es autocontenido, lo que facilita el lazy-loading y el mantenimiento.

### D2: Sidebar con permisos específicos (no wildcards)
**Decisión**: Los items del sidebar para ALUMNO usan permisos específicos (`estado-academico:ver`, `evaluacion:reservar`, `avisos:confirmar`), no wildcards (`estado-academico:*`).

**Rationale**: El backend resuelve permisos granulares, no wildcards. Usar permisos específicos evita el problema que tiene TUTOR hoy (sidebar no muestra nada porque los items piden `*` y el rol tiene `:ver`). Además, es más preciso: un ALUMNO puede no tener todos los wildcards.

### D3: Endpoint consolidado `/api/alumno/dashboard`
**Decisión**: Crear un endpoint nuevo en el backend (`GET /api/alumno/dashboard`) que agregue en una sola respuesta los datos del dashboard del alumno: materia cursadas con progreso, atrasos, próximos coloquios, avisos no leídos, comunicaciones no leídas.

**Rationale**: Evita hacer 5-6 requests paralelos desde el frontend, simplifica el loading state y mejora la performance. El endpoint orquesta llamadas a los servicios existentes (no duplica lógica). Usa el permiso `estado-academico:ver` del ALUMNO.

**Alternativa considerada**: Composición desde el frontend con TanStack Query.
- **Pros**: Sin cambios en backend.
- **Contras**: Múltiples round-trips, error handling complejo, carga secuencial en el peor caso.
- **Veredicto**: Rechazada. La latencia de múltiples requests degrada la UX del dashboard que es la pantalla principal del alumno.

### D4: Lazy-loading de rutas del alumno
**Decisión**: Todas las páginas del feature `alumno/` se cargan con `React.lazy()` + `Suspense`, siguiendo el patrón de `coordinacion/`, `finanzas/` y `admin/`.

**Rationale**: El bundle del alumno no se descarga hasta que un usuario con rol ALUMNO navega, reduciendo el tamaño inicial del JS.

### D5: Reuso del layout y guards existentes
**Decisión**: Las rutas del alumno viven dentro del mismo `<AuthGuard>` y `<AppLayout>` que el resto del frontend. No se crea un layout separado.

**Rationale**: El shell (header, sidebar, breadcrumbs) es el mismo para todos los roles autenticados. El sidebar ya filtra items por permisos, así que ALUMNO solo ve sus rutas.

### D6: Sin backend nuevo para coloquios, avisos, programas, inbox
**Decisión**: Las vistas de coloquios, avisos, programas e inbox consumen directamente los endpoints existentes (`C-14`, `C-15`, `C-17`, `C-20`). No se crean nuevos endpoints específicos para alumno.

**Rationale**: Los endpoints existentes ya respetan permisos y scope de tenant. El ALUMNO tiene los permisos necesarios (`evaluacion:reservar`, `avisos:confirmar`). Crear duplicados agregaría mantenimiento sin beneficio.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **Performance del dashboard**: el endpoint consolidado puede ser lento si agrega muchos datos | Cache con TanStack Query (staleTime 30s). Si persiste, considerar caché Redis a nivel backend. |
| **Sidebar permission mismatch**: si los permisos del ALUMNO no matchean con los requeridos, no ve nada | Test manual con usuario ALUMNO antes de cerrar. Seguir el approach de permisos específicos (D2). |
| **Rutas solapadas**: las rutas `/alumno/*` podrían colisionar con rutas existentes | Usar prefijo `/alumno/` para todas las rutas. No hay rutas con ese prefijo hoy. |
| **Backend endpoint dashboard**: si se cambia la estructura de datos, frontend se rompe | Tipado fuerte TypeScript + contrato OpenAPI. El service del frontend define la interfaz. |
