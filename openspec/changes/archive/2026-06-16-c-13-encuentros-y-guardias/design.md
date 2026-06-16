## Context

El módulo de encuentros y guardias permite planificar, registrar y auditar la actividad sincrónica de cada equipo docente durante el cuatrimestre. Depende de C-07 (usuarios-y-asignaciones), que ya provee el modelo `Asignacion` y `Dictado` como contexto académico. El flujo principal (FL-06) cubre: creación de series recurrentes con generación automática de instancias, registro de encuentros realizados con grabación, supervisión por coordinación y exportación de contenido HTML para el LMS.

El sistema opera sobre PostgreSQL con SQLAlchemy 2.0 async y FastAPI. Los modelos existentes en `backend/app/models/` usan los mixins `BaseMixin`, `TenantMixin`, `SoftDeleteMixin`, `AuditMixin` y siguen el patrón de `dictado_id` como FK al contexto académico (ADR-006).

## Goals / Non-Goals

**Goals:**

- Modelar la entidad `SlotEncuentro` como plantilla de encuentro recurrente con día de la semana, hora, fecha de inicio y cantidad de semanas (cant_semanas = 0 indica fecha única)
- Modelar la entidad `InstanciaEncuentro` como encuentro concreto, derivada de un slot o independiente, con estado (Programado/Realizado/Cancelado), enlaces y comentario
- Al crear un slot recurrente, generar automáticamente N instancias (RN-13)
- Modelar la entidad `Guardia` como registro de guardia de atención a alumnos, con día, horario, estado y comentarios
- Exponer API REST `/api/v1/encuentros/*` con guard `encuentros:gestionar`
- Exponer API REST `/api/v1/guardias/*` con guard `encuentros:gestionar`
- Generar bloque HTML con los encuentros programados para publicar en el LMS (F6.4)
- Proveer exportación de guardias a formato descargable (F6.6)
- Anclar los modelos a `dictado_id` siguiendo ADR-006 (forward note de KB §E10/E11)
- Auditar las mutaciones con código `ENCUENTRO_CREAR` / `ENCUENTRO_EDITAR` / `GUARDIA_REGISTRAR`

**Non-Goals:**

- **No** incluir notificaciones push ni recordatorios automáticos de encuentros
- **No** integrar con calendarios externos (Google Calendar, Outlook)
- **No** implementar videoconferencia embebida — solo almacenar el enlace (meet_url)
- **No** modificar el modelo de Asignacion existente
- **No** incluir frontend — solo backend API

## Decisions

### D1: Slot → Instancias con generación upfront (no lazy)

**Decisión**: Al crear un `SlotEncuentro` con `cant_semanas > 0`, el sistema genera todas las `InstanciaEncuentro` en el mismo momento (upfront). Cada instancia queda con estado `Programado` y fechas calculadas como `fecha_inicio + (semana_i * 7)`.

**Rationale**: La cantidad de instancias por slot es acotada (típicamente 12-16 semanas por cuatrimestre). La generación upfront permite consultar y editar instancias individuales sin lógica condicional en los queries de lectura. Simplifica el modelo: no hay necesidad de calcular "instancias virtuales" en cada GET.

**Alternativa considerada**: Generación lazy (calcular instancias en el GET) — descartada porque complejiza las consultas (hay que calcular rangos de fechas en cada request) e impide editar instancias individuales de forma persistente.

### D2: `dictado_id` como FK al contexto académico (ADR-006)

**Decisión**: `SlotEncuentro`, `InstanciaEncuentro` y `Guardia` usan `dictado_id` (FK → Dictado) como referencia al contexto académico, en lugar de los campos sueltos `materia_id`/`carrera_id`/`cohorte_id`. Sigue el patrón de `Asignacion` y `VersionPadron` (C-07+). No se duplican los campos individuales.

**Rationale**: ADR-006 define a `Dictado` como la entidad raíz del contexto académico. Usar `dictado_id` simplifica el modelo (3 FKs → 1 FK) y garantiza consistencia referencial. El contexto completo (materia, carrera, cohorte) se resuelve por JOIN a través de `Dictado`.

**Alternativa considerada**: Mantener `materia_id`/`carrera_id`/`cohorte_id` como campos directos — descartado porque va contra ADR-006 y el patrón ya usado en C-07+.

### D3: SlotEncuentro con `asignacion_id` OWNER nullable

**Decisión**: `SlotEncuentro` tiene `asignacion_id` nullable FK → Asignacion, que identifica al usuario que creó el slot (quién da la clase). Es nullable porque un COORDINADOR puede crear slots que luego serán cubiertos por otro docente. `InstanciaEncuentro` hereda el `asignacion_id` del slot, pero puede modificarse individualmente.

**Rationale**: Flexible para los casos de uso reales: el PROFESOR crea su propio slot, o el COORDINADOR crea slots y los asigna. La herencia del asignacion_id desde el slot permite tracking por docente sin duplicar lógica.

### D4: Guardia con `asignacion_id` FK no nullable

**Decisión**: `Guardia` requiere `asignacion_id` (FK → Asignacion, no nullable) porque siempre identifica quién cubre la guardia (RN del negocio: un TUTOR registra su propia guardia).

**Rationale**: A diferencia del slot (que puede ser creado por un coordinador para otro docente), la guardia siempre es registrada por quien la cubre.

### D5: Generación de HTML con string.Template

**Decisión**: El bloque HTML para el LMS se genera con `string.Template` de la stdlib, usando una plantilla fija con los encuentros del dictado ordenados por fecha.

**Rationale**: Es parte de la stdlib, no requiere dependencias externas, y la salida es un fragmento HTML simple (tabla de encuentros). La lógica es: consultar instancias activas, ordenar por fecha, aplicar plantilla.

### D6: Exportación de guardias como streaming CSV

**Decisión**: La exportación de guardias usa StreamingResponse con CSV, siguiendo el mismo patrón de `equipos/export` (C-08).

**Rationale**: Consistente con el código existente y eficiente para volúmenes moderados de datos.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **R1**: Generación upfront puede crear muchas instancias si cant_semanas es muy grande | Limitar cant_semanas a un máximo razonable (52 semanas = 1 año). Validación en schema Pydantic. |
| **R2**: InstanciaEncuentro con estado y slot_id nullable puede tener datos inconsistentes (ej: instancia sin slot pero sin fecha) | Validación en service: si slot_id es NULL, fecha y hora son obligatorios; si slot_id no es NULL, se heredan del slot. |
| **R3**: Bloque HTML generado puede no ser compatible con todos los LMS | El bloque es HTML semántico simple (`<table>` con clases básicas). Si se requiere personalización por LMS, se puede agregar un parámetro de formato más adelante. |
| **R4**: dictado_id como única FK obliga a JOIN para obtener materia/carrera/cohorte | Carga aceptable: Dictado tiene índices por tenant, y la resolución del nombre de materia se hace en el service (no en el router). |
