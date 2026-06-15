## Context

C-07 ya entregó la entidad `Asignacion` (E5) con su ABM individual: `app/models/asignacion.py`, `repositories/asignacion_repository.py`, `services/asignacion_service.py`, `api/v1/routers/asignaciones.py` y la migración `007_create_usuario_asignacion.py`. La tabla tiene tenant, contexto académico nullable (`dictado_id`/`materia_id`/`carrera_id`/`cohorte_id`), `comisiones` (array), `responsable_id`, `desde`/`hasta` y soft-delete. `estado_vigencia` (Vigente|Vencida) es DERIVADO por fechas vía `estado_vigencia_for()` / `find_roles_vigentes()`, nunca columna.

C-08 construye las operaciones de **equipo** sobre ese modelo, sin tocar su schema. Un "equipo docente" es el conjunto de asignaciones que comparten la tripleta de contexto `(materia_id, carrera_id, cohorte_id)` dentro de un tenant.

> **Governance: ALTO.** Este change toca multi-tenancy, RBAC, identidad de sesión y auditoría sobre operaciones que modifican MUCHAS filas a la vez. Las decisiones de seguridad están marcadas **[SEC]** abajo y requieren revisión humana explícita en apply.

Constraintes vigentes (reglas duras): identidad y `tenant_id` siempre desde JWT (nunca de URL/body), repositories filtran por tenant por defecto, RBAC `modulo:accion` fail-closed, no lógica de negocio en routers, no DB directa en services, soft-delete siempre, Pydantic `extra='forbid'`, ≤500 LOC por archivo, una migración por cambio de schema (acá: ninguna), cobertura ≥90% en reglas de negocio.

## Goals / Non-Goals

**Goals:**
- Vista "mis-equipos" del docente (F4.2) acotada a sus asignaciones vigentes, derivada de la sesión.
- Listado filtrable de asignaciones del tenant para coordinación (F4.3).
- Asignación masiva (F4.4): N docentes → un contexto materia×carrera×cohorte×rol con vigencia común, transaccional.
- Clonado de equipo entre períodos (F4.5, RN-12): copiar asignaciones vigentes del origen al destino con fechas nuevas.
- Vigencia en bloque (F4.6): actualizar `desde`/`hasta` de todo un equipo de una vez.
- Export del equipo a archivo descargable (F4.7).
- Auditoría `ASIGNACION_MODIFICAR` en cada operación masiva que altera estado.

**Non-Goals:**
- NO se modifica el schema de `asignacion` ni se crea migración (la tabla de C-07 ya alcanza).
- NO se reescribe el ABM individual de C-07 (las operaciones de equipo se apoyan en él / en el repository).
- NO se construye UI (las páginas de Dashboard de equipos son un change frontend aparte).
- NO se resuelve el rol NEXO en profundidad (PA-25, pendiente) — "mis-equipos" lo incluye como lector de lo propio, sin semántica especial.
- NO autocompletado con índices full-text dedicados; RN-30 se satisface con búsqueda `ILIKE` sobre nombre/apellido acotada al tenant (mejora futura si hace falta).

## Decisions

### D1 — Nueva capability `equipos`, sin tabla nueva
Las operaciones de equipo son una capa de orquestación sobre `Asignacion`. Se modela como capability `equipos` separada de las operaciones CRUD individuales de C-07. **Alternativa descartada**: meter todo en el router/servicio de `asignaciones` de C-07 — rompería el límite de 500 LOC y mezclaría responsabilidades (CRUD de una fila vs. operaciones de bloque).

### D2 — Definición de "equipo" = tripleta `(materia_id, carrera_id, cohorte_id)`
Un equipo se identifica por su contexto académico, no por una entidad nueva. Clonado, vigencia en bloque y export operan sobre todas las asignaciones vivas que matchean esa tripleta en el tenant. **Alternativa descartada**: crear una entidad `Equipo` persistida — innecesaria; agrega estado redundante y otra migración. El equipo es una vista/agrupación derivada.

### D3 [SEC] — `equipos:asignar` fail-closed en operaciones de coordinación; "mis-equipos" por sesión
Todos los endpoints de F4.3–F4.7 (consulta del tenant, masiva, clonado, vigencia, export) declaran `Depends(require_permission(Perm.EQUIPOS_ASIGNAR))` → sin el permiso, 403. El endpoint "mis-equipos" (F4.2) NO usa ese guard: se autoriza por el solo hecho de tener sesión válida y devuelve EXCLUSIVAMENTE las asignaciones cuyo `usuario_id == current_user.id` y `tenant_id == current_user.tenant_id`. **Regla dura #8**: el `usuario_id` de "mis-equipos" sale de `current_user`, jamás de un query param. Reusa `Perm.EQUIPOS_ASIGNAR` ya existente — no se agrega permiso nuevo.

### D4 [SEC] — Multi-tenancy row-level en todas las consultas nuevas
Toda nueva query del `AsignacionRepository` recibe/usa `tenant_id` de la sesión y filtra por él + `deleted_at IS NULL`. El contexto del clonado/masiva (materia, carrera, cohorte, usuarios) se valida contra el tenant del caller; una referencia a otro tenant es indistinguible de "no existe" (404), igual que en C-07. La creación en lote graba `tenant_id` de la sesión en cada fila.

