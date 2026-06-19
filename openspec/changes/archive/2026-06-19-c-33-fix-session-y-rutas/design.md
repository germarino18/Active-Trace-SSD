## Context

El `AuthProvider` monta y llama `attemptRefresh()` para restaurar la sesión. El flujo actual necesita `tenantRef.current` (que apunta al ID del tenant) para incluir `X-Tenant-ID` en el header del refresh. Pero `tenantRef` es un React ref en memoria — se resetea a `''` en cada reload. Por eso `attemptRefresh` entra en `if (!tenantRef.current)` y llama `clearSession()` inmediatamente, forzando re-login.

El backend ya emite el refresh token en una cookie `httpOnly` al hacer login. El único dato faltante es el tenant ID, que el frontend nunca persiste.

En paralelo, el sidebar referencia rutas `/atrasados`, `/comunicacion`, `/nexo/*` que no existen en el router de React Router, produciendo 404 al navegar.

## Goals / Non-Goals

**Goals:**
- Persistir el tenant ID en una cookie JS al hacer login, para que `attemptRefresh` pueda ejecutarse tras un reload.
- Registrar en el router las rutas `/atrasados`, `/comunicacion` con páginas funcionales.
- Registrar rutas stub para `/nexo/atrasados`, `/nexo/encuentros`, `/nexo/tareas` que previenen el 404.
- Mantener el access token estrictamente en memoria (sin localStorage, sin cookie legible).

**Non-Goals:**
- Implementar las vistas completas del rol NEXO (eso es un change futuro).
- Cambiar el mecanismo de refresh token (sigue siendo httpOnly cookie gestionada por el backend).
- Añadir nueva lógica de permisos o roles.
- Cambiar la experiencia de las rutas por materia (`/materias/:id/atrasados`).

## Decisions

### D-1: Cookie JS para tenant ID (no localStorage)

**Decisión**: Usar `document.cookie` nativo con `SameSite=Strict; Secure` para guardar el tenant ID (`js-trace-tenant`). No usar `localStorage`.

**Rationale**: El usuario lo pidió explícitamente. Las cookies tienen ventajas sobre `localStorage`: se pueden scoping por dominio y path, y se pueden configurar con atributos de seguridad. La cookie es de sesión (sin `Max-Age`), por lo que expira al cerrar el browser, alineándose con el ciclo de vida del refresh token.

**Alternativa descartada**: `localStorage` — es accesible desde cualquier JS del origen (XSS), y el equipo prefiere cookies por política de seguridad.

**Implementación**: Helper `src/shared/utils/tenantCookie.ts` con `setTenantCookie(id)`, `getTenantCookie()`, `clearTenantCookie()`. Sin dependencia externa (`js-cookie`).

### D-2: Leer cookie en `AuthProvider.useEffect` antes de `attemptRefresh`

**Decisión**: En el `useEffect` de mount de `AuthProvider`, leer la cookie del tenant antes de llamar `attemptRefresh`. Si la cookie existe: poblar `tenantRef.current` + llamar `setTenantId()` del cliente API + intentar refresh. Si no existe: `clearSession()` inmediato (usuario nunca logueado).

**Rationale**: Mínimo cambio posible al flujo existente. No requiere reescribir la lógica de refresh.

### D-3: AtrasadosGeneralPage — agregación multi-materia

**Decisión**: La página `/atrasados` fetchea las materias del docente y para cada una obtiene los atrasados. Muestra una tabla unificada con columna "Materia". Ofrece filtro por materia.

**Rationale**: El sidebar apunta a `/atrasados` esperando una vista cross-materia. La alternativa (redirect a `/materias`) degrada la UX al no mostrar qué alumnos están atrasados de forma inmediata.

**Endpoint usado**: `GET /api/v1/materias/` (lista materias) + `GET /api/v1/calificaciones/{materiaId}/atrasados` por materia.

### D-4: ComunicacionGeneralPage — historial cross-materia

**Decisión**: La página `/comunicacion` lista las comunicaciones enviadas/pendientes agrupadas por materia, con acceso rápido al link hacia `/materias/:id/comunicar` por materia. No replica el flujo de envío; actúa como hub de estado.

**Rationale**: El envío real requiere contexto de materia (umbral, listado de alumnos). Duplicar ese flujo aquí sería complejidad innecesaria. Un hub de estado es suficiente para que la ruta no sea 404.

### D-5: Stubs NEXO sin rutas reales

**Decisión**: Tres páginas stub `NexoAtrasadosStubPage`, `NexoEncuentrosStubPage`, `NexoTareasStubPage` con mensaje "Esta vista está en desarrollo" y CTA para volver al dashboard.

**Rationale**: NEXO es un rol con páginas propias que requieren un change completo. Stubs previenen el 404 y comunican al usuario que la funcionalidad está pendiente, sin comprometer el timeline.

## Risks / Trade-offs

- **[Risk] Cookie SameSite=Strict bloquea flows de oauth/redirect externos** → Mitigación: no hay redirect externo en este sistema; el riesgo no aplica.
- **[Risk] Cookie visible desde JS (no httpOnly)** → Es intencional: el tenant no es un secreto (es el nombre de la institución). El secreto real (tokens) sigue httpOnly.
- **[Risk] AtrasadosGeneralPage genera N+1 requests** → Mitigación: las materias suelen ser pocas (≤20). Se puede optimizar con `Promise.all`. Un endpoint agregado sería ideal pero requiere cambio de backend; se pospone.
- **[Risk] ComunicacionGeneralPage puede volverse stale** → Mitigación: usa TanStack Query con `staleTime` corto (15s); el usuario puede revalidar manualmente.
