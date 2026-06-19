## Why

El sidebar de `AppLayout.tsx` es una lista plana de ítems sin separación por rol: presenta duplicados ("Dashboard" aparece dos veces, "Avisos" dos veces, "Coloquios" dos veces), rutas incorrectas ("Atrasados" y "Comunicación" apuntan a `/materias` en lugar de sus rutas reales), y mezcla ítems de ALUMNO con ítems docentes/admin, lo que rompe la experiencia de cada perfil. El rol NEXO no tiene ningún ítem propio. Este change sanea y estructura la navegación antes de que se sigan añadiendo vistas.

## What Changes

- Refactorizar `defaultMenuItems` en `AppLayout.tsx`: pasar de lista plana a estructura de secciones por rol (`SidebarSection[]`) con agrupación semántica.
- Eliminar ítems duplicados: un solo "Dashboard" general, un solo "Avisos", un solo "Coloquios" por scope.
- Corregir rutas erróneas: "Atrasados" → `/atrasados`, "Comunicación" → `/comunicacion`.
- Agregar sección NEXO: ítems de solo lectura para atrasados, encuentros y tareas, filtrados por carrera vía permiso `nexo:*`.
- Garantizar separación ALUMNO / docentes: ítems de alumno solo visibles con permisos `estado-academico:ver` / `evaluacion:reservar`; no se solapan con ítems de tutor/coordinador.
- Actualizar `Sidebar.tsx` para renderizar secciones con encabezado opcional en lugar de una lista plana.
- Agregar tests de renderizado: cada perfil de rol ve exactamente los ítems esperados y ningún duplicado.

## Capabilities

### New Capabilities

- `sidebar-role-sections`: Sidebar estructurado en secciones por rol — ALUMNO, TUTOR/PROFESOR, COORDINADOR, NEXO, FINANZAS, ADMIN — con encabezado de sección y filtrado por permisos.

### Modified Capabilities

- `shell-layout`: La estructura del shell (`AppLayout` + `Sidebar`) cambia su contrato: `menuItems: MenuItem[]` pasa a `sections: SidebarSection[]`. Requiere actualización del spec existente.

## Impact

- **Archivos modificados**: `frontend/src/features/layout/components/AppLayout.tsx`, `frontend/src/features/layout/components/Sidebar.tsx`, `frontend/src/shared/types/index.ts` (nuevo tipo `SidebarSection`).
- **Tests nuevos**: `frontend/src/features/layout/components/__tests__/Sidebar.test.tsx`.
- **Sin cambios de API**: change puramente frontend.
- **Dependencias**: requiere que `useAuth` exponga `hasAnyPermission` (ya disponible) y los permisos de NEXO estén definidos en el backend RBAC (pueden mockearse en tests).
