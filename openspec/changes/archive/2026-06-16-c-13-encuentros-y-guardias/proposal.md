## Why

El sistema necesita gestionar los encuentros sincrónicos (clases virtuales) y las guardias de atención a alumnos que cada equipo docente planifica durante el cuatrimestre. Actualmente no existe ningún mecanismo para registrar slots recurrentes, instancias concretas, ni guardias de tutores. Sin este módulo, docentes y coordinadores no pueden planificar ni auditar la actividad sincrónica del período, ni exportar contenido al aula virtual del LMS.

## What Changes

- **Nuevo modelo `SlotEncuentro`** — plantilla de encuentro recurrente con día de la semana, hora, cantidad de semanas y enlace de videoconferencia.
- **Nuevo modelo `InstanciaEncuentro`** — encuentro concreto, derivado de un slot o creado como único, con estado (Programado/Realizado/Cancelado), enlaces y comentario. Sigue la regla RN-13: al crear un slot recurrente, el sistema genera automáticamente todas las instancias.
- **Nuevo modelo `Guardia`** — registro de guardia de atención a alumnos, con día, horario, estado y comentarios.
- **Endpoint REST** `/api/v1/encuentros/*` con guard `encuentros:gestionar`.
- **Endpoint REST** `/api/v1/guardias/*` con guard `encuentros:gestionar`.
- **Generación de bloque HTML** con los encuentros programados, listo para publicar en el LMS (F6.4).
- **Exportación de guardias** a formato descargable (F6.6).
- **Migración Alembic** para tablas `slot_encuentro`, `instancia_encuentro`, `guardia`.

## Capabilities

### New Capabilities
- `encuentros-api`: REST API para gestión de encuentros — creación de slots recurrentes con generación automática de instancias (RN-13), creación de encuentros únicos, edición de instancias (estado, meet_url, video_url, comentario), generación de bloque HTML para LMS, y vista admin transversal de todos los encuentros del tenant.
- `guardias-api`: REST API para registro de guardias de atención a alumnos — registro por TUTOR, consulta global con filtros por COORDINADOR/ADMIN, y exportación del registro.

### Modified Capabilities
_Ninguna. Es el primer módulo de encuentros y guardias del sistema._

## Impact

- **Nuevos modelos**: `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` en `backend/app/models/`
- **Nuevos schemas Pydantic**: `backend/app/schemas/encuentros.py`, `backend/app/schemas/guardias.py`
- **Nuevos repositories**: `backend/app/repositories/encuentro_repository.py`, `backend/app/repositories/guardia_repository.py`
- **Nuevos services**: `backend/app/services/encuentros.py`, `backend/app/services/guardias.py`
- **Nuevos routers**: `backend/app/api/v1/routers/encuentros.py`, `backend/app/api/v1/routers/guardias.py`
- **Nueva migración**: tablas `slot_encuentro`, `instancia_encuentro`, `guardia`
- **Nuevos tests**: `backend/tests/test_encuentros/`, `backend/tests/test_guardias/`
- **Dependencias**: requiere `C-07` (usuarios-y-asignaciones) completado, pues encuentros y guardias se anclan a `Asignacion` (quién crea/cubre) y a `Materia`
