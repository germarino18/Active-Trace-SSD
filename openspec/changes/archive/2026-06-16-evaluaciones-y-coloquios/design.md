## Context

El sistema ya implementa los módulos de calificaciones (C-10), atrasados (C-11), comunicaciones (C-12) y encuentros (C-13). Todos siguen Clean Architecture con FastAPI async, SQLAlchemy 2.0, multi-tenancy row-level, RBAC fino (`modulo:accion`), y audit append-only. Los modelos nuevos se anclan a `Dictado` vía `dictado_id` (ADR-006), mismo patrón usado en C-13 (encuentros).

La KB define el modelo E14 (Evaluacion, ReservaEvaluacion, ResultadoEvaluacion), las funcionalidades F7.1–F7.5 y el flujo FL-07. La matriz de permisos ya contempla `Reservar instancia de evaluación` para ALUMNO.

Este change implementa el módulo completo de coloquios siguiendo los mismos patrones que encuentros (C-13).

## Goals / Non-Goals

**Goals:**

- Implementar los modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con `dictado_id` como FK al contexto académico (ADR-006).
- ABM de convocatorias de coloquio (crear, editar, cerrar) con definición de días disponibles, cupos y ventana de inscripción.
- Importar padrón de alumnos habilitados para una convocatoria específica.
- Reserva de turno por ALUMNO con control de cupo disponible; cancelación de reserva.
- Panel de métricas (convocados, reservas activas, cupos libres, notas registradas).
- Registro académico consolidado de resultados de coloquios.
- Agenda de reservas activas para COORDINACIÓN.
- Migración Alembic con las 3 tablas.
- Tests (modelos, repositorio, servicio, router) siguiendo el patrón de C-13.

**Non-Goals:**

- Frontend (se implementa en C-23 frontend-coordinacion).
- Exportación de datos a CSV/Excel (se puede agregar después).
- Notificaciones automáticas al alumno al reservar/cancelar (fuera de alcance).
- Integración con Moodle para resultados de coloquios.
- Evaluaciones del tipo "parcial" o "TP" — este change cubre solo coloquios. Las fechas académicas pertenecen a C-17.

## Decisions

### D1 — Modelos anclados a `Dictado` vía `dictado_id`

**Decisión**: `Evaluacion` usa `dictado_id` (FK → Dictado) en lugar de `materia_id` + `cohorte_id` como sugiere la KB E14.

**Razón**: ADR-006 establece que `Dictado` es la entidad raíz del contexto académico. Todos los changes downstream (C-07 en adelante) usan `dictado_id`. C-13 (encuentros) ya lo implementa así. Mantener consistencia.

**Alternativa considerada**: Usar `materia_id + cohorte_id` como indica la KB original. Se descarta porque rompe la convención establecida en C-08, C-10 y C-13, y dificultaría consultas que necesiten cruzar por dictado.

### D2 — Cupo controlado en aplicación, no con constraint DB

**Decisión**: El control de cupo disponible se hace en el Service (contar reservas Activas y comparar con el cupo definido), no con una constraint CHECK en la tabla.

**Razón**: El cupo es un atributo de la convocatoria (`Evaluacion`), no de la reserva. Cambiar el cupo no debería requerir migración. Una constraint DB no puede validar contra el cupo de otra fila. Se usa transacción serializable o bloqueo optimista (SELECT ... FOR UPDATE) en la reserva para evitar race conditions.

**Alternativa considerada**: CHECK trigger en DB. Se descarta porque el cupo no está en la misma tabla y sería complejo de mantener.

### D3 — Un schema para Evaluacion (convocatoria) con días y cupos

**Decisión**: `Evaluacion` almacena `dias_disponibles` (entero: días hábiles de inscripción), y `cupo_maximo` como entero. No se modelan franjas horarias ni turnos individuales — el ALUMNO reserva un día específico dentro de la ventana.

**Razón**: La KB (E14) define `dias_disponibles` como entero y FL-07 habla de "días disponibles y cupos por día". Simplificamos a un cupo global por convocatoria por ahora; si se necesita cupo por día, se agrega después como mejora.

### D4 — Permisos independientes para gestión, reserva y consulta

**Decisión**: Se crean 3 permisos:
- `coloquios:gestionar` — COORDINADOR, ADMIN (ABM convocatorias, importar alumnos, registrar resultados)
- `coloquios:reservar` — ALUMNO (reservar/cancelar turno)
- `coloquios:ver` — COORDINADOR, ADMIN, PROFESOR `(propio)` (ver métricas, agenda, registro académico)

**Razón**: La matriz de roles (KB 03 §3.3) asigna `Reservar instancia de evaluación` solo a ALUMNO, y las funcionalidades administrativas a COORDINADOR/ADMIN. El permiso `(propio)` para PROFESOR permite ver solo los coloquios de sus dictados.

### D5 — Auditoría con código estandarizado

**Decisión**: Se registran acciones con códigos `COLOQUIO_CREAR`, `COLOQUIO_IMPORTAR_ALUMNOS`, `COLOQUIO_RESERVAR`, `COLOQUIO_CANCELAR_RESERVA`, `COLOQUIO_REGISTRAR_RESULTADO`. Mismo patrón que `ENCUENTRO_CREAR` en C-13.

**Razón**: Consistencia con los códigos de auditoría existentes. Cada acción significativa queda trazada.

### D6 — Sin soft delete en tablas de coloquios

**Decisión**: `Evaluacion`, `ReservaEvaluacion` y `ResultadoEvaluacion` NO usan soft delete. Una convocatoria se "cierra" (nuevo estado), no se borra. Una reserva cancelada queda con estado Cancelada. Los resultados son inmutables una vez registrados.

**Razón**: Mismo criterio que C-13 con `InstanciaEncuentro`. Las cancelaciones y cierres se modelan como cambios de estado, no como borrado lógico.

## Risks / Trade-offs

- **[Riesgo] Race condition en reserva de turno**: dos ALUMNOS pueden reservar el último cupo simultáneamente.
  → **Mitigación**: usar `SELECT ... FOR UPDATE` dentro de la transacción al verificar cupo disponible, o manejar la excepción de unicidad si se implementa `(evaluacion_id, alumno_id)` unique.

- **[Trade-off] Cupo global vs por día**: se implementa cupo global por convocatoria. Si el negocio requiere cupo por día, habrá que refactorizar a una tabla intermedia de `FranjaHoraria`.

- **[Riesgo] Importación duplicada de alumnos**: un alumno puede importarse dos veces a la misma convocatoria.
  → **Mitigación**: constraint unique `(evaluacion_id, alumno_id)` en una tabla de `AlumnoConvocado` (si se necesita), o upsert (INSERT ON CONFLICT DO NOTHING). Se define en spec.

- **[Trade-off] Sin soft delete**: si en el futuro se necesita recuperar una convocatoria cerrada o una reserva cancelada, no hay borrado físico del que recuperarse — solo cambio de estado. Aceptable porque el estado cumple ese rol.
