## Why

Los coloquios (evaluaciones orales) son parte fundamental del calendario académico: los PROFESORES necesitan convocar alumnos, definir cupos y días disponibles; los ALUMNOS necesitan reservar turno; y la COORDINACIÓN necesita visibilidad global del estado de todas las convocatorias, reservas y resultados. Hoy no existe ningún registro sistematizado de este flujo — se maneja informalmente. Este change implementa el módulo completo de evaluaciones y coloquios, desde la convocatoria hasta el registro de resultados.

## What Changes

- Nuevos modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con anclaje a `Dictado` (ADR-006).
- ABM de convocatorias de coloquio con definición de días disponibles y cupos.
- Importación de padrón de alumnos habilitados para una convocatoria específica.
- Reserva de turno por ALUMNO con control de cupo (estado Activa/Cancelada).
- Panel de métricas de coloquios (convocados, reservas activas, cupos libres, notas registradas).
- Registro académico consolidado de resultados de coloquios.
- Agenda consolidada de reservas activas para COORDINACIÓN.
- Permisos finos: `coloquios:gestionar` (COORDINADOR/ADMIN), `coloquios:reservar` (ALUMNO), `coloquios:ver` (consulta).
- Auditoría con código `COLOQUIO_*` para acciones significativas.
- Migración Alembic con tablas `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`.

## Capabilities

### New Capabilities

- `coloquios-gestion`: Gestión completa de convocatorias de coloquio (crear, editar, cerrar; importar padrón de alumnos; panel de métricas; listado con indicadores).
- `coloquios-reserva`: Reserva de turno por ALUMNO con control de cupo, cancelación, y agenda consolidada para COORDINACIÓN.
- `coloquios-resultados`: Registro de resultados de coloquios (notas finales) y consulta del registro académico consolidado.

### Modified Capabilities

Ninguna. Módulo nuevo, sin cambios a specs existentes.

## Impact

- Nuevas tablas: `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion` — migración Alembic.
- Nuevos endpoints bajo `/api/v1/coloquios/` con guards `coloquios:*`.
- Nuevos permisos a seedear: `coloquios:gestionar`, `coloquios:reservar`, `coloquios:ver`.
- Nuevos códigos de auditoría: `COLOQUIO_CREAR`, `COLOQUIO_IMPORTAR_ALUMNOS`, `COLOQUIO_RESERVAR`, `COLOQUIO_CANCELAR_RESERVA`, `COLOQUIO_REGISTRAR_RESULTADO`.
- Dependencia externa: ninguna — todo sobre PostgreSQL + FastAPI existente.
