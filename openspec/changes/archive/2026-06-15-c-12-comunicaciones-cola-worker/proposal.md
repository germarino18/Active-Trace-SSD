## Why

El flujo central de PROFESOR (importar → analizar → comunicar) culmina con la comunicación a alumnos atrasados. Actualmente no existe un mecanismo para que los docentes envíen notificaciones masivas a los alumnos detectados como atrasados, ni un worker asíncrono que gestione el despacho con tracking de estados, preview obligatorio y aprobación configurable. Sin este módulo, el sistema detecta atrasos pero no puede cerrar el ciclo de acción.

## What Changes

- **Nuevo modelo `Comunicacion`** con destinatario cifrado, máquina de estados (Pendiente → Enviando → Enviado/Error/Cancelado), y agrupación por `lote_id`.
- **Worker asíncrono** en `backend/workers/` que consume la cola de comunicaciones y transiciona estados según resultado del envío.
- **Preview obligatorio** de asunto + cuerpo antes de encolar (RN-16).
- **Envío masivo con cola**: los mensajes ingresan como Pendiente y el worker los procesa asincrónicamente (RN-15).
- **Aprobación humana configurable por tenant**: si está activa, un usuario con permiso `comunicacion:aprobar` debe aprobar el lote antes del despacho (RN-17).
- **Plantillas con variables de sustitución** (nombre alumno, materia, etc.).
- **Endpoint REST** `/api/comunicaciones/*` con guard `comunicacion:enviar`.
- **Audit** con código `COMUNICACION_ENVIAR`.
- **Migración 010** para la tabla `comunicacion`.

## Capabilities

### New Capabilities
- `comunicaciones-api`: REST API para gestión de comunicaciones — preview, enqueue masivo, aprobación (lote/individual), cancelación y tracking de estados en tiempo real.
- `comunicaciones-worker`: Worker asíncrono de despacho que consume la cola, ejecuta el envío real y transiciona estados (Pendiente → Enviando → Enviado/Error/Cancelado).

### Modified Capabilities
_Ninguna. Es el primer módulo de comunicaciones del sistema._

## Impact

- **Nuevo modelo**: `Comunicacion` en `backend/app/models/comunicacion.py`
- **Nuevo schema Pydantic**: `backend/app/schemas/comunicaciones.py`
- **Nuevo repository**: `backend/app/repositories/comunicacion.py`
- **Nuevo service**: `backend/app/services/comunicaciones.py`
- **Nuevos routers**: `backend/app/api/routers/comunicaciones.py`
- **Nuevo worker**: `backend/workers/comunications_worker.py` (o nombre similar)
- **Nueva migración**: `010_create_comunicacion_table.py`
- **Nueva skill**: comunicación con alumnos, cola asíncrona, plantillas
- **Nuevos tests**: en `backend/tests/test_comunicaciones/`
- **Dependencias**: requiere `C-11` (análisis de atrasados) completado, pues el caso de uso principal es comunicar a alumnos atrasados
