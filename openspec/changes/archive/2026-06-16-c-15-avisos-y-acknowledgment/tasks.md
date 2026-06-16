## 1. Model + Migration

- [x] 1.1 Create `backend/app/models/aviso.py` with `Aviso` and `AcknowledgmentAviso` models (BaseMixin, TenantMixin, SoftDeleteMixin, enums for alcance/severidad)
- [x] 1.2 Create Alembic migration `013_create_aviso_tables.py` (aviso + acknowledgment_aviso tables with indexes)
- [x] 1.3 Register `Aviso` and `AcknowledgmentAviso` in `backend/app/models/__init__.py`

## 2. Schemas

- [x] 2.1 Create `backend/app/schemas/avisos.py` with: `AvisoCreate`, `AvisoUpdate`, `AvisoRead`, `AvisoVisibleRead` (with acknowledged bool), `AvisoListParams`, `AcknowledgmentRead`, `AcknowledgmentStats`, `ConfirmResponse`

## 3. Repository

- [x] 3.1 Create `backend/app/repositories/aviso_repository.py` with `AvisoRepository` extending `BaseRepository[Aviso]`:
  - `find_visible(usuario_id, roles, materia_ids, cohorte_ids)` — filtered by alcance, activo, date window, audience scope
  - `find_pending_ack(usuario_id, roles, materia_ids, cohorte_ids)` — visible + requiere_ack + not yet confirmed
  - `find_all_managed(skip, limit)` — for admin listing (all, including inactive)
  - `count_acknowledgments(aviso_id)` — total and per-user counts

## 4. Service

- [x] 4.1 Create `backend/app/services/avisos_service.py` with `AvisoService`:
  - `create_aviso(data, current_user, request)` → AvisoRead
  - `update(id, data, current_user, request)` → AvisoRead
  - `delete(id, current_user, request)` → None (soft-delete)
  - `get_visible(current_user)` → list of AvisoVisibleRead (with audience resolution)
  - `get_pendientes(current_user)` → list of AvisoVisibleRead (pending confirms)
  - `confirmar(aviso_id, current_user, request)` → ConfirmResponse (idempotent)
  - `get_stats(aviso_id, current_user)` → AcknowledgmentStats
  - Factory `create()` classmethod following existing pattern

## 5. Router

- [x] 5.1 Create `backend/app/api/v1/routers/avisos.py` with endpoints:
  - `POST /api/v1/avisos` — create (perm: avisos:publicar)
  - `PATCH /api/v1/avisos/{id}` — update (perm: avisos:publicar)
  - `DELETE /api/v1/avisos/{id}` — soft-delete (perm: avisos:publicar)
  - `GET /api/v1/avisos/{id}` — get single (perm: avisos:publicar)
  - `GET /api/v1/avisos` — list all managed (perm: avisos:publicar)
  - `GET /api/v1/avisos/visible` — visible for current user (auth required)
  - `GET /api/v1/avisos/pendientes` — pending confirms (auth required)
  - `POST /api/v1/avisos/{id}/confirmar` — confirm (perm: avisos:confirmar)
  - `GET /api/v1/avisos/{id}/stats` — ack stats (perm: avisos:publicar)

## 6. App Wiring

- [x] 6.1 Register `avisos_router` in `backend/app/main.py` (import + include_router)
- [x] 6.2 Register `AcknowledgmentAviso` in existing `AccionAuditoria` enum if needed

## 7. Tests

- [x] 7.1 Write unit/integration tests for `AvisoRepository`:
  - find_visible filters by alcance/activo/window
  - tenant scoping
  - find_pending_ack excludes already-confirmed
- [x] 7.2 Write unit/integration tests for `AvisoService`:
  - CRUD operations
  - audience resolution
  - idempotent confirmation
  - soft-delete cascade (acknowledgments preserved)
- [x] 7.3 Write API tests for all endpoints:
  - 201/200/204 on success
  - 403/404 on permission/not-found errors
  - 422 on validation errors
  - Pagination and ordering
