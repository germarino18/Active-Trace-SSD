## Context

El sidebar actual (`AppLayout.tsx` + `Sidebar.tsx`) usa una lista plana de `MenuItem[]` donde el filtrado de visibilidad se hace solo por `requiredPermissions`. Esto genera tres problemas concretos:

1. **Duplicados**: "Dashboard" aparece para todos + para alumno; "Avisos" y "Coloquios" aparecen para alumno y para roles docentes; sin separación visual ni lógica.
2. **Rutas incorrectas**: "Atrasados" y "Comunicación" apuntan a `/materias` en lugar de `/atrasados` y `/comunicacion`.
3. **NEXO sin ítems**: el rol tiene permisos en la KB (`atrasados:ver`, `encuentros:ver`, `tareas:ver` con scope carrera) pero ningún ítem propio en el sidebar.

El cambio es puramente frontend — no hay cambios de API ni de permisos backend.

## Goals / Non-Goals

**Goals:**
- Introducir el tipo `SidebarSection` (sección con label opcional + array de ítems) para reemplazar la lista plana.
- Reorganizar `defaultMenuItems` → `defaultSections` con agrupación por rol: ALUMNO, DOCENTE (TUTOR/PROFESOR), COORDINACIÓN, NEXO, FINANZAS, ADMIN.
- Corregir las rutas `/materias` erróneas en "Atrasados" y "Comunicación".
- Agregar ítems de NEXO con permisos propios (`nexo:atrasados:ver`, `nexo:encuentros:ver`, `nexo:tareas:ver`).
- Actualizar `Sidebar.tsx` para renderizar secciones con encabezado de sección (hidden cuando todos sus ítems están ocultos).
- Cubrir con tests: cada perfil de rol ve exactamente sus ítems y no los de otros roles.

**Non-Goals:**
- Cambiar el diseño visual del sidebar (colores, fuentes, responsive behavior — sin cambios).
- Implementar permisos NEXO en el backend (los tests los mockean).
- Agregar íconos nuevos distintos a los ya disponibles en Material Symbols.
- Implementar sub-menús o ítems anidados.

## Decisions

### D1 — `SidebarSection[]` en lugar de secciones hardcodeadas por permiso

**Decisión**: Agregar el tipo `SidebarSection = { label?: string; items: MenuItem[] }` en `shared/types` y pasar `sections: SidebarSection[]` al `Sidebar`.

**Alternativa descartada**: filtrar por prefijo de permiso en tiempo de render (`item.permissions.some(p => p.startsWith('estado-academico'))`). Produce acoplamiento entre lógica de presentación y nombres de permisos; es frágil ante renombrados.

**Rationale**: La sección es la unidad de agrupación correcta — el encabezado de sección se oculta automáticamente si todos sus ítems son invisibles. Es la misma primitiva que usa el DS Obsidian para nav groups.

### D2 — Permisos NEXO con prefijo `nexo:`

**Decisión**: Los ítems de NEXO usan `requiredPermissions: ['nexo:atrasados:ver']`, etc., en lugar de reutilizar `atrasados:ver`. Esto permite que en el futuro el backend emita un scope diferente para NEXO (solo-lectura por carrera) sin afectar a otros roles.

**Alternativa descartada**: reutilizar `atrasados:ver` y agregar lógica de rol en el sidebar. Viola el principio de que la identidad viene del JWT — el sidebar no debe inspeccionar roles, solo permisos.

### D3 — Secciones determinadas en `AppLayout`, no en `Sidebar`

**Decisión**: `AppLayout` construye `defaultSections`; `Sidebar` recibe `sections: SidebarSection[]` y solo renderiza. La lógica de qué sección existe es responsabilidad del layout.

**Rationale**: Mantiene `Sidebar` como componente tonto (solo visual); facilita testing del layout sin montar todo el árbol del sidebar.

### D4 — Sección vacía = oculta

**Decisión**: `Sidebar` filtra cada sección; si todos sus ítems resultan invisibles (permisos), la sección entera (encabezado + ítems) no se renderiza.

### D5 — ADMIN replica todas las funcionalidades de tutor/coordinador

**Decisión**: El rol ADMIN ve y accede a todas las vistas del sidebar que también ven TUTOR y COORDINADOR. No se crea un conjunto de vistas exclusivo y reducido para ADMIN.

**Rationale**: La KB establece que ADMIN tiene capacidades equivalentes a las de otros roles (importar calificaciones, ver atrasados, detectar entregas, gestionar encuentros, registrar guardias, etc.). Limitar sus vistas sería contradecir la matriz de capacidades definida en `knowledge-base/03_actores_y_roles.md §3.3`.

**Alternativa descartada**: Darle a ADMIN solo vistas de "gestión" (Estructura, Usuarios, Auditoría) y nada de las vistas operativas. Descartada porque dejaría a ADMIN sin acceso a funcionalidades que la KB le asigna explícitamente.

### D6 — Permisos role-agnostic (sin prefijo de rol en el string)

**Decisión**: Los permisos que múltiples roles comparten NO llevan prefijo de rol. Antes: `tutor:alumnos:ver`, `tutor:entregas:ver`, `tutor:guardias:gestionar`. Ahora: `alumnos:ver`, `entregas:ver`, `guardias:gestionar`.

**Rationale**: Un string como `tutor:entregas:ver` acopla el permiso a un rol específico, lo cual viola el principio de RBAC fino: los permisos describen *capacidades* (`modulo:accion`), no *quién eres*. Con strings role-agnostic, el backend puede emitir `entregas:ver` a TUTOR, PROFESOR y ADMIN por igual, y el sidebar funciona para todos sin cambios.

**Convención resultante**: Solo los permisos genuinamente exclusivos de un rol llevan prefijo: `nexo:atrasados:ver` se justifica porque NEXO tiene un scope diferente (carrera) que el resto — no es la misma capacidad.

**Impacto en backend**: El backend debe emitir `alumnos:ver`, `entregas:ver` y `guardias:gestionar` (sin prefijo `tutor:`) al asignar permisos a TUTOR, PROFESOR y ADMIN.

### D7 — Aprobación masiva sin ítem de sidebar propio

**Decisión**: "Aprobar comunicaciones masivas" (`comunicacion:aprobar`) no tiene un ítem de sidebar separado. El flujo de aprobación ocurre dentro de la vista `/comunicacion` ya existente.

**Rationale**: El ítem "Comunicación" en la sección Docente lleva al usuario a la vista completa donde tanto el envío como la aprobación son acciones contextuales. Agregar un segundo ítem crearía confusión de navegación sin valor adicional.

## Risks / Trade-offs

- **[Riesgo] Permisos NEXO no emitidos aún por el backend** → En producción los usuarios NEXO no verán sus ítems hasta que el backend emita `nexo:*` permisos. Mitigación: los tests mockean el JWT; en producción es un no-op (sección vacía se oculta).
- **[Riesgo] Rutas `/atrasados` y `/comunicacion` pueden no existir aún** → Corregir las rutas es correcto igual; si la ruta no existe el router mostrará 404 — es mejor que apuntar a `/materias`.
- **[Trade-off] Añadir `SidebarSection` al tipo compartido** → Añade superficie a `shared/types`, pero es un tipo simple (2 campos) que no introduce dependencias nuevas.
