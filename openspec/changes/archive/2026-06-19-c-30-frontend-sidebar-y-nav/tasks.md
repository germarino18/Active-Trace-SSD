## 1. Tipos y contrato

- [x] 1.1 Agregar tipo `SidebarSection = { label?: string; items: MenuItem[] }` a `frontend/src/shared/types/index.ts`
- [x] 1.2 Actualizar la firma de `Sidebar` para aceptar `sections: SidebarSection[]` en lugar de `menuItems: MenuItem[]`

## 2. Tests primero (TDD — RED)

- [x] 2.1 Crear `frontend/src/features/layout/components/__tests__/Sidebar.test.tsx` con test: ALUMNO ve ítems de alumno y no ve ítems docentes (debe fallar antes del cambio)
- [x] 2.2 Agregar test: NEXO ve sección NEXO y no ve sección ALUMNO (debe fallar antes del cambio)
- [x] 2.3 Agregar test: no hay duplicados de "Dashboard", "Avisos", "Coloquios" para ningún perfil
- [x] 2.4 Agregar test: "Atrasados" navega a `/atrasados` y "Comunicación" navega a `/comunicacion`
- [x] 2.5 Agregar test: sección con todos sus ítems sin permisos no se renderiza (label ausente del DOM)

## 3. Implementación de Sidebar con secciones (GREEN)

- [x] 3.1 Actualizar `Sidebar.tsx`: mapear `sections` → filtrar ítems por permisos → ocultar sección si resulta vacía → renderizar encabezado de sección si `label` presente
- [x] 3.2 Correr tests del paso 2 — deben pasar

## 4. Reorganizar `defaultSections` en AppLayout

- [x] 4.1 Reemplazar `defaultMenuItems: MenuItem[]` por `defaultSections: SidebarSection[]` en `AppLayout.tsx` con las siguientes secciones:
  - **ALUMNO**: Dashboard alumno, Mis Materias, Coloquios, Avisos, Programas, Calendario, Mensajes, Comunicaciones (permisos alumno)
  - **General** (sin label): Dashboard general, Mi Perfil (sin permiso requerido)
  - **Docente**: Calificaciones, Mis Alumnos, Entregas sin corregir, Guardias, Atrasados (`/atrasados`), Comunicación (`/comunicacion`), Encuentros, Coloquios docentes (permisos tutor/coordinador)
  - **NEXO**: Atrasados NEXO, Encuentros NEXO, Tareas NEXO (permisos `nexo:*:ver`)
  - **Coordinación**: Equipos Docentes, Avisos, Tareas, Programas, Fechas Académicas, Monitores (permisos coordinador)
  - **Finanzas**: Liquidaciones, Grilla Salarial, Facturas (permisos finanzas)
  - **Admin**: Estructura Académica, Usuarios, Auditoría, Métricas (permisos admin)
- [x] 4.2 Pasar `sections={defaultSections}` al `<Sidebar>` en el JSX de `AppLayout`

## 5. Triangulación de tests

- [x] 5.1 Agregar test: COORDINADOR ve sección Coordinación y Docente pero NO sección ALUMNO ni NEXO
- [x] 5.2 Agregar test: FINANZAS ve sección Finanzas y NO sección Docente ni ALUMNO ni NEXO
- [x] 5.3 Agregar test: usuario sin permisos (solo Mi Perfil) ve exactamente 1 ítem

## 6. Verificación

- [x] 6.1 Correr `pnpm test` en `frontend/` — toda la suite debe pasar
- [x] 6.2 Correr `pnpm tsc --noEmit` — sin errores de tipos (errores pre-existentes en archivos no modificados; ninguno en Sidebar/AppLayout/types)
