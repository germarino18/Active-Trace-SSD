## Context

El rol **TUTOR** no puede operar el frontend actualmente por dos problemas: (1) el sidebar filtra usando permisos wildcard (`atrasados:*`) que no existen en la sesión del TUTOR (solo tiene `atrasados:ver`), y (2) faltan items de menú y vistas enteras necesarias para el rol ("Mis Alumnos", "Guardias", "Entregas sin corregir"). El backend ya implementa todos los endpoints necesarios y filtra por scope del tutor.

**Estado actual del frontend:**
- `hasAnyPermission()` en `AuthContext.tsx:110-113` usa `Array.includes()` para matching exacto — no soporta wildcards
- Sidebar (`AppLayout.tsx:26-58`) define `defaultMenuItems` con permisos planos como `atrasados:*`, `encuentros:*`
- Routing (`App.tsx`) tiene rutas existentes para atrasados y entregas bajo `/materias/:id/` (MateriaLayout), no como rutas independientes
- No existe página "Mis Alumnos" ni registro de guardias desde frontend

## Goals / Non-Goals

**Goals:**
- TUTOR puede ver items de navegación correctos en el sidebar
- TUTOR puede ver sus alumnos asignados por materia
- TUTOR puede ver atrasados de sus alumnos (scope propio)
- TUTOR puede ver entregas sin corregir (scope propio)
- TUTOR puede registrar guardias (propio)
- TUTOR puede confirmar avisos (ack inline)
- Todos los cambios son frontend-only

**Non-Goals:**
- No se modifica la matriz de permisos del backend
- No se crean nuevos endpoints de API
- No se modifica el comportamiento del backend
- No se cambia el diseño responsive ni el layout
- No se implementa autorización a nivel ruta (solo sidebar filtering)

## Decisions

### D1: Sidebar — permisos específicos en lugar de wildcard
| Alternativa | Veredicto |
|---|---|
| ✅ Cambiar `atrasados:*` → `atrasados:ver`, `encuentros:*` → `encuentros:gestionar` | **Elegido** — simple, directo, no rompe otros roles |
| ❌ Agregar lógica de wildcard en `hasAnyPermission` | Más complejo, riesgo de errores |

**Rationale**: Los permisos del backend ya son específicos (modulo:accion). El sidebar debe reflejar los mismos strings. Roles con `*` (COORDINADOR, ADMIN) siguen matcheando porque el backend les asigna TODOS los permisos específicos (`atrasados:ver`, `atrasados:exportar`, etc).

### D2: "Mis Alumnos" — ruta independiente (`/tutor/alumnos`)
| Alternativa | Veredicto |
|---|---|
| ✅ Ruta `/tutor/alumnos` con página dedicada en `features/tutor/` | **Elegido** — aislado, escalable, sin acoplar a MateriaLayout |
| ❌ Anidado bajo `/materias/:id/alumnos` | Confuso porque TUTOR no necesariamente selecciona una materia |

**Rationale**: El TUTOR necesita ver TODOS sus alumnos de TODAS sus materias en una sola vista. Una ruta independiente es más clara.

### D3: Guardias — vista dentro de Encuentros o página separada
| Alternativa | Veredicto |
|---|---|
| ✅ Modal/formulario accesible desde sidebar ("Guardias") que usa el endpoint `POST /api/v1/encuentros` con flag `tipo=guardia` | **Elegido** — reutiliza EncuentrosListPage con filtro, o página simple |
| ❌ Página separada completa | Sobrecarga innecesaria |

**Rationale**: Las guardias son encuentros con un tipo específico. El endpoint `POST /api/v1/encuentros` ya permite crearlas. Se crea un modal/formulario reutilizando los hooks existentes de `useEncuentros`.

### D4: Avisos — confirmación inline en tabla
Se agrega botón "Confirmar" en la fila de avisos para TUTOR que llama `POST /api/v1/avisos/:id/ack`. Se reutiliza la tabla existente de `AvisosListPage` o se crea un componente simple en `features/tutor/`.

### D5: Entregas sin corregir como ruta independiente
La ruta actual `EntregasSinCorregirPage` es hija de `/materias/:id/`. Para TUTOR necesitamos una versión que devuelva entregas de TODAS sus materias. Se crea página en `features/tutor/` que consume el mismo endpoint (backend ya filtra por tutor si no se pasa materia_id).

## Risks / Trade-offs

- **[Riesgo]** El endpoint de atrasados sin `materia_id` podría no filtrar por tutor → **Mitigación**: Verificar que el backend lo soporte; si no, ajustar query param
- **[Riesgo]** `EncuentrosListPage` usa `hasPermission('coordinacion:encuentros:crear')` para el botón crear — TUTOR no tiene ese permiso, pero puede registrar guardias → **Mitigación**: Evaluar si se necesita un permiso separado `guardias:registrar` o reutilizar `encuentros:gestionar`
- **[Trade-off]** No se agrega PermissionGuard a nivel ruta → el TUTOR podría navegar a URLs no permitidas (aunque sin sidebar visibles). Aceptable porque sería un 404/403 del backend
- **[Riesgo]** Tests existentes mockean `hasAnyPermission` con lógica de `includes()` — no se rompen porque los tests no mockean permisos wildcard
