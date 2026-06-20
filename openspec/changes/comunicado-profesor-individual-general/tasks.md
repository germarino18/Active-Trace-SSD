## 1. Backend — schemas & request models (Strict TDD)

- [x] 1.1 RED: write a unit test asserting `ComunicadoDestinatarioItem` (`extra='forbid'`) requires `entrada_padron_id: UUID` + `dictado_id: UUID` and rejects unknown fields
- [x] 1.2 RED: write a unit test asserting `ComunicadoFlexibleRequest` (`extra='forbid'`) accepts `actividad_id: UUID | None`, requires `asunto_template`/`cuerpo_template` (min_length 1) and `destinatarios` (min_length 1), and rejects unknown fields
- [x] 1.3 GREEN: add `ComunicadoDestinatarioItem` and `ComunicadoFlexibleRequest` models in `app/api/v1/routers/profesor.py` (or a profesor schema module), `extra='forbid'`
- [x] 1.4 TRIANGULATE: add cases for `actividad_id=null` accepted and empty `destinatarios` rejected; REFACTOR

## 2. Backend — service `prepare_comunicado_flexible` (Strict TDD, real DB)

- [x] 2.1 SAFETY NET: run existing `profesor_service` / comunicaciones integration tests; capture baseline (must be green) before touching the service
- [x] 2.2 RED: integration test (real/ephemeral DB, NO DB mocks) — `prepare_comunicado_flexible` with a single destinatario and `actividad_id=null` enqueues one Comunicacion and returns `total=1`
- [x] 2.3 GREEN: implement `prepare_comunicado_flexible(actividad_id, asunto_template, cuerpo_template, destinatarios, current_user, request)` in `profesor_service.py`: resolve email/nombre/apellido from the padron entry, resolve materia from `dictado_id`, build `EnvioMasivoItem`s, call `ComunicacionesService.enqueue_masivo` — never call `update_estado` directly
- [x] 2.4 RED+GREEN: when `actividad_id` is provided, validate it belongs to the tenant and the destinatario's dictado; 404/skip otherwise
- [x] 2.5 TRIANGULATE: destinatarios across two materias → groups by materia, calls `enqueue_masivo` once per materia, returns aggregated `total` and a `lotes` list
- [x] 2.6 TRIANGULATE: destinatario without email is excluded (total reflects exclusion); destinatario whose `entrada_padron_id`/`dictado_id` is outside the tenant or not among the professor's vigente dictados is rejected
- [x] 2.7 TRIANGULATE (approval reuse): with `tenant.aprobacion_comunicaciones=True`, enqueued comunicaciones stay pending (Pend), are NOT auto-sent; with `False`, they auto-transition to Enviando
- [x] 2.8 RED+GREEN: an audit entry is recorded for the flexible send, including resolved total and `actividad_id` (or null)
- [x] 2.9 REFACTOR: extract a shared email/identity-resolution helper; keep file ≤500 LOC

## 3. Backend — endpoint (Strict TDD, real DB)

- [x] 3.1 RED: API test — `POST /api/v1/profesor/comunicado-atrasados-flexible` returns 403 without `COMUNICACION_ENVIAR` (fail-closed)
- [x] 3.2 RED: API test — happy path (individual) enqueues and returns `{total, lote_id, lotes}`
- [x] 3.3 GREEN: add the router endpoint gated by `require_permission(Perm.COMUNICACION_ENVIAR)`, identity from session, delegating to `prepare_comunicado_flexible`, `await db.commit()`
- [x] 3.4 TRIANGULATE: 422 on unknown field (`extra='forbid'`); general mode across materias returns aggregated total + multiple `lotes`; tenant isolation (cannot target another tenant's entrada)
- [x] 3.5 REFACTOR: confirm no business logic in the router (delegates to service only)

## 4. Frontend — types, service, hook (TDD)

- [x] 4.1 Add types `ComunicadoDestinatario` (`{ entrada_padron_id, dictado_id }`) and `ComunicadoFlexibleData` (`{ actividad_id?: string|null, asunto_template, cuerpo_template, destinatarios }`) in `features/profesor/types/index.ts`; extend/confirm `ComunicadoResult` carries `lotes?: string[]`
- [x] 4.2 RED: test for `enviarComunicadoFlexible(data)` calling `POST /api/v1/profesor/comunicado-atrasados-flexible`
- [x] 4.3 GREEN: implement `enviarComunicadoFlexible` in `features/profesor/services/profesor.service.ts`
- [x] 4.4 GREEN: add `useMutationComunicadoFlexible` hook in `features/profesor/hooks/useProfesor.ts` (TanStack mutation)

## 5. Frontend — AtrasadosGeneralPage UI (TDD, components <200 LOC, no `any`)

- [x] 5.1 RED: component test — each row renders a per-row "Enviar comunicado" action that opens a form scoped to that student
- [x] 5.2 GREEN: add per-row individual action; pre-fill the student's overdue/failed materias derived client-side from `AtrasadoGeneral[]` by matching `entrada_padron_id`
- [x] 5.3 RED+GREEN: add the top-level "Enviar a todos" action that builds a `destinatarios` list from the currently visible (filter-respecting) rows
- [x] 5.4 RED+GREEN: comunicado form with Zod schema where `actividad_id` is OPTIONAL (`z.string().optional()`); submitting without an activity sends `actividad_id: null` and is not blocked
- [x] 5.5 GREEN: wire submit to `useMutationComunicadoFlexible`; show aggregated `total` and lote reference on success; extract the form into a sub-component if the page approaches 200 LOC
- [x] 5.6 TRIANGULATE: individual send → single-element `destinatarios`; general send under an active subject filter includes only filtered rows

## 6. Verification

- [ ] 6.1 Run backend test suite (coverage ≥80% lines, ≥90% on the new business rules); confirm approval-gate tests pass
- [x] 6.2 Run frontend tests/lint; confirm no `any` and components <200 LOC
- [ ] 6.3 Mark `[x]` the corresponding row in `CHANGES.md` and run `/opsx:archive`
