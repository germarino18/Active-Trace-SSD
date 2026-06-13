## Why

El sistema ya tiene seguridad completa (auth, RBAC, audit log) pero no tiene **estructura académica**: no existen carreras, cohortes, materias ni la instancia que las cruza (`Dictado`). Estas son las entidades raíz del dominio (C-06, GATE 5) sobre las que cuelgan todos los módulos downstream — usuarios/asignaciones, padrón, calificaciones, equipos, encuentros, coloquios. Sin ellas, nada del flujo académico puede construirse. `Dictado` materializa ADR-006 (catálogo único de `Materia` separado de su puesta en cursado en una `carrera × cohorte`).

## What Changes

- Nuevos modelos SQLAlchemy con `tenant_id` row-level y soft delete: `Carrera`, `Cohorte`, `Materia`, `Dictado`.
- Repositories con scope de tenant por defecto y métodos de unicidad por cada entidad.
- Services con la lógica de negocio: validación de unicidad por tenant, consistencia `Dictado.carrera_id == Cohorte.carrera_id`, y las reglas de estado (carrera inactiva no admite cohortes abiertas; no se crea `Dictado` sobre materia/carrera/cohorte inactiva).
- ABM (CRUD) bajo `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias`, `/api/admin/dictados`, cada endpoint con guard `require_permission("estructura:gestionar")` (rol ADMIN).
- Schemas Pydantic v2 (`extra='forbid'`) request/response por entidad.
- Auditoría de las acciones de mutación (alta/edición/baja/cambio de estado) vía el `AuditLogger` existente.
- Migración Alembic **005** (`carrera`, `cohorte`, `materia`, `dictado`) — una sola migración para todo el change. La 004 ya la tomó C-05 audit-log.
- **Fuera de alcance (decisión explícita)**: el re-anclaje de E5 Asignación / E6 Padrón / E10 Encuentro / E11 Guardia / E13 Aviso / E14 Evaluación a `dictado_id` se DIFIERE a sus respectivos changes (C-07+). C-06 solo crea las 4 entidades raíz y su ABM.

## Capabilities

### New Capabilities
- `estructura-academica`: gestión administrativa (ABM) de carreras, cohortes, materias y dictados del tenant, con unicidad por tenant, aislamiento multi-tenant, reglas de estado activa/inactiva y consistencia carrera↔cohorte de los dictados.

### Modified Capabilities
<!-- Ninguna: C-06 introduce capacidades nuevas; no modifica requisitos de specs existentes. -->

## Impact

- **Código nuevo**: `app/models/{carrera,cohorte,materia,dictado}.py`, `app/repositories/*_repository.py` (4), `app/services/estructura/*` (services), `app/schemas/estructura.py`, `app/api/v1/routers/estructura.py`, `app/core/permissions.py` (reusa `Perm.ESTRUCTURA_GESTIONAR`, ya definido).
- **Migración**: `alembic/versions/005_create_estructura_academica.py`.
- **Registro**: alta del router en `app/main.py`.
- **Permisos**: `estructura:gestionar` ya existe en el seed de C-04 (migración 003) y está asignado a ADMIN — **no requiere seeding nuevo**.
- **Dependencias**: C-04 (rbac) — archivado. Habilita GATE 5 (C-07, C-15, C-17).
- **Sin breaking changes**: solo agrega entidades y endpoints nuevos.
