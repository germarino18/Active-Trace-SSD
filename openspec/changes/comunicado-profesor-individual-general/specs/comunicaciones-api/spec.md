## ADDED Requirements

### Requirement: Flexible overdue-communication endpoint with optional activity and explicit recipients
The comunicaciones API SHALL expose `POST /api/v1/profesor/comunicado-atrasados-flexible` that accepts an OPTIONAL `actividad_id` and an explicit list of recipients (`destinatarios`), enqueuing through the existing approval-gated bulk pipeline. The request schema MUST set `extra='forbid'` and the endpoint MUST require `Perm.COMUNICACION_ENVIAR`.

#### Scenario: Request contract
- **WHEN** a PROFESOR calls the endpoint with `{ actividad_id?: uuid|null, asunto_template, cuerpo_template, destinatarios: [{ entrada_padron_id, dictado_id }, ...] }`
- **THEN** the system accepts the request, requiring `asunto_template` and `cuerpo_template` (min length 1) and `destinatarios` with at least one element
- **THEN** the system rejects any undeclared field with 422

#### Scenario: Recipients grouped by materia into bulk lotes
- **WHEN** recipients span multiple materias
- **THEN** the system groups recipients by their materia (resolved server-side from `dictado_id`) and invokes the bulk enqueue once per materia, since each lote carries a single `materia_id` and `materia` template variable

#### Scenario: Response shape
- **WHEN** the enqueue completes
- **THEN** the system returns `{ total, lote_id, lotes }` where `total` is the count of enqueued communications, `lotes` is the list of generated lote ids, and `lote_id` is the single lote id when only one was generated (else null)
