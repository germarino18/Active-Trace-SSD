## Why

El panel ADMIN es el centro de gestión del tenant: estructura académica, usuarios, roles, permisos, equipos docentes, encuentros y auditoría. Aunque el proyecto tiene routers backend y páginas frontend para ADMIN, existen **gaps de integración** y **funcionalidades faltantes** que impiden que el módulo funcione de extremo a extremo: endpoints faltantes (toggle estado, métricas, evaluaciones, programas), filtros no implementados, desajustes frontend-backend, y la ausencia de **vigencia temporal en materias/dictados** — un requisito explícito del negocio. Este cambio completa toda la funcionalidad ADMIN para ambos lados del stack.

## What Changes

**Backend:**
- Agregar endpoint `PATCH /carreras/{id}/estado`, `PATCH /cohortes/{id}/estado`, `PATCH /materias/{id}/estado` para toggle de estado (Activa/Inactiva)
- Agregar endpoint `PATCH /dictados/{id}/estado` para toggle de estado en dictados
- Agregar **vigencia temporal** (`vig_desde`, `vig_hasta`) al modelo `Dictado` y exponer en schemas
- Agregar filtros (`activa`, `q`, `skip`, `limit`) a endpoints de listado de carreras, cohortes, materias
- Agregar endpoint `GET /api/admin/usuarios/{id}/roles` y `POST /api/admin/usuarios/{id}/roles` para asignación explícita de roles a usuarios
- Agregar endpoint `GET /api/admin/metricas` con KPIs del tenant
- Agregar endpoint de programas (file upload + listado) para materias
- Agregar endpoint de evaluaciones CRUD
- Asegurar que `PATCH /usuarios/{id}` reciba los campos correctos (matching frontend `EditarUsuarioData`)

**Frontend:**
- Conectar `UsuariosPage` con el catálogo real de roles (desde `/api/admin/roles`) en lugar de un campo texto
- Agregar `MetricasPage` funcional conectada al endpoint de métricas
- Agregar página o sección de **Dictados** con vigencia y toggle de estado
- Agregar manejo de errores consistente en todas las páginas admin
- Conectar `Evaluaciones` y `Programas` si los endpoints se implementan
- Asegurar que los filtros en las tablas funcionen contra backend real

**Testing:**
- Tests backend para cada nuevo endpoint (pytest, ≥80% cobertura)
- Tests de integración frontend para flujos críticos ADMIN

## Capabilities

### New Capabilities
- `vigencia-dictados`: Gestión de fechas de vigencia en dictados (materia × carrera × cohorte)
- `metricas-tenant`: KPIs globales del tenant (alumnos, riesgo, progreso) para el panel ADMIN
- `admin-roles-usuarios`: Asignación explícita y catálogo de roles desde la gestión de usuarios
- `admin-estado-toggle`: Endpoints para cambiar estado Activa/Inactiva de entidades de estructura académica
- `evaluaciones-crud`: ABM de evaluaciones (parciales, TPs, coloquios)

### Modified Capabilities
- `estructura-academica`: Agregar filtros por `activa` en listados y campo `vig_desde`/`vig_hasta` opcional en dictados
- `usuarios`: Vincular con catálogo de roles real en lugar de campo texto; exponer endpoint de asignación de roles
- `ui-admin`: Completar integración con todos los endpoints backend; agregar MetricasPage funcional y DictadosPage

## Impact

- **Backend**: `backend/app/api/v1/routers/estructura.py` — nuevos endpoints PATCH + filtros; `backend/app/api/v1/routers/usuarios.py` — asignación de roles; nuevos routers para métricas, evaluaciones, programas
- **Frontend**: `frontend/src/features/admin/` — conectar páginas existentes con backend real; nuevas páginas para Dictados; actualizar UsuarioFormModal con selector de roles desde API
- **Schemas**: nuevos schemas Pydantic para métricas, evaluaciones, programas
- **Modelos**: posible migración Alembic para agregar `vig_desde`/`vig_hasta` a Dictado (si no existen)
- **Tests**: nuevas suites para cada endpoint/module
