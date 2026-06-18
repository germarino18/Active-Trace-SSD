## 1. Backend — Endpoint consolidado de dashboard

- [ ] 1.1 Crear `backend/app/api/v1/routers/alumno.py` con router `/api/alumno/dashboard`
- [ ] 1.2 Implementar endpoint `GET /api/alumno/dashboard` que agregue: materias del alumno con progreso, avisos no leídos count, comunicaciones no leídas count, próximos coloquios, próximas fechas académicas
- [ ] 1.3 Proteger endpoint con guard `estado-academico:ver`
- [ ] 1.4 Registrar el router en `backend/app/api/v1/router.py`
- [ ] 1.5 Tests del endpoint: datos correctos, 403 sin permiso, aislamiento multi-tenant

## 2. Frontend — Feature module y scaffolding

- [ ] 2.1 Crear estructura `frontend/src/features/alumno/` con `pages/`, `components/`, `hooks/`, `services/`, `types/`
- [ ] 2.2 Crear `services/alumno.service.ts` con funciones para consumir los endpoints (dashboard, estado académico, coloquios, avisos, programas, inbox, comunicaciones)
- [ ] 2.3 Crear `types/alumno.types.ts` con interfaces TypeScript para todas las entidades del alumno
- [ ] 2.4 Crear `hooks/useAlumnoDashboard.ts` hook para el dashboard consolidado con TanStack Query

## 3. Frontend — Layout, routing y sidebar

- [ ] 3.1 Agregar rutas del alumno en `App.tsx` bajo prefijo `/alumno/` con lazy-loading
- [ ] 3.2 Agregar items del sidebar en `AppLayout.tsx` para ALUMNO con permisos específicos (`estado-academico:ver`, `evaluacion:reservar`, `avisos:confirmar`)
- [ ] 3.3 Verificar que el Sidebar filtra correctamente items para rol ALUMNO

## 4. Frontend — Dashboard del alumno

- [ ] 4.1 Crear `pages/AlumnoDashboardPage.tsx` con cards de materia, progreso y alertas
- [ ] 4.2 Crear `components/MateriaCard.tsx` con barra de progreso y estado
- [ ] 4.3 Crear `components/AlertasPanel.tsx` con avisos no leídos, comunicaciones, coloquios próximos
- [ ] 4.4 Implementar empty state y error state
- [ ] 4.5 Tests del dashboard

## 5. Frontend — Estado académico

- [ ] 5.1 Crear `pages/MisMateriasPage.tsx` con listado de materias del alumno
- [ ] 5.2 Crear `pages/MateriaDetallePage.tsx` con calificaciones, actividades y estado
- [ ] 5.3 Tests de vistas de estado académico

## 6. Frontend — Reserva de coloquios

- [ ] 6.1 Crear `pages/MisColoquiosPage.tsx` con listado de convocatorias abiertas
- [ ] 6.2 Crear componente `components/ReservaTurnoModal.tsx` para seleccionar fecha y confirmar
- [ ] 6.3 Implementar flujo de reserva (seleccionar → confirmar → feedback)
- [ ] 6.4 Implementar cancelación de reserva propia
- [ ] 6.5 Tests de reserva/cancelación

## 7. Frontend — Avisos y acknowledgment

- [ ] 7.1 Crear `pages/MisAvisosPage.tsx` con tablón de avisos activos
- [ ] 7.2 Implementar botón "Confirmar lectura" para avisos con require_ack
- [ ] 7.3 Implementar filtro de avisos leídos/no leídos
- [ ] 7.4 Tests de avisos

## 8. Frontend — Programas y fechas académicas

- [ ] 8.1 Crear `pages/MisProgramasPage.tsx` con listado de programas por materia
- [ ] 8.2 Crear `pages/MisFechasPage.tsx` con calendario de fechas académicas
- [ ] 8.3 Tests de programas y fechas

## 9. Frontend — Inbox (bandeja de mensajes)

- [ ] 9.1 Crear `pages/AlumnoInboxPage.tsx` con listado de hilos
- [ ] 9.2 Crear `pages/AlumnoHiloPage.tsx` con detalle del hilo y formulario de respuesta
- [ ] 9.3 Tests de inbox

## 10. Frontend — Comunicaciones recibidas

- [ ] 10.1 Crear `pages/MisComunicacionesPage.tsx` con historial de comunicaciones
- [ ] 10.2 Crear `pages/ComunicacionDetallePage.tsx` con contenido completo
- [ ] 10.3 Tests de comunicaciones
