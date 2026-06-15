## Why

C-07 entregó el ABM individual de `Asignacion` (un vínculo a la vez), pero el setup de un cuatrimestre (FL-03) implica mover decenas de asignaciones de golpe: clonar el equipo del período anterior, asignar varios docentes a la vez y reajustar vigencias en bloque. Hacerlo asignación por asignación es inviable y propenso a error. C-08 introduce las operaciones de equipo (vista propia del docente + operaciones masivas del coordinador) sobre el modelo `Asignacion` ya existente, sin cambiar su schema.

## What Changes

- **Vista "mis-equipos" del docente** (F4.2): endpoint que devuelve las asignaciones VIGENTES del usuario autenticado (rol, materia, carrera, cohorte, comisiones, vigencia, estado), derivadas de su sesión JWT — nunca de un parámetro. Filtros por estado, materia, rol, carrera, cohorte.
- **Gestión/consulta de asignaciones del tenant** (F4.3): listado filtrable de todas las asignaciones vivas del tenant (materia, carrera, cohorte, usuario, rol, responsable). Se apoya en el ABM individual ya existente de C-07.
- **Asignación masiva** (F4.4, RN-30): asignar un bloque de N docentes a una combinación materia × carrera × cohorte × rol con una vigencia común, en una sola operación transaccional. Búsqueda de docentes con autocompletado server-side.
- **Clonar equipo entre períodos** (F4.5, RN-12): duplicar todas las asignaciones VIGENTES de un equipo origen (materia × carrera × cohorte) hacia un destino (misma materia × carrera × nueva cohorte), aplicando las fechas del nuevo período.
- **Modificar vigencia general del equipo** (F4.6): actualizar `desde`/`hasta` de todas las asignaciones de un equipo en una sola operación.
- **Exportar equipo a archivo** (F4.7): generar un archivo descargable (CSV) con el detalle de las asignaciones del equipo (docente, rol, materia, carrera, cohorte, vigencia, estado).
- Nuevos endpoints bajo `/api/equipos/*`, todos protegidos por el guard `equipos:asignar` (COORDINADOR, ADMIN). La vista "mis-equipos" se autoriza por sesión (cualquier docente ve lo propio), no requiere `equipos:asignar`.
- Toda operación masiva que altere estado genera auditoría (`ASIGNACION_MODIFICAR`), append-only, con detalle del bloque afectado.

## Capabilities

### New Capabilities
- `equipos`: operaciones de equipo docente sobre `Asignacion` — vista "mis-equipos" del docente, consulta filtrada del tenant, asignación masiva, clonado entre períodos, modificación de vigencia en bloque y export a archivo. Cubre el guard `equipos:asignar`, el alcance por sesión de la vista propia, y la auditoría `ASIGNACION_MODIFICAR` de las operaciones masivas.

### Modified Capabilities
<!-- C-07 no creó una capability `asignaciones` con requirements de spec; su ABM individual vive sólo en código. C-08 no modifica requirements de spec existentes — sólo agrega la nueva capability `equipos`. -->

## Impact

- **Nuevos archivos backend**:
  - `app/schemas/equipo.py` (DTOs: filtros mis-equipos, asignación masiva, clonado, vigencia en bloque, item de export).
  - `app/services/equipo_service.py` (lógica masiva: clonado RN-12, asignación en bloque, vigencia en bloque, armado del export).
  - `app/api/v1/routers/equipos.py` (router `/api/equipos/*`).
  - Métodos nuevos en `app/repositories/asignacion_repository.py` (consultas por equipo, mis-equipos vigentes, listado filtrado del tenant, creación en lote, update de vigencia en bloque).
- **Sin migración Alembic**: C-08 NO toca el schema de `asignacion` (la tabla de C-07, migración `007`, ya tiene todos los campos necesarios: contexto académico, `comisiones`, `desde`/`hasta`, soft-delete, tenant).
- **Reusa sin agregar**: `Perm.EQUIPOS_ASIGNAR` (ya en `core/permissions.py`) y `AccionAuditoria.ASIGNACION_MODIFICAR` (ya en `core/acciones_auditoria.py`).
- **Seguridad (governance ALTO)**: multi-tenancy row-level en cada consulta nueva, fail-closed en `equipos:asignar`, identidad de "mis-equipos" sólo desde JWT, soft-delete preservado y auditoría obligatoria de toda operación masiva.
- **Frontend**: habilita las páginas de equipos del Dashboard (fuera del alcance de C-08, que es backend).
