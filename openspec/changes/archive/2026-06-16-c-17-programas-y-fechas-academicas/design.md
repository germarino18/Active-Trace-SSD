## Context

C-17 adds two academic management modules to the activia-trace platform: program documents (ProgramaMateria) and academic dates (FechaAcademica). These complete the Epica 5 — Estructura Académica (F5.3, F5.4) and support the COORDINADOR's FL-03 setup flow (pasos 5-6: carga de programas y fechas de evaluaciones).

The project already supports:
- `Dictado` (C-06) as the root academic context entity per ADR-006
- `estructura:gestionar` in Perm enum and RBAC seed
- Existing patterns: BaseMixin, TenantMixin, SoftDeleteMixin, BaseRepository, Service with factory pattern, Router at `/api/v1/` with `require_permission` guards
- Pydantic v2 schemas with `extra='forbid'` and `from_attributes=True`
- Alembic migrations (latest: 014 from C-16)
- Soft delete on all entities
- Real PostgreSQL test DB (no mocking)

Latest migration is 014. The new migration will be 015.

## Goals / Non-Goals

**Goals:**
- Model `ProgramaMateria`: store program document reference (opaque pointer) per `dictado_id`, with title and upload timestamp
- Model `FechaAcademica`: academic evaluation dates (Parcial/TP/Coloquio/Recuperatorio) per `dictado_id`, with instance number, period label, date, and title
- Expose `/api/v1/programas` CRUD endpoints guarded by `estructura:gestionar`
- Expose `/api/v1/fechas-academicas` CRUD endpoints guarded by `estructura:gestionar`
- Generate LMS-ready content fragment from academic dates for a given dictado and period (F5.4)
- Audit log all write operations (create, update, delete) for both entities
- Tenant isolation on both entities via existing TenantMixin + BaseRepository pattern

**Non-Goals:**
- No dedicated file storage service — `referencia_archivo` stores an opaque reference (local path or storage key); actual file upload/multipart is included, but cloud storage integration is deferred
- No calendar integration (Google Calendar, Outlook) — the calendar view is in-app only
- No iCal export
- No public (unauthenticated) access to program files or dates
- No frontend implementation — API only
- No new permissions — `estructura:gestionar` already exists

## Decisions

### D1: `dictado_id` as FK for both entities (ADR-006)

Both `ProgramaMateria` and `FechaAcademica` use `dictado_id` (FK → Dictado) instead of individual `materia_id`/`carrera_id`/`cohorte_id` fields. This follows the same pattern used in C-13 (encuentros-y-guardias: D2) and C-14 (evaluaciones-y-coloquios), aligning with ADR-006.

**Rationale**: Dictado is the root academic context entity. Using `dictado_id` guarantees consistency with downstream entities and simplifies the model to a single FK. The full context (materia, carrera, cohorte) is resolved via JOIN through Dictado.

**Alternativa considerada**: Maintaining individual fields as originally sketched in KB E15/E16 — descartado porque va contra el patrón ADR-006 ya adoptado en C-13 and C-14.

### D2: ProgramaMateria uniqueness on `dictado_id`

`ProgramaMateria` has a unique constraint on `(tenant_id, dictado_id)` among non-deleted records. Each dictado can have at most one program document.

**Rationale**: A single subject×career×cohort combination should have exactly one official program document. If a new version replaces the old one, the existing record is updated (not versioned), keeping the model simple.

**Alternativa considerada**: Versioned program history — descartada porque el requerimiento actual (F5.3) es "subir y asociar el programa oficial", no "historial de versiones". Versioning can be added later if needed.

### D3: `referencia_archivo` as opaque text pointer

`referencia_archivo` stores a path or key that points to the uploaded file. For this change, the upload endpoint accepts a multipart file via `UploadFile`, stores it to a configured local directory, and saves the relative path in `referencia_archivo`. The download endpoint returns the file via `FileResponse`.

**Rationale**: This enables the feature without blocking on a cloud storage integration. The system only handles the reference opaquely, so switching to S3/MinIO later only requires changing the upload/download implementation in the service layer — no schema changes.

### D4: FechaAcademica uses dictado_id + `periodo` as scoping fields

`FechaAcademica` uses `dictado_id + tipo + numero` for instance identity, and `periodo` (text, e.g., "2026-1") as the academic period scoping field for listing/calendar queries.

**Rationale**: The `periodo` text field is flexible (supports "2026-1", "2026-A", etc.) without requiring a separate period entity or calendar table. Combined with `dictado_id`, it allows filtering all dates for a specific subject×period in a single query.

### D5: LMS content fragment as plain text/markdown

The F5.4 fragment is generated as a simple formatted text block (markdown or plain text) listing academic dates grouped by type and ordered by date.

**Rationale**: Simpler than HTML (which varies by LMS). A markdown fragment is universally pasteable into any LMS editor. If HTML is required later, it can be added as an additional format option.

### D6: Single migration for both tables

Migration 015 creates both `programa_materia` and `fecha_academica` tables in one migration, with indexes on `(tenant_id, dictado_id)` for both tables and an additional index on `(dictado_id, periodo)` for fecha_academica queries.

**Rationale**: Both tables are conceptually part of the same module (estructura académica) and have no inter-dependency. A single migration is simpler and faster.

## Risks / Trade-offs

- **[Risk] Local file storage not suitable for multi-instance deployments**: If the app scales to multiple replicas, local file uploads won't be shared. **Mitigation**: The service layer abstracts file storage behind a simple interface. When cloud storage is needed, only the upload/download methods in the service change — no model or schema changes.
- **[Risk] No program versioning**: If a coordinator uploads a new program, the old reference is overwritten. **Mitigation**: The audit log records all updates (who changed what and when). Full versioning can be added as an enhancement.
- **[Trade-off] Plain text vs. HTML LMS fragment**: A markdown fragment may need manual formatting for some LMS platforms. Acceptable because most modern LMS editors support markdown paste. HTML generation can be added as a format option.
