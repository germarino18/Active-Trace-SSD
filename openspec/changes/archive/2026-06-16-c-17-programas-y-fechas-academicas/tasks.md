## 1. Models + Migration

- [x] 1.1 Create `backend/app/models/programa_materia.py` with `ProgramaMateria` model (BaseMixin, TenantMixin, SoftDeleteMixin, FK → Dictado, `titulo`, `referencia_archivo`, `cargado_at`)
- [x] 1.2 Create `backend/app/models/fecha_academica.py` with `FechaAcademica` model (BaseMixin, TenantMixin, SoftDeleteMixin, FK → Dictado, `TipoFechaAcademica` enum with PARCIAL/TP/COLOQUIO/RECUPERATORIO, `numero`, `periodo`, `fecha`, `titulo`)
- [x] 1.3 Create Alembic migration `015_create_programa_materia_fecha_academica_tables.py` (both tables with indexes on tenant_id+dictado_id, and dictado_id+periodo for fechas)
- [x] 1.4 Register `ProgramaMateria` and `FechaAcademica` in `backend/app/models/__init__.py`

## 2. Schemas

- [x] 2.1 Create `backend/app/schemas/programas.py` with: `ProgramaMateriaCreate`, `ProgramaMateriaRead` (with `from_attributes=True`), `ProgramaMateriaUpdate`
- [x] 2.2 Create `backend/app/schemas/fechas_academicas.py` with: `FechaAcademicaCreate`, `FechaAcademicaRead` (with `from_attributes=True`), `FechaAcademicaUpdate`, `FechaAcademicaFilterParams`, `LmsContentFragment`

## 3. Repositories

- [x] 3.1 Create `backend/app/repositories/programa_materia_repository.py` with `ProgramaMateriaRepository` extending `BaseRepository[ProgramaMateria]`:
  - `find_by_dictado(dictado_id)` — get program by dictado
  - `exists_by_dictado(dictado_id)` — check uniqueness
- [x] 3.2 Create `backend/app/repositories/fecha_academica_repository.py` with `FechaAcademicaRepository` extending `BaseRepository[FechaAcademica]`:
  - `find_by_dictado_periodo(dictado_id, periodo, skip, limit)` — tabular listing
  - `find_calendar(dictado_id, periodo)` — all dates grouped for calendar view
  - `exists_by_dictado_tipo_numero(dictado_id, tipo, numero)` — uniqueness check

## 4. Services

- [x] 4.1 Create `backend/app/services/programas_service.py` with `ProgramasService`:
  - `upload_programa(dictado_id, titulo, archivo, current_user, request)` → ProgramaMateriaRead (stores file, saves reference)
  - `update_programa(id, data, archivo_opcional, current_user, request)` → ProgramaMateriaRead
  - `get_programa(id, current_user)` → ProgramaMateriaRead
  - `get_by_dictado(dictado_id, current_user)` → ProgramaMateriaRead
  - `delete_programa(id, current_user, request)` → None (soft-delete, preserves file)
  - `download_programa(id, current_user)` → FileResponse
  - Factory `create()` classmethod following existing pattern
- [x] 4.2 Create `backend/app/services/fechas_academicas_service.py` with `FechasAcademicasService`:
  - `create_fecha(data, current_user, request)` → FechaAcademicaRead
  - `update_fecha(id, data, current_user, request)` → FechaAcademicaRead
  - `get_fecha(id, current_user)` → FechaAcademicaRead
  - `list_fechas(dictado_id, periodo, skip, limit, current_user)` → paginated list
  - `list_calendar(dictado_id, periodo, current_user)` → monthly-grouped view
  - `generate_lms_fragment(dictado_id, periodo, current_user)` → LmsContentFragment (markdown)
  - `delete_fecha(id, current_user, request)` → None (soft-delete)
  - Factory `create()` classmethod following existing pattern

## 5. Routers

- [x] 5.1 Create `backend/app/api/v1/routers/programas.py` with endpoints:
  - `POST /api/v1/programas` — upload program (perm: estructura:gestionar, multipart file)
  - `PATCH /api/v1/programas/{id}` — update (perm: estructura:gestionar)
  - `GET /api/v1/programas/{id}` — get single (perm: estructura:gestionar)
  - `GET /api/v1/programas/por-dictado/{dictado_id}` — get by dictado (perm: estructura:gestionar)
  - `DELETE /api/v1/programas/{id}` — soft-delete (perm: estructura:gestionar)
  - `GET /api/v1/programas/{id}/descargar` — download file (perm: estructura:gestionar)
- [x] 5.2 Create `backend/app/api/v1/routers/fechas_academicas.py` with endpoints:
  - `POST /api/v1/fechas-academicas` — create (perm: estructura:gestionar)
  - `PATCH /api/v1/fechas-academicas/{id}` — update (perm: estructura:gestionar)
  - `GET /api/v1/fechas-academicas/{id}` — get single (perm: estructura:gestionar)
  - `GET /api/v1/fechas-academicas` — tabular list (perm: estructura:gestionar, query params: dictado_id, periodo)
  - `DELETE /api/v1/fechas-academicas/{id}` — soft-delete (perm: estructura:gestionar)
  - `GET /api/v1/fechas-academicas/calendario` — calendar view (perm: estructura:gestionar, query params: dictado_id, periodo)
  - `GET /api/v1/fechas-academicas/fragmento-lms` — LMS fragment (perm: estructura:gestionar, query params: dictado_id, periodo)

## 6. App Wiring

- [x] 6.1 Register `programas_router` and `fechas_academicas_router` in `backend/app/main.py` (import + include_router)

## 7. Tests

- [x] 7.1 Write tests for `ProgramaMateriaRepository`:
  - find_by_dictado returns program for existing dictado
  - exists_by_dictado correctly checks uniqueness
  - tenant scoping isolation
- [x] 7.2 Write tests for `ProgramasService`:
  - Upload program with file
  - Update program title and file
  - Soft delete preserves file reference
  - Download returns file
  - Tenant isolation (cannot access other tenant's program)
- [x] 7.3 Write tests for `FechaAcademicaRepository`:
  - find_by_dictado_periodo filters correctly
  - find_calendar returns dates grouped by month
  - exists_by_dictado_tipo_numero uniqueness check
  - tenant scoping
- [x] 7.4 Write tests for `FechasAcademicasService`:
  - CRUD operations
  - Duplicate tipo+numero rejected
  - LMS fragment generation with dates
  - LMS fragment when no dates returns message
  - Soft delete
  - Tenant isolation
- [x] 7.5 Write API tests for all endpoints:
  - 201/200/204 on success
  - 403 on permission errors (user without estructura:gestionar)
  - 404 on not-found (other tenant or deleted)
  - 422 on validation errors (duplicate, invalid data)
  - File upload/download for programas
  - LMS fragment content format for fechas
