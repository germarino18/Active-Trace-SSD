## Why

Hoy un PROFESOR solo puede enviar un comunicado a alumnos atrasados **atado a una actividad específica** y **dentro de un único dictado** (los endpoints `POST /profesor/dictados/{id}/comunicado-atrasados` y `comunicado-atrasado-null` exigen `actividad_id` obligatorio). La vista consolidada cross-materia (`AtrasadosGeneralPage`, sobre `GET /profesor/atrasados`) no tiene ningún botón de comunicado, y no existe forma de avisarle a **un solo alumno** ni de mandar un único mensaje a **todos** los desaprobados/atrasados sin elegir una actividad. El profesor necesita poder recordar a sus alumnos atrasados de forma directa, individual o masiva, sin obligarse a seleccionar una actividad que muchas veces no aplica (p. ej. el alumno arrastra varias materias).

## What Changes

- Nuevo endpoint backend que permite enviar un comunicado a alumnos atrasados **con `actividad_id` opcional** ("obviar actividad") y a un **conjunto explícito de destinatarios** (uno o muchos), reutilizando el pipeline de comunicaciones aprobado (`enqueue_masivo` → aprobación). Reemplaza la rigidez per-actividad/per-dictado de los endpoints actuales sin removerlos.
- **Modo Individual**: el frontend agrega un botón por fila en el panel "Desaprobados/Atrasados" (`AtrasadosGeneralPage`) que abre el formulario de comunicado precargado con el `entrada_padron_id` de ESE alumno y sus materias atrasadas/desaprobadas listadas; envía solo a ese alumno.
- **Modo General**: un botón superior "Enviar a todos" que dispara el mismo mensaje a **todos** los desaprobados + atrasados de la vista consolidada.
- El formulario de comunicado hace `actividad_id` **opcional**; el mensaje puede emitirse sin atarse a una actividad.
- Nuevos modelos Pydantic request con `extra='forbid'`, gateados por `Perm.COMUNICACION_ENVIAR`, con scope de tenant y auditoría, agrupando destinatarios por materia para respetar el `materia_id`/variable `materia` por comunicación que exige `enqueue_masivo`.
- Frontend: nueva función de servicio + hook TanStack + tipos; formulario con actividad opcional reutilizable para ambos modos.
- NO se modifica el motor de aprobación ni la máquina de estados (Pend→Send→OK/Fail / Pend→Canc): se consume tal cual.

## Capabilities

### New Capabilities
- `comunicado-profesor-flexible`: capacidad backend de enviar comunicados a alumnos atrasados con `actividad_id` opcional y destinatarios explícitos (individual o masivo, cross-materia), reusando el pipeline aprobado de comunicaciones.

### Modified Capabilities
- `comunicaciones-api`: se añade el requirement del endpoint flexible de comunicado a atrasados (actividad opcional, destinatarios explícitos, agrupado por materia) sobre la API de comunicaciones existente.
- `atrasados-general-view`: la vista consolidada de atrasados del PROFESOR pasa a ofrecer comunicado por fila (individual) y comunicado a todos (general).
- `comunicacion-atrasados`: el flujo de comunicado a atrasados deja de requerir una actividad; se documenta el modo sin-actividad y los destinatarios individuales/masivos.

## Impact

- **Backend**:
  - `app/api/v1/routers/profesor.py` — nuevo endpoint POST (p. ej. `/profesor/comunicado-atrasados-flexible`), nuevos request models (`ComunicadoFlexibleRequest`, `ComunicadoDestinatarioItem`) con `extra='forbid'`, `require_permission(Perm.COMUNICACION_ENVIAR)`.
  - `app/services/profesor_service.py` — nuevo método `prepare_comunicado_flexible(...)`: valida tenant/dictados, resuelve emails desde entradas de padrón, agrupa por materia, llama `enqueue_masivo` por materia, audita.
  - Reusa `app/services/comunicaciones_service.py::enqueue_masivo` y `app/schemas/comunicaciones.py` (`EnvioMasivoRequest`/`EnvioMasivoItem`) sin cambios.
- **Frontend**:
  - `features/academico/pages/AtrasadosGeneralPage.tsx` — botón por fila + botón "Enviar a todos" + formulario (actividad opcional).
  - `features/profesor/services/profesor.service.ts` — `enviarComunicadoFlexible(...)`.
  - `features/profesor/hooks/useProfesor.ts` — `useMutationComunicadoFlexible`.
  - `features/profesor/types/index.ts` — `ComunicadoFlexibleData`, `ComunicadoDestinatario`.
- **Sin cambios de schema/DB**: no hay migración Alembic; se reutilizan tablas y la máquina de estados de comunicaciones.
- **Governance CRÍTICO** (comunicación saliente con aprobación): el endpoint NO puede saltear el gate de aprobación — siempre pasa por `enqueue_masivo`, que respeta `tenant.aprobacion_comunicaciones`.