### D5 — Clonado (RN-12): sólo asignaciones VIGENTES, fechas del destino, no duplica
El clonado lee las asignaciones VIGENTES del equipo origen (`desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`), y por cada una crea una nueva en el destino preservando `usuario_id`, `rol`, `responsable_id`, `comisiones`, cambiando el contexto al destino (misma materia/carrera, nueva cohorte) y aplicando `desde`/`hasta` del nuevo período. **Idempotencia**: si en el destino ya existe una asignación viva equivalente (mismo `usuario_id` + `rol` + contexto), NO se duplica (se omite y se reporta como "ya existente"). **Alternativa descartada**: clonar también las vencidas — contradice FL-03 ("duplica las asignaciones vigentes") y arrastraría histórico muerto.

### D6 — Operaciones masivas: transaccionales, un solo commit, un solo audit
Asignación masiva, clonado y vigencia en bloque se ejecutan dentro de una sola transacción (el router hace un único `await db.commit()` al final, igual que el patrón de C-07). Si una fila falla la validación, se aborta toda la operación (sin commit parcial). Cada operación emite UN evento `ASIGNACION_MODIFICAR` con `filas_afectadas` = N y `detalle` describiendo el bloque (contexto, rol, vigencia, ids o conteo). **Alternativa descartada**: un audit por fila — inflaría el log y perdería la noción de "operación de bloque".

### D7 [SEC] — Auditoría `ASIGNACION_MODIFICAR` (reusa constante existente)
`AccionAuditoria.ASIGNACION_MODIFICAR` ya existe en `core/acciones_auditoria.py` (forward-declared). C-08 la usa para masiva, clonado y vigencia en bloque vía `AuditLogger.log(...)`, append-only, con `current_user` + `request` de la sesión. "mis-equipos", el listado del tenant y el export son de SOLO LECTURA → no auditan (no alteran estado).

### D8 — Export como CSV en streaming
F4.7 devuelve un `text/csv` descargable (`Content-Disposition: attachment`) con columnas: docente (nombre/identificador), rol, materia, carrera, cohorte, `desde`, `hasta`, estado_vigencia. El armado vive en `EquipoService` (no en el router). **Alternativa descartada**: XLSX — agrega dependencia (openpyxl) sin pedido explícito; CSV es portable y suficiente para F4.7.

### D9 — Capas: Router → EquipoService → AsignacionRepository → Asignacion
Nuevo `EquipoService` con la lógica de bloque (validación de contexto/usuarios, reglas RN-12/RN-30, armado del export, auditoría). Nuevos métodos en `AsignacionRepository`: `find_mis_equipos_vigentes`, `find_by_filtros` (listado tenant), `find_equipo` (por tripleta), `create_many`, `update_vigencia_equipo`, `buscar_docentes` (autocompletado RN-30). El router no contiene lógica; el service no toca la sesión SQL salvo vía repository.

## Risks / Trade-offs

- **[Riesgo] Clonado/masiva crean duplicados lógicos** → Mitigación: D5 deduplica por `(usuario_id, rol, materia_id, carrera_id, cohorte_id)` vivo; la masiva omite docentes ya asignados al mismo contexto+rol y los reporta.
- **[Riesgo] Operación de bloque parcialmente aplicada ante fallo** → Mitigación: D6, una sola transacción, abort total sin commit parcial.
- **[Riesgo SEC] Fuga cross-tenant en consultas masivas** → Mitigación: D4, todo filtra por `tenant_id` de la sesión; validación de contexto/usuarios contra el tenant (404 si ajeno). Tests dedicados de aislamiento.
- **[Riesgo SEC] "mis-equipos" expone asignaciones ajenas** → Mitigación: D3, filtro estricto por `current_user.id`; test que un docente A no ve las de B.
- **[Riesgo] Export grande en memoria** → Mitigación: CSV en streaming; el volumen por equipo (un curso) es acotado, no es un export global del tenant.
- **[Trade-off] RN-30 con `ILIKE` y no full-text** → aceptable al volumen de docentes por tenant; revisable si crece.

## Migration Plan

- **Sin migración de DB.** C-08 no altera schema; reusa la tabla `asignacion` de la migración `007`.
- Despliegue: agregar router `equipos` al app factory, sin cambios destructivos. Rollback = quitar el router; no hay datos nuevos que revertir (las asignaciones creadas por masiva/clonado son filas normales de `asignacion`, soft-deletables por el flujo de C-07).

## Open Questions

- **PA-25 (rol NEXO)**: "mis-equipos" trata a NEXO como lector de sus propias asignaciones; si NEXO tuviera una semántica de "equipo extendido" (ver equipos de otros), se ajustará en el change que cierre PA-25. No bloquea C-08.
- **Formato de export**: se asume CSV (D8). Si producto pide XLSX, es un cambio incremental aislado en `EquipoService`.
- **Dedup en clonado/masiva (D5)**: se asume "omitir y reportar" los ya existentes. Confirmar con producto si en cambio debe fallar la operación completa ante un duplicado.
