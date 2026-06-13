## Context

C-06 es el primer change de la FASE 2 (GATE 5). La seguridad multi-tenant está completa: `Tenant` + mixins + repository base con scope de tenant (C-02), auth JWT (C-03), RBAC fino `modulo:accion` con guard `require_permission` (C-04) y audit log append-only + impersonación (C-05). Falta el esqueleto académico: las entidades raíz `Carrera`, `Cohorte`, `Materia` y la instancia `Dictado` (ADR-006).

Restricciones de contrato (reglas duras del proyecto):
- Multi-tenancy row-level: `tenant_id` en cada tabla; el `BaseRepository` filtra por tenant por defecto.
- Identidad SIEMPRE desde la sesión JWT (`CurrentUser`), nunca de URL/body.
- Flujo unidireccional Routers → Services → Repositories → Models. Sin lógica de negocio en routers, sin DB directa desde services.
- Soft delete siempre (append-only), nunca hard delete.
- Pydantic v2 con `extra='forbid'`. snake_case. ≤500 LOC/archivo. UNA migración Alembic.
- Strict TDD: cada task es un ciclo RED→GREEN→triangulación→REFACTOR; tests sin mocks de DB (DB efímera real).

Governance: MEDIO, pero toca core-models (CRÍTICO) → el diseño de tablas y las decisiones no obvias se documentan abajo.

## Goals / Non-Goals

**Goals:**
- Crear los 4 modelos raíz con sus constraints de unicidad por tenant y soft delete.
- ABM completo (list/get/create/update/soft-delete + cambio de estado) bajo `/api/admin/*` con guard `estructura:gestionar`.
- Codificar las reglas de negocio del dominio (unicidad, consistencia carrera↔cohorte, estados activa/inactiva) en la capa de Services.
- Auditar las mutaciones con el `AuditLogger` existente.
- Una sola migración Alembic (005) que crea las 4 tablas con sus índices únicos parciales (`WHERE deleted_at IS NULL`).

**Non-Goals:**
- **NO** re-anclar entidades downstream a `dictado_id`. E5 Asignación, E6 Padrón, E10 Encuentro, E11 Guardia, E13 Aviso, E14 Evaluación se re-anclan en SUS changes (C-07+). C-06 solo introduce `Dictado` como entidad raíz.
- NO sembrar el permiso `estructura:gestionar` (ya existe en C-04, ver Decisión 3).
- NO frontend (es C-24).
- NO endpoints de listado anidado/relacional avanzado (ej. dictados por carrera con joins): el ABM básico alcanza para C-06; las vistas las arma el frontend/los analíticos.

## Decisions

### D1 — `Dictado` es entidad raíz en C-06; el re-anclaje downstream se difiere
ADR-006 establece que calificaciones, equipos, encuentros y coloquios cuelgan del `Dictado`, no de `Materia`. La nota de modelado de §E3.1 (KB 04) es explícita: "C-06 introduce `Dictado` como entidad raíz; el re-anclaje de cada entidad downstream se hace en el change que la implementa, no acá".
- **Decisión**: C-06 crea las 4 tablas y su ABM. Las FK `dictado_id` en entidades downstream se agregan en C-07+ cuando esas entidades se construyen.
- **Por qué**: mantiene el change atómico (~4-6h), respeta los gates de dependencia, y evita migraciones que toquen tablas aún inexistentes. Alternativa rechazada: crear ya las FK forward — imposible, esas tablas no existen todavía, y acoplaría C-06 a decisiones de modelado de cada módulo.

### D2 — Consistencia `Dictado.carrera_id == Cohorte.carrera_id`: validación en Service, no constraint DB
La cohorte ya pertenece a una carrera (E2). Un `Dictado` debe referir la misma carrera que su cohorte.
- **Decisión**: validar la consistencia en `DictadoService.create/update` cargando la `Cohorte` y comparando `carrera_id`. Si no coinciden → `ValidationException`.
- **Por qué service-level en vez de DB**: PostgreSQL no soporta un CHECK que cruce filas de otra tabla; la única vía en DB sería una FK compuesta `(carrera_id, cohorte_id) → cohorte(carrera_id, id)` que exige un índice único `(id, carrera_id)` en `cohorte` y propaga complejidad. La validación en Service es explícita, testeable, y devuelve un error de dominio claro (422) en lugar de un IntegrityError opaco. Alternativa considerada: FK compuesta — se descarta por sobre-ingeniería para C-06; la consistencia queda cubierta por test. **Decisión no obvia surfaceada para revisión (governance core-models).**

### D3 — `estructura:gestionar` ya existe: no se siembra
Verificado en `alembic/versions/003_create_rol_permiso_tables.py`: `PERMISOS` incluye `("estructura:gestionar", "estructura")` (línea 47) y `MATRIX` lo asigna a `ADMIN` (línea 103). `Perm.ESTRUCTURA_GESTIONAR = "estructura:gestionar"` ya está en `app/core/permissions.py` y se usa en `admin.py`.
- **Decisión**: reusar `Perm.ESTRUCTURA_GESTIONAR` en el guard. NO agregar seeding. La migración 005 no toca `permiso`/`rol_permiso`.

