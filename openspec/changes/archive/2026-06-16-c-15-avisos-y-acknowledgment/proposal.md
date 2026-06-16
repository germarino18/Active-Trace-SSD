## Why

The platform needs a broadcast announcement system (`Aviso`) to communicate urgent or scheduled information to users by role, cohort, or course. Each aviso can require explicit acknowledgment, enabling tracking of who has read critical notices — a core requirement for academic compliance and institutional communication (F3.5).

## What Changes

- **New model `Aviso`**: tenant-scoped announcement with alcance (Global/PorMateria/PorCohorte/PorRol), severidad (Info/Advertencia/Crítico), visibility window (inicio_en/fin_en), ordering, active flag, and optional acknowledgment requirement.
- **New model `AcknowledgmentAviso`**: many-to-one join tracking which user confirmed reading which aviso, with timestamp.
- **New Alembic migration**: creates `aviso` and `acknowledgment_aviso` tables.
- **New repository `AvisoRepository`**: CRUD + filtered queries by audience (role, scope, cohorte) respecting visibility window (RN-18/19/20).
- **New service `AvisoService`**: create/update/delete avisos, list visible avisos for current user, confirm acknowledgment, get acknowledgment stats.
- **New router `avisos.py`** at `/api/v1/avisos`: endpoints for CRUD (COORDINADOR/ADMIN), visualization (filtered by role/scope/cohorte), and acknowledgment.
- **New schemas**: `AvisoCreate`, `AvisoUpdate`, `AvisoRead`, `AvisoListParams`, `AvisoConfirmRequest`, `AcknowledgmentStats`, `AcknowledgmentRead`.
- **Audit events**: aviso creation, update, deletion, and acknowledgment logging via existing AuditLogger.
- **New permission usage**: `avisos:publicar` (already exists in RBAC seed) guards write endpoints; `avisos:confirmar` (already exists) guards acknowledgment. No new permissions needed.

## Capabilities

### New Capabilities
- `avisos-crud`: Full CRUD for tenant announcements — create, update, soft-delete, list, and get-by-id.
- `avisos-visualization`: Filtered listing of visible avisos for the current user based on role, alcance, cohorte, and visibility window (RN-18/19/20).
- `avisos-acknowledgment`: Confirm reading an aviso (requiere_ack=true), list pending confirms, and retrieve acknowledgment counters (derived, not denormalized).

### Modified Capabilities
- *(none — no existing specs change behaviorally)*

## Impact

- **New files**:
  - `backend/app/models/aviso.py`
  - `backend/app/repositories/aviso_repository.py`
  - `backend/app/services/avisos_service.py`
  - `backend/app/schemas/avisos.py`
  - `backend/app/api/v1/routers/avisos.py`
  - `backend/alembic/versions/013_create_aviso_tables.py`
- **Modified files**:
  - `backend/app/main.py` — register new router
  - `backend/app/core/permissions.py` — `Perm` enum already has both `AVISOS_PUBLICAR` and `AVISOS_CONFIRMAR`; no change needed
- **No new dependencies** — uses existing TenantMixin, SoftDeleteMixin, BaseRepository, AuditLogger, PermissionResolver.
