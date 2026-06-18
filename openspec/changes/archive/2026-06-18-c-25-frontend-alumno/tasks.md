## 1. Backend — Endpoint consolidado de dashboard

- [x] 1.1 Crear `backend/app/api/v1/routers/alumno.py` con router `/api/alumno/dashboard`
- [x] 1.2 Implementar endpoint `GET /api/alumno/dashboard` que agregue: materias del alumno con progreso, avisos no leídos count, comunicaciones no leídas count, próximos coloquios, próximas fechas académicas
- [x] 1.3 Proteger endpoint con guard `estado-academico:ver`
- [x] 1.4 Registrar el router en `backend/app/api/v1/router.py`
- [x] 1.5 Tests del endpoint: datos correctos, 403 sin permiso, aislamiento multi-tenant

## 2. Frontend — Feature module y scaffolding

- [x] 2.1 Crear estructura `frontend/src/features/alumno/` con `pages/`, `components/`, `hooks/`, `services/`, `types/`
- [x] 2.2 Crear `services/alumno.service.ts` con funciones para consumir los endpoints (dashboard, estado académico, coloquios, avisos, programas, inbox, comunicaciones)
- [x] 2.3 Crear `types/alumno.types.ts` con interfaces TypeScript para todas las entidades del alumno
- [x] 2.4 Crear `hooks/useAlumnoDashboard.ts` hook para el dashboard consolidado con TanStack Query

## 3. Frontend — Layout, routing y sidebar

- [x] 3.1 Agregar rutas del alumno en `App.tsx` bajo prefijo `/alumno/` con lazy-loading
- [x] 3.2 Agregar items del sidebar en `AppLayout.tsx` para ALUMNO con permisos específicos (`estado-academico:ver`, `evaluacion:reservar`, `avisos:confirmar`)
- [x] 3.3 Verificar que el Sidebar filtra correctamente items para rol ALUMNO

## 4. Frontend — Dashboard del alumno

- [x] 4.1 Crear `pages/AlumnoDashboardPage.tsx` con cards de materia, progreso y alertas
- [x] 4.2 Crear `components/MateriaCard.tsx` con barra de progreso y estado
- [x] 4.3 Crear `components/AlertasPanel.tsx` con avisos no leídos, comunicaciones, coloquios próximos
- [x] 4.4 Implementar empty state y error state
- [x] 4.5 Tests del dashboard

## 5. Frontend — Estado académico

- [x] 5.1 Crear `pages/MisMateriasPage.tsx` con listado de materias del alumno
- [x] 5.2 Crear `pages/MateriaDetallePage.tsx` con calificaciones, actividades y estado
- [x] 5.3 Tests de vistas de estado académico

## 6. Frontend — Reserva de coloquios

- [x] 6.1 Crear `pages/MisColoquiosPage.tsx` con listado de convocatorias abiertas
- [x] 6.2 Crear componente `components/ReservaTurnoModal.tsx` para seleccionar fecha y confirmar
- [x] 6.3 Implementar flujo de reserva (seleccionar → confirmar → feedback)
- [x] 6.4 Implementar cancelación de reserva propia
- [x] 6.5 Tests de reserva/cancelación

## 7. Frontend — Avisos y acknowledgment

- [x] 7.1 Crear `pages/MisAvisosPage.tsx` con tablón de avisos activos
- [x] 7.2 Implementar botón "Confirmar lectura" para avisos con require_ack
- [x] 7.3 Implementar filtro de avisos leídos/no leídos
- [x] 7.4 Tests de avisos

## 8. Frontend — Programas y fechas académicas

- [x] 8.1 Crear `pages/MisProgramasPage.tsx` con listado de programas por materia
- [x] 8.2 Crear `pages/MisFechasPage.tsx` con calendario de fechas académicas
- [x] 8.3 Tests de programas y fechas

## 9. Frontend — Inbox (bandeja de mensajes)

- [x] 9.1 Crear `pages/AlumnoInboxPage.tsx` con listado de hilos
- [x] 9.2 Crear `pages/AlumnoHiloPage.tsx` con detalle del hilo y formulario de respuesta
- [x] 9.3 Tests de inbox

## 10. Frontend — Comunicaciones recibidas

- [x] 10.1 Crear `pages/MisComunicacionesPage.tsx` con historial de comunicaciones
- [x] 10.2 Crear `pages/ComunicacionDetallePage.tsx` con contenido completo
- [x] 10.3 Tests de comunicaciones
