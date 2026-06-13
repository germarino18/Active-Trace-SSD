# Tasks — C-06 estructura-academica

> Strict TDD por task: RED (test que falla) → GREEN (mínimo) → TRIANGULAR (≥2 casos: happy + edge) → REFACTOR. Tests sin mocks de DB (DB efímera real, fixtures de `tests/conftest.py`). Cada test de regla de negocio cubre el escenario correspondiente del spec.

## 1. Modelos y migración (capa de datos)

- [x] 1.1 RED→GREEN: `Carrera` model en `app/models/carrera.py` (`BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin`): `codigo` (String, not null), `nombre` (String, not null), `estado` (String, default "Activa"); índice único parcial `ix_carrera_codigo_tenant` sobre `(tenant_id, codigo) WHERE deleted_at IS NULL`. Test: instancia + persistencia + scope tenant.
- [x] 1.2 RED→GREEN: `Materia` model en `app/models/materia.py` (mismos mixins): `codigo`, `nombre`, `estado` (default "Activa"); índice único parcial `ix_materia_codigo_tenant` sobre `(tenant_id, codigo) WHERE deleted_at IS NULL`.
- [x] 1.3 RED→GREEN: `Cohorte` model en `app/models/cohorte.py` (mismos mixins): `carrera_id` (FK `carrera.id`, not null), `nombre`, `anio` (Integer), `vig_desde` (Date, nullable), `vig_hasta` (Date, nullable), `estado` (default "Activa"); índice único parcial `ix_cohorte_nombre_tenant` sobre `(tenant_id, carrera_id, nombre) WHERE deleted_at IS NULL`.
- [x] 1.4 RED→GREEN: `Dictado` model en `app/models/dictado.py` (mismos mixins): `materia_id` (FK `materia.id`), `carrera_id` (FK `carrera.id`), `cohorte_id` (FK `cohorte.id`), `estado` (default "Activo"); índice único parcial `ix_dictado_terna_tenant` sobre `(tenant_id, materia_id, carrera_id, cohorte_id) WHERE deleted_at IS NULL`.
- [x] 1.5 Registrar los 4 modelos en `app/models/__init__.py` (import para que Alembic/metadata los vea).
- [x] 1.6 Crear migración `alembic/versions/005_create_estructura_academica.py` con `down_revision = "d4e5f6a7b8c9"`: crea `carrera`, `materia`, `cohorte`, `dictado` con columnas de mixins (id, tenant_id, created_at, updated_at, deleted_at, created_by_id, updated_by_id), FKs (`tenant_id`→tenant CASCADE; FKs académicas) e índices únicos parciales de D4. `downgrade()` dropea en orden inverso (dictado→cohorte→materia→carrera). NO toca `permiso`/`rol_permiso`.
- [x] 1.7 Verificar `alembic upgrade head` y `downgrade -1` en DB de test (round-trip de la migración).

## 2. Repositories (scope tenant + unicidad)

- [x] 2.1 RED→GREEN: `CarreraRepository` (extiende `BaseRepository`) en `app/repositories/carrera_repository.py` con `find_by_codigo(tenant_id, codigo)` (vivos). Test: unicidad detectada, scope tenant, soft-delete excluido.
- [x] 2.2 RED→GREEN: `MateriaRepository` con `find_by_codigo(tenant_id, codigo)`.
- [x] 2.3 RED→GREEN: `CohorteRepository` con `find_by_nombre(tenant_id, carrera_id, nombre)`.
- [x] 2.4 RED→GREEN: `DictadoRepository` con `find_by_terna(tenant_id, materia_id, carrera_id, cohorte_id)`.

## 3. Schemas (Pydantic v2, extra='forbid')

- [x] 3.1 `app/schemas/estructura.py`: `CarreraCreate`/`CarreraUpdate`/`CarreraResponse` (codigo, nombre, estado). Todos `model_config = ConfigDict(extra="forbid")`; `estado` validado contra enum Activa/Inactiva.
- [x] 3.2 `MateriaCreate`/`MateriaUpdate`/`MateriaResponse`.
- [x] 3.3 `CohorteCreate`/`CohorteUpdate`/`CohorteResponse` (carrera_id, nombre, anio, vig_desde, vig_hasta, estado).
- [x] 3.4 `DictadoCreate`/`DictadoUpdate`/`DictadoResponse` (materia_id, carrera_id, cohorte_id, estado: Activo/Inactivo).

## 4. Services (reglas de negocio)

- [x] 4.1 RED→GREEN→TRIANGULAR: `CarreraService` en `app/services/estructura/carrera_service.py`: create/update/soft_delete/cambio_estado. Regla: unicidad `(tenant_id, codigo)` → `ValidationException` si duplicado vivo. Tests: alta OK, duplicado rechazado, reúso tras baja OK, cambio de estado.
- [x] 4.2 RED→GREEN→TRIANGULAR: `MateriaService`: unicidad `(tenant_id, codigo)`. Tests: alta OK, duplicado rechazado.
- [x] 4.3 RED→GREEN→TRIANGULAR: `CohorteService`: unicidad `(tenant_id, carrera_id, nombre)` + regla D5 "carrera inactiva no admite cohorte abierta (`vig_hasta` nulo)" → `ValidationException`. Tests: alta en carrera activa OK, nombre duplicado rechazado, cohorte abierta sobre carrera inactiva rechazada.
- [x] 4.4 RED→GREEN→TRIANGULAR: `DictadoService`: unicidad de terna + consistencia D2 (`Dictado.carrera_id == Cohorte.carrera_id`) + regla D5 (materia/carrera/cohorte no inactivas) → `ValidationException`. Tests: alta consistente OK, terna duplicada rechazada, inconsistencia carrera↔cohorte rechazada, alta sobre entidad inactiva rechazada.
- [x] 4.5 Integrar `AuditLogger` en las mutaciones de los 4 services (alta/edición/baja/cambio de estado) con código de acción de estructura. Test: alta genera registro de auditoría atribuido al actor.

## 5. Router ABM (/api/admin/*)

- [x] 5.1 RED→GREEN: `app/api/v1/routers/estructura.py` con `router = APIRouter(prefix="/api/admin", tags=["estructura"])` y `_estructura_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]`. Identidad/tenant SIEMPRE desde `get_current_user`.
- [x] 5.2 Endpoints carreras: `GET/POST/GET{id}/PUT{id}/DELETE{id}` + cambio de estado, todos con `_estructura_guard`. Test: 403 sin permiso, 200/201 con ADMIN, 404 cross-tenant.
- [x] 5.3 Endpoints materias (mismo patrón).
- [x] 5.4 Endpoints cohortes (mismo patrón).
- [x] 5.5 Endpoints dictados (mismo patrón).
- [x] 5.6 Registrar el router en `app/main.py` (`include_router(estructura_router)`).

## 6. Tests de integración y cierre

- [x] 6.1 Test de aislamiento multi-tenant E2E: tenant A no ve/edita/borra entidades del tenant B; no puede referenciar carrera/cohorte/materia de B al crear cohorte/dictado.
- [x] 6.2 Test de unicidad por tenant: el mismo `codigo`/`nombre`/terna puede repetirse entre tenants distintos (no colisiona).
- [x] 6.3 Test del guard `estructura:gestionar`: usuario sin el permiso → 403 en cada endpoint; ADMIN → OK.
- [x] 6.4 Verificar cobertura ≥80% líneas / ≥90% reglas de negocio del módulo. Confirmar ≤500 LOC por archivo backend.
