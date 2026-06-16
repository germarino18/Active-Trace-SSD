## Why

Coordinators and administrators need to centralize the official program documents for each subject per career and cohort (F5.3), and manage the academic calendar of exams, assignments, and colloquia with tabular and calendar views (F5.4). Without this, program versions are scattered across shared drives and evaluation dates are communicated manually — both sources of confusion during peak academic periods. This change also enables generating ready-to-publish LMS content fragments from the academic dates.

## What Changes

- **New model `ProgramaMateria`**: tenant-scoped document record for a subject×career×cohort combination, with `titulo`, `referencia_archivo` (opaque pointer to storage), and `cargado_at` timestamp.
- **New model `FechaAcademica`**: tenant-scoped academic event (Parcial/TP/Coloquio/Recuperatorio) per subject×cohort, with instance number, period label, date, and descriptive title.
- **New Alembic migration**: creates `programa_materia` and `fecha_academica` tables.
- **New repository `ProgramaMateriaRepository`**: CRUD + filtered queries by subject×career×cohort, tenant-scoped.
- **New repository `FechaAcademicaRepository`**: CRUD + filtered queries by subject×cohort×period, tenant-scoped.
- **New service `ProgramasService`**: upload+associate program document (stores reference), list by subject×career×cohort, update/soft-delete.
- **New service `FechasAcademicasService`**: CRUD for academic dates, list (tabular), calendar-format query, and LMS content fragment generation.
- **New router `programas.py`** at `/api/v1/programas`: upload, list, get-by-id, update, soft-delete. Guards with `estructura:gestionar`.
- **New router `fechas_academicas.py`** at `/api/v1/fechas-academicas`: CRUD, tabular list, calendar view, LMS fragment generation. Guards with `estructura:gestionar`.
- **New schemas**: `ProgramaMateriaCreate`, `ProgramaMateriaRead`, `ProgramaMateriaUpdate`, `FechaAcademicaCreate`, `FechaAcademicaRead`, `FechaAcademicaUpdate`, `FechaAcademicaFilterParams`, `LmsContentFragment`.
- **LMS content fragment** (F5.4): the system generates a formatted content fragment ready to paste into the LMS virtual classroom, listing all academic dates for a subject×cohort×period.
- **Audit events**: creation, update, and deletion of programs and academic dates via existing AuditLogger.
- **Permission reuse**: `estructura:gestionar` (already exists in Perm enum and RBAC seed) guards all endpoints. No new permissions needed.

## Capabilities

### New Capabilities
- `programas-materia`: Upload, associate, list, update, and soft-delete program documents per subject×career×cohort with `referencia_archivo` opaque pointer to storage.
- `fechas-academicas`: Full CRUD of academic dates (Parcial/TP/Coloquio/Recuperatorio) per subject×cohort×instance number, with tabular listing, calendar view, and LMS fragment generation.

### Modified Capabilities
- *(none — no existing specs change behaviorally)*

## Impact

- **New files**:
  - `backend/app/models/programa_materia.py`
  - `backend/app/models/fecha_academica.py`
  - `backend/app/repositories/programa_materia_repository.py`
  - `backend/app/repositories/fecha_academica_repository.py`
  - `backend/app/services/programas_service.py`
  - `backend/app/services/fechas_academicas_service.py`
  - `backend/app/schemas/programas.py`
  - `backend/app/schemas/fechas_academicas.py`
  - `backend/app/api/v1/routers/programas.py`
  - `backend/app/api/v1/routers/fechas_academicas.py`
  - `backend/alembic/versions/0NN_create_programa_materia_fecha_academica_tables.py`
- **Modified files**:
  - `backend/app/models/__init__.py` — register ProgramaMateria, FechaAcademica
  - `backend/app/main.py` — register both routers
- **No new permissions** — `estructura:gestionar` already exists.
