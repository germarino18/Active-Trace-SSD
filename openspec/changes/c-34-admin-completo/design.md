## Context

El módulo ADMIN tiene código backend (routers, services, repos, models) y frontend (páginas, hooks, servicios, componentes) ya escritos, pero con **gaps de integración** que impiden un funcionamiento E2E completo. Los cambios listados en el proposal son los necesarios para cerrar esos gaps: endpoints faltantes, filtros, asignación de roles, vigencia, métricas.

**Stack existente:**
- Backend: FastAPI async + SQLAlchemy 2.0 + Pydantic v2 — routers en `backend/app/api/v1/routers/`
- Frontend: React 18 + TypeScript + TanStack Query + React Hook Form + Zod — feature modules en `frontend/src/features/`
- Admin router backend existente: `admin.py` (roles/permisos CRUD + asignación rol-permiso)
- Admin frontend existente: `src/features/admin/` con pages para Usuarios, Carreras, Cohortes, Materias, EstructuraAcademica, Metricas, Auditoria

## Goals / Non-Goals

**Goals:**
- Cerrar todos los gaps de integración back ↔ front para ADMIN
- Agregar endpoints faltantes (toggle estado, métricas, programas, evaluaciones)
- Agregar filtros a endpoints de listado de estructura académica
- Implementar vigencia temporal en dictados
- Conectar el catálogo real de roles en el frontend de usuarios
- Asegurar que todas las páginas ADMIN funcionan con datos reales

**Non-Goals:**
- No se rediseña la UI existente (solo se conecta a backend real)
- No se implementan features de otros roles (COORDINADOR, PROFESOR, etc.)
- No se modifica el sistema de autorización/RBAC existente
- No se implementan flujos de importación masiva de datos

## Decisions

### D1: Toggle estado vía PATCH individual, no endpoint genérico
Cada recurso (carrera, cohorte, materia, dictado) tendrá su propio `PATCH /{recurso}/{id}/estado` en su router respectivo. Esto mantiene el patrón existente de un endpoint por recurso y evita introducir un router genérico que rompa la estructura actual. El endpoint alterna entre `Activa` ↔ `Inactiva`.

### D2: Vigencia en Dictado, no en Materia
La entidad `Dictado` (materia × carrera × cohorte) es el nivel correcto para la vigencia temporal, no `Materia`. Una materia es un concepto de catálogo (existe siempre), el dictado es la instancia concreta que tiene un período de validez. Si `vig_desde`/`vig_hasta` no existen en el modelo, se agregan vía migración Alembic. Si ya existen como columnas en el modelo, solo se exponen en schemas y se agregan a los response mappers.

### D3: Asignación de roles a usuarios vía tabla intermedia usuario_rol
Se crea (si no existe) la tabla `usuario_rol` con FK a `usuario` y `rol`, más vigencia (`desde`, `hasta`). Endpoints:
- `GET /api/admin/usuarios/{id}/roles` — lista roles asignados al usuario
- `POST /api/admin/usuarios/{id}/roles` — asigna un rol (body: `{rol_id, desde?, hasta?}`)
- `DELETE /api/admin/usuarios/{id}/roles/{rol_id}` — remueve asignación

### D4: Filtros en listados como query params opcionales
Se agregan parámetros `activa: Optional[bool]`, `q: Optional[str]` a los endpoints `GET /carreras`, `/cohortes`, `/materias`, `/dictados`. El repositorio recibe un objeto de filtros y los aplica en el query. El frontend pasa los filtros desde los hooks existentes.

### D5: Métricas como query agregadas, no tabla separada
El endpoint `GET /api/admin/metricas` ejecuta consultas agregadas sobre las tablas existentes: COUNT de usuarios activos, COUNT de alumnos, promedio de progreso, porcentaje en riesgo. No se crea una tabla de métricas — los datos son en vivo.

### D6: Evaluaciones y Programas como routers separados
Siguiendo el patrón existente, evaluaciones va en un nuevo `evaluaciones.py` router y programas en `programas.py` (o se extiende el existente). El frontend ya tiene servicios apuntando a `/api/v1/evaluaciones` — se respeta esa ruta.

### D7: Los endpoints de estado del backend ya usan soft delete
El spec existente dice que toggle estado es Activa/Inactiva, no soft delete. Se implementa como cambio de columna `estado`, no como `deleted_at`. Esto es consistente con cómo el spec `estructura-academica` describe el estado.

## Risks / Trade-offs

- [Riesgo] **Backend tiene endpoint PATCH pero frontend usa PUT para usuarios**: Hay que verificar el schema `UsuarioUpdate` vs `EditarUsuarioData` y alinearlos. Si hay mismatch, se prefiere PATCH en backend y se adapta el frontend.
- [Riesgo] **Dictado puede no tener campo `vig_desde`/`vig_hasta`**: Si el modelo no los tiene, se necesita migración Alembic + posible rollback. Se verifica antes de implementar.
- [Riesgo] **Métricas dependen de datos poblados**: Sin datos reales, las métricas devuelven ceros. Se documenta que es comportamiento esperado y se agrega un paso de seed data en los tests.
- [Trade-off] **No se refactoriza el frontend existente**: Algunas páginas pueden tener tipos que no matchean exactamente con las responses del backend. Se prioriza adaptar el frontend a las responses reales del backend.
