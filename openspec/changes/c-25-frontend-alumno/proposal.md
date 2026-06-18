## Why

El PRD define el **Portal del Alumno** como Fase 2 del producto (RF-47 a RF-50). El backend ya tiene toda la funcionalidad que el alumno necesita: estado académico (`C-10`), reserva de coloquios (`C-14`), avisos con acknowledgment (`C-15`), programas (`C-17`), mensajería interna (`C-20`), y el shell frontend con auth (`C-21`). Lo que falta es la capa de presentación para el rol **ALUMNO**, que hoy no tiene ninguna vista dedicada — ni siquiera puede loguearse y ver su propio estado. Este change cierra esa brecha: le da al estudiante un dashboard consolidado donde gestionar su vida académica sin depender del docente.

## What Changes

- **Dashboard del alumno**: vista consolidada con cards por materia, barra de progreso, indicadores de estado (al día / atrasado / sin actividad).
- **Vista "Mi estado académico"**: desglose de calificaciones por materia, actividades aprobadas/pendientes, estado general.
- **Reserva de coloquios**: listar convocatorias abiertas del alumno, reservar turno con cupo, cancelar reserva propia.
- **Tablón de avisos**: avisos dirigidos al alumno (scope global/materia/cohorte) con botón "Confirmar lectura" (acknowledgment).
- **Programas y fechas académicas**: listar programas de las materias que cursa + calendario de parciales/TP/coloquios.
- **Bandeja de mensajes internos**: inbox para mensajes docente ↔ alumno (reutiliza `C-20` backend).
- **Comunicaciones recibidas**: historial de comunicaciones del sistema dirigidas al alumno.
- **Login**: el alumno usa el mismo flujo de login que existe (email+password+2FA). El SSO con Moodle (RF-47) queda para una iteración futura.

## Capabilities

### New Capabilities
- `alumno-dashboard`: Dashboard consolidado del alumno con cards de materia, progreso y estado general.
- `alumno-estado-academico`: Vista detallada de calificaciones, actividades y estado por materia.
- `alumno-coloquios-reserva`: Listado de convocatorias abiertas + reserva/cancelación de turno.
- `alumno-avisos`: Tablón de avisos con acknowledgment.
- `alumno-programas`: Lista de programas + calendario de fechas académicas.
- `alumno-inbox`: Bandeja de mensajes internos del alumno.
- `alumno-comunicaciones`: Historial de comunicaciones recibidas.

### Modified Capabilities
<!-- No existing specs are modified — this is entirely new frontend -->

## Impact

- **Frontend**: nuevo feature `alumno/` con pages, components, hooks, services, types
- **Sidebar**: agregar rutas del alumno, visibles solo para rol ALUMNO (permiso `estado-academico:ver` y afines)
- **AuthGuard**: el login actual ya soporta cualquier rol — el alumno puede loguearse hoy, pero no ve nada. Solo ajustar visibilidad.
- **Backend**: no se esperan cambios mayores. Los endpoints de `C-10`, `C-11`, `C-14`, `C-15`, `C-17`, `C-20` ya están. Posiblemente se necesite un endpoint consolidado para el dashboard del alumno (ver diseño).
