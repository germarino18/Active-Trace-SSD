## 1. Utility: tenant cookie helper

- [x] 1.1 Crear `frontend/src/shared/utils/tenantCookie.ts` con `setTenantCookie(id)`, `getTenantCookie(): string | null`, `clearTenantCookie()` usando `document.cookie` nativo con atributos `SameSite=Strict; Secure`
- [x] 1.2 Escribir tests unitarios para `tenantCookie.ts`: set escribe cookie, get la lee, get retorna null si ausente, clear la elimina

## 2. Auth: persistencia de sesión via cookie

- [x] 2.1 En `AuthContext.tsx`, al inicio del `useEffect` de mount, leer la cookie con `getTenantCookie()` y si existe: llamar `setTenantId()` del API client y poblar `tenantRef.current`
- [x] 2.2 En `AuthContext.tsx`, en la función `login`, agregar llamado a `setTenantCookie(tenant)` luego de `tenantRef.current = tenant`
- [x] 2.3 En `AuthContext.tsx`, en `clearSession`, agregar llamado a `clearTenantCookie()`
- [x] 2.4 Verificar que `verify2faCallback` también setea la cookie (el tenant ya está seteado por `login`, no hace falta setear de nuevo, pero confirmar que el flujo funciona end-to-end)
- [x] 2.5 Escribir test unitario: montar `AuthProvider` con cookie `js-trace-tenant=test` ya presente, mockear `authService.refreshToken` y `authService.getCurrentUser` — verificar que la sesión queda `authenticated` sin llamar `login`
- [x] 2.6 Escribir test unitario: montar `AuthProvider` sin cookie — verificar que el estado es `unauthenticated` sin llamar al endpoint de refresh
- [x] 2.7 Escribir test unitario: montar `AuthProvider` con cookie pero refresh falla (404) — verificar que el estado queda `unauthenticated` y la cookie es eliminada

## 3. Páginas: AtrasadosGeneralPage

- [x] 3.1 Crear `frontend/src/features/academico/pages/AtrasadosGeneralPage.tsx` — fetchea `useMaterias()` y para cada materia los atrasados via `useAtrasadosPorMateria(materiaId)` (hook existente o nuevo)
- [x] 3.2 Implementar tabla unificada con columnas Alumno, Materia, Actividades aprobadas, % Aprobación — con un `select` de filtro por materia encima
- [x] 3.3 Implementar estado vacío ("No hay alumnos atrasados en ninguna de tus materias") y estado de carga
- [x] 3.4 Escribir test: usuario con materias que tienen atrasados — verificar que la tabla renderiza los datos combinados
- [x] 3.5 Escribir test: usuario sin atrasados — verificar que se muestra el empty state

## 4. Páginas: ComunicacionGeneralPage

- [x] 4.1 Crear `frontend/src/features/academico/pages/ComunicacionGeneralPage.tsx` — fetchea `useMaterias()` y para cada materia el resumen de comunicaciones via `useComunicacionesPorMateria(materiaId)` (hook existente o nuevo)
- [x] 4.2 Renderizar una card o fila por materia con contadores (enviados / pendientes / fallidos / cancelados) y botón "Comunicar" que navega a `/materias/:id/comunicar`
- [x] 4.3 Implementar highlight de pendientes (color de advertencia) y estado vacío
- [x] 4.4 Escribir test: materia con comunicaciones pendientes — verificar que el badge/contador de pendientes se renderiza con clase de advertencia
- [x] 4.5 Escribir test: usuario sin comunicaciones — verificar el mensaje vacío y los CTAs por materia

## 5. Páginas: Stubs NEXO

- [x] 5.1 Crear `frontend/src/features/nexo/pages/NexoAtrasadosStubPage.tsx` con heading "Atrasados — NEXO" y mensaje "Esta vista está en desarrollo"
- [x] 5.2 Crear `frontend/src/features/nexo/pages/NexoEncuentrosStubPage.tsx` con heading "Encuentros — NEXO" y mensaje "Esta vista está en desarrollo"
- [x] 5.3 Crear `frontend/src/features/nexo/pages/NexoTareasStubPage.tsx` con heading "Tareas — NEXO" y mensaje "Esta vista está en desarrollo"
- [x] 5.4 Cada stub debe incluir un link "Volver al dashboard" (`/dashboard`)

## 6. Router: registrar rutas nuevas en App.tsx

- [x] 6.1 Importar `AtrasadosGeneralPage` y `ComunicacionGeneralPage` en `App.tsx`
- [x] 6.2 Importar `NexoAtrasadosStubPage`, `NexoEncuentrosStubPage`, `NexoTareasStubPage` en `App.tsx`
- [x] 6.3 Registrar ruta `{ path: '/atrasados', element: <AtrasadosGeneralPage /> }` dentro del `AuthGuard` — sin `requiredPermissions` adicional (el componente maneja su guard interno via `PermissionGuard` o redirige)
- [x] 6.4 Registrar ruta `{ path: '/comunicacion', element: <ComunicacionGeneralPage /> }` dentro del `AuthGuard`
- [x] 6.5 Registrar rutas NEXO `{ path: '/nexo/atrasados' }`, `{ path: '/nexo/encuentros' }`, `{ path: '/nexo/tareas' }` dentro de un `AuthGuard` con los permisos correspondientes (`nexo:atrasados:ver`, `nexo:encuentros:ver`, `nexo:tareas:ver`)
- [x] 6.6 Verificar que las 5 rutas nuevas ya no producen 404 navegando manualmente (dev server)

## 7. Verificación end-to-end

- [x] 7.1 Levantar el dev server frontend, hacer login, recargar la página — verificar que la sesión se mantiene sin re-login
- [x] 7.2 Navegar desde el sidebar a "Atrasados" → verificar que carga `AtrasadosGeneralPage` sin 404
- [x] 7.3 Navegar desde el sidebar a "Comunicación" → verificar que carga `ComunicacionGeneralPage` sin 404
- [x] 7.4 Logout → verificar que la cookie `js-trace-tenant` es eliminada
- [x] 7.5 Ejecutar suite de tests frontend (`npm run test`) → todos los tests nuevos en verde, ningún test existente roto