### D4 — Unicidad: índice único parcial por tenant con `WHERE deleted_at IS NULL`
Siguiendo el patrón establecido en C-03/C-04 (`ix_permiso_codigo_tenant`):
- `carrera`: índice único `(tenant_id, codigo) WHERE deleted_at IS NULL`.
- `materia`: índice único `(tenant_id, codigo) WHERE deleted_at IS NULL`.
- `cohorte`: índice único `(tenant_id, carrera_id, nombre) WHERE deleted_at IS NULL`.
- `dictado`: índice único `(tenant_id, materia_id, carrera_id, cohorte_id) WHERE deleted_at IS NULL`.
- **Por qué parcial**: el soft delete permite "reusar" un código/nombre tras dar de baja el registro anterior; el índice parcial sólo cuenta filas vivas. La verificación de unicidad se hace primero en el Service (devuelve 422 con mensaje claro vía `ValidationException`); el índice DB es la red de seguridad contra carreras concurrentes.

### D5 — Reglas de estado en Service
- **Carrera inactiva no admite cohortes abiertas** (E1, E2): al crear/actualizar una `Cohorte` con `vig_hasta IS NULL` (abierta), el Service verifica que la `Carrera` esté `Activa`; si no → `ValidationException`.
- **No se crea `Dictado` sobre materia/carrera/cohorte inactiva** (E3.1): `DictadoService` carga las tres entidades referidas y rechaza si alguna está inactiva.
- **Por qué Service**: son reglas de dominio que cruzan entidades; no expresables como CHECK de una sola tabla.

### D6 — Estructura de capas (espejo de C-04)
- Modelos: un archivo por entidad en `app/models/`, usando `BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin`.
- Repositories: uno por entidad extendiendo `BaseRepository`, con un método `find_by_*` para la verificación de unicidad (scope tenant + soft-delete ya aplicados por la base).
- Services: uno por entidad (o un módulo `app/services/estructura/`), reciben `session` + `current_user`, orquestan repos, aplican reglas y disparan auditoría.
- Router: un único `app/api/v1/routers/estructura.py` con cuatro sub-secciones (carreras/cohortes/materias/dictados), guard `_estructura_guard = [Depends(require_permission(Perm.ESTRUCTURA_GESTIONAR))]`. Identidad y tenant desde `get_current_user`.
- Schemas: `app/schemas/estructura.py` con `*Create`/`*Update`/`*Response` por entidad, todos `extra='forbid'`.

### D7 — Enum de estado
`Carrera`/`Materia`/`Cohorte`: estado `Activa | Inactiva`. `Dictado`: `Activo | Inactivo` (KB usa género distinto). Se modelan como `str` con `Enum` Python validado en Pydantic; en DB columna `String` con CHECK o `sa.Enum`. Se opta por `String` + validación Pydantic (consistente con el patrón de roles/permisos que usan `String` libre), manteniendo la migración simple. El default al crear es `Activa`/`Activo`.

## Risks / Trade-offs

- [Consistencia carrera↔cohorte sólo en Service] → un cliente que escriba directo en DB podría violarla. Mitigación: toda escritura pasa por el Service (regla dura: sin DB directa); cubierto por test de integración. Documentado para revisión de governance.
- [Race condition en unicidad entre check de Service e insert] → dos requests concurrentes podrían pasar el check. Mitigación: el índice único parcial en DB es la red de seguridad; el `IntegrityError` se traduce a `ValidationException` (422) en el router/handler.
- [Soft delete + unicidad parcial] → reusar un código tras baja es intencional (no un bug); los tests deben cubrir "alta → baja → alta con mismo código = OK".
- [Volumen de tablas/tests en un solo change] → 4 entidades × CRUD × reglas. Mitigación: el ABM es homogéneo (espejo de `admin.py`); se reutiliza el `BaseRepository` y el patrón de router.

## Migration Plan

1. Crear `alembic/versions/005_create_estructura_academica.py` con `down_revision = "d4e5f6a7b8c9"` (la 004). Crea `carrera`, `cohorte`, `materia`, `dictado` con FKs (`tenant_id`, y en cohorte/dictado las FKs académicas con `ondelete` apropiado), columnas de mixins (id, created_at, updated_at, deleted_at, created_by_id, updated_by_id) e índices únicos parciales de D4.
2. `downgrade()` dropea las 4 tablas en orden inverso (dictado → cohorte → materia → carrera) y sus índices.
3. No toca `permiso`/`rol_permiso` (D3).
4. Rollback: `alembic downgrade -1`. Sin pérdida de datos en otras tablas (tablas nuevas).

## Open Questions

- Ninguna bloqueante para C-06. PA-01 (Materia vs InstanciaDictado) queda resuelta por ADR-006 = `Materia` (catálogo) + `Dictado` (instancia). PA-07 (cohortes ↔ carrera) queda resuelta por el modelo E2 (`Cohorte.carrera_id`) + la consistencia de D2.
- `Cohorte.anio` y `vig_desde/vig_hasta`: se incluyen como atributos (E2) pero sin reglas adicionales más allá de "abierta = `vig_hasta IS NULL`" (usado por la regla de carrera inactiva, D5).
