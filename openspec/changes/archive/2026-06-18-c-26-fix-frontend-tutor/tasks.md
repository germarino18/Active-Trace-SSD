## 1. Sidebar — Corregir permisos wildcard

- [x] 1.1 Cambiar `atrasados:*` → `atrasados:ver` en `defaultMenuItems` (`AppLayout.tsx:29`)
- [x] 1.2 Cambiar `encuentros:*` → `encuentros:gestionar` en `defaultMenuItems` (`AppLayout.tsx:44`)
- [x] 1.3 Verificar que `comunicacion:*` también se ajuste a `comunicacion:ver` para TUTOR (`AppLayout.tsx:30`)
- [x] 1.4 Verificar que COORDINADOR y ADMIN sigan viendo todos los items (tienen permisos específicos asignados)

## 2. Sidebar — Nuevos items para TUTOR

- [x] 2.1 Agregar item "Mis Alumnos" (`path: '/tutor/alumnos', icon: 'group'`) con permiso `alumnos:ver`
- [x] 2.2 Agregar item "Entregas sin corregir" (`path: '/entregas-sin-corregir', icon: 'assignment_late'`)
- [x] 2.3 Agregar item "Guardias" (`path: '/guardias', icon: 'shield'`)

## 3. Vista "Mis Alumnos" (`/tutor/alumnos`)

- [x] 3.1 Crear estructura `features/tutor/` con `pages/`, `hooks/`, `services/`, `components/`, `types/`
- [x] 3.2 Crear `TutorAlumnosPage.tsx` con tabla de alumnos (nombre, email, materia, comisión)
- [x] 3.3 Crear hook `useTutorAlumnos.ts` que consuma `GET /api/v1/tutor/alumnos`
- [x] 3.4 Crear `tutor.service.ts` con función `getTutorAlumnos()`
- [x] 3.5 Agregar ruta `/tutor/alumnos` en `App.tsx`
- [x] 3.6 Manejar EmptyState cuando no hay alumnos asignados
- [x] 3.7 Cargado lazy con `lazy()`

## 4. Guardias (registro desde frontend)

- [x] 4.1 Crear `GuardiasListPage.tsx` con listado histórico (`GET /api/v1/encuentros?tipo=guardia`)
- [x] 4.2 Crear hook `useGuardias.ts` y service `guardia.service.ts`
- [x] 4.3 Crear formulario/modal de registro de guardia (`POST /api/v1/encuentros` con `tipo=guardia`)
- [x] 4.4 Agregar ruta `/guardias` en `App.tsx`
- [x] 4.5 Cargado lazy con `lazy()`

## 5. Entregas sin corregir (scope TUTOR)

- [x] 5.1 Crear `TutorEntregasSinCorregirPage.tsx` — versión simplificada que no requiere materia_id
- [x] 5.2 Crear hook `useTutorEntregas.ts` (o reutilizar `useEntregas` sin materia_id)
- [x] 5.3 Agregar ruta `/entregas-sin-corregir` en `App.tsx`
- [x] 5.4 Cargado lazy con `lazy()`

## 6. Confirmación de avisos para TUTOR

- [x] 6.1 Verificar que el botón de ack existe en la tabla de avisos para TUTOR
- [x] 6.2 Si no existe, agregar columna de acción con botón "Confirmar" que llame `POST /api/v1/avisos/:id/ack`
- [x] 6.3 Deshabilitar botón después de confirmar y mostrar badge "Confirmado"
- [x] 6.4 Manejar errores de confirmación (aviso ya acked, red, etc.)

## 7. Tests

- [x] 7.1 Escribir tests para tutor-sidebar (items visibles por rol)
- [x] 7.2 Escribir tests para TutorAlumnosPage (fetch, empty state, render)
- [x] 7.3 Escribir tests para GuardiasListPage (listado, registro)
- [x] 7.4 Escribir tests para confirmación de avisos
- [x] 7.5 Verificar que tests existentes no se rompen (especialmente Sidebar y AuthContext)
