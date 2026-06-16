## 1. Model + Migration

- [x] 1.1 Create `backend/app/models/tarea.py` with `Tarea` and `ComentarioTarea` models (BaseMixin, TenantMixin, SoftDeleteMixin, `TareaEstado` enum with PENDIENTE/EN_PROGRESO/RESUELTA/CANCELADA)
- [x] 1.2 Create Alembic migration `014_create_tarea_tables.py` (tarea + comentario_tarea tables with composite indexes)
- [x] 1.3 Register `Tarea` and `ComentarioTarea` in `backend/app/models/__init__.py`

## 2. Schemas

- [x] 2.1 Create `backend/app/schemas/tareas.py` with: `TareaCreate`, `TareaUpdateEstado`, `TareaRead` (with nested comments), `ComentarioCreate`, `ComentarioRead`, `TareaFilterParams`, `TareaEstado`

## 3. Repository

- [x] 3.1 Create `backend/app/repositories/tarea_repository.py` with `TareaRepository` extending `BaseRepository[Tarea]`:
  - `find_by_asignado(usuario_id, estado=None, materia_id=None, texto=None, skip=0, limit=20)` — tasks assigned to a user with optional filters
  - `find_all_managed(tenant_id, estado=None, materia_id=None, asignado_a_id=None, texto=None, skip=0, limit=20)` — admin listing with full filters
  - `get_with_comments(tarea_id)` — task + comments ordered by creado_at ASC

## 4. Service

- [x] 4.1 Create `backend/app/services/tareas_service.py` with `TareasService`:
  - `create_tarea(data, current_user, request)` → TareaRead (asignado_por = current_user)
  - `cambiar_estado(id, estado, comentario_opcional, current_user, request)` → TareaRead (validates via StateMachine, restricts RESUELTA→EN_PROGRESO to COORDINADOR/ADMIN)
  - `get_mis_tareas(current_user, filters)` → paginated list
  - `get_all_managed(current_user, filters)` → paginated list (COORDINADOR/ADMIN only)
  - `get_tarea(id, current_user)` → TareaRead with comments
  - `delete_tarea(id, current_user, request)` → None (soft-delete)
  - `agregar_comentario(tarea_id, texto, current_user)` → ComentarioRead
  - Factory `create()` classmethod following existing pattern

## 5. Router

- [x] 5.1 Create `backend/app/api/v1/routers/tareas.py` with endpoints:
  - `POST /api/v1/tareas` — create (perm: tareas:gestionar, service check for COORDINADOR/ADMIN)
  - `PATCH /api/v1/tareas/{id}/estado` — state transition (perm: tareas:gestionar)
  - `GET /api/v1/tareas/{id}` — get single task with comments (perm: tareas:gestionar)
  - `DELETE /api/v1/tareas/{id}` — soft-delete (perm: tareas:gestionar, COORDINADOR/ADMIN only)
  - `GET /api/v1/tareas/mias` — my tasks (perm: tareas:gestionar, any role)
  - `GET /api/v1/tareas` — admin list all (perm: tareas:gestionar, COORDINADOR/ADMIN only)
  - `POST /api/v1/tareas/{id}/comentarios` — add comment (perm: tareas:gestionar)

## 6. App Wiring

- [x] 6.1 Register `tareas_router` in `backend/app/main.py` (import + include_router)

## 7. Tests

- [x] 7.1 Write tests for `TareaRepository`:
  - find_by_asignado filters by estado/materia/texto
  - find_all_managed composite filters
  - tenant scoping
  - get_with_comments ordering
- [x] 7.2 Write tests for `TareasService`:
  - Task creation with proper asignado_por derivation
  - All valid/invalid state transitions via StateMachine
  - RESUELTA→EN_PROGRESO restricted to COORDINADOR/ADMIN
  - My tasks vs admin listing isolation
  - Soft delete
  - Comment addition to task
- [x] 7.3 Write API tests for all endpoints:
  - 201/200/204 on success
  - 403/404 on permission/not-found errors
  - 422 on invalid state transitions
  - Pagination and filtering
  - Comment creation via state transition with auto-comment
