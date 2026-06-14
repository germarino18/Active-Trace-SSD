## Why

activia-trace todavía no tiene un perfil de persona ni un modelo de autorización contextual: hoy la identidad vive en `users` (solo auth) con un campo plano `users.roles` (ARRAY tenant-global, sin contexto ni vigencia), y no existe lugar para los datos de negocio y la PII de cada usuario (DNI, CUIL, CBU). C-07 introduce el modelo `Usuario` (perfil con PII cifrada) y `Asignacion` (Usuario ↔ Rol ↔ contexto académico, con vigencia temporal), convirtiendo a `Asignacion` en la **fuente de verdad de los roles** que alimenta el RBAC. Es el eje del modelo de autorización (KB E5) y desbloquea la gestión de equipos docentes, encuentros, coloquios y liquidaciones aguas abajo.

## What Changes

- **Nueva tabla `usuario`** (perfil de negocio, FK 1:1 a `users.id`): `nombre`, `apellidos`, PII **cifrada AES-256** (`dni`, `cuil`, `cbu`, `alias_cbu`), `banco`, `regional`, `legajo` y `legajo_profesional` (atributos de negocio opcionales, nunca credencial — regla dura #14), `facturador`, `estado` (Activo|Inactivo). `users` queda **solo auth** (no se le agregan columnas PII). El `email` no se duplica: vive solo en `users.email` (ya es la clave `(tenant_id, email)` de login).
- **Nueva infraestructura de cifrado**: un `TypeDecorator` de SQLAlchemy (`EncryptedString`) que envuelve las primitivas AES-256-GCM ya existentes en `app/core/security.py` (`encrypt_value`/`decrypt_value`/`get_encryption_key`). La PII se cifra at-rest y se descifra solo en lectura explícita; nunca aparece en logs ni en respuestas.
- **Nueva tabla `asignacion`** (KB E5): `usuario_id`, `rol` (enum), contexto académico `dictado_id` + `materia_id`/`carrera_id`/`cohorte_id` (nullable = rol de tenant global), `comisiones`, `responsable_id` (jerarquía docente), vigencia `desde`/`hasta`. `estado_vigencia` (Vigente|Vencida) es **derivado por fechas, no almacenado**.
- **BREAKING — RBAC: los roles efectivos pasan a derivarse de `Asignacion` vigente**, reemplazando `users.roles`. El claim `roles` del JWT (`TokenService`) y `CurrentUser.roles` (`get_current_user`) se computan como `DISTINCT asignacion.rol` con `estado_vigencia = Vigente`. La firma de `PermissionResolver.get_effective_permissions(tenant_id, roles)` **no cambia**. El contexto de `Asignacion` NO acota permisos en C-07 (RBAC sigue tenant-global vía el catálogo `rol_permiso` de C-04); acotar por contexto es alcance futuro.
- **Migración 007 con backfill**: por cada `users.roles[i]` existente crea una `Asignacion` con ese rol, sin contexto, `desde = users.created_at`, `hasta = NULL`. Marca `users.roles` como deprecado (no se lee en runtime).
- **Nuevo permiso `equipos:asignar`** en el catálogo (hoy solo existe `equipos:gestionar`), sembrado para COORDINADOR y ADMIN, requerido por el CRUD de asignaciones.
- **ABM `/api/admin/usuarios`** (gate `usuarios:gestionar`, ya existe) y **CRUD `/api/asignaciones`** (gate `equipos:asignar`). Soft-delete siempre; una asignación vencida se conserva en el histórico y no otorga permisos.

## Capabilities

### New Capabilities
- `usuarios`: perfil de negocio `Usuario` (1:1 con la identidad de auth `users`), PII cifrada AES-256, atributos de negocio (legajo, facturador, banco), estado, ABM administrativo y reglas de no-exposición de PII.
- `asignaciones`: vínculo Usuario↔Rol↔contexto académico con vigencia temporal; fuente de verdad de los roles efectivos; jerarquía `responsable_id`; CRUD gated por `equipos:asignar`; conservación histórica de asignaciones vencidas.

### Modified Capabilities
- `auth-jwt-2fa`: el claim `roles` del access token deja de leerse de `users.roles` y pasa a derivarse de las asignaciones vigentes del usuario.
- `rbac-permisos-finos`: la resolución de permisos se alimenta de los roles derivados de `Asignacion` vigente; se incorpora el permiso `equipos:asignar` al catálogo.

## Impact

- **Modelos/migraciones**: nuevos `backend/app/models/usuario.py` y `asignacion.py`; nuevo `backend/app/core/crypto.py` (`EncryptedString`); migración `007` (tablas `usuario` + `asignacion`, backfill de `users.roles` → `asignacion`, seed de `equipos:asignar` en `permiso`/`rol_permiso`). Una migración por cambio de schema (regla dura #15).
- **RBAC/auth (CRÍTICO, cross-cutting)**: `app/services/auth/token_service.py`, `app/api/dependencies/auth.py`, y un nuevo repositorio/servicio para resolver roles vigentes. Hay 216 tests de auth/RBAC que deben seguir verdes (safety net). `PermissionResolver` y `RolPermisoRepository` no cambian de firma.
- **Catálogo de permisos**: `app/core/permissions.py` suma `Perm.EQUIPOS_ASIGNAR`.
- **API**: nuevos routers/services/repositories/schemas para `usuarios` y `asignaciones` (flujo Routers→Services→Repositories→Models, regla dura #11).
- **Gobernanza**: dominio CRÍTICO (auth/RBAC/core-models). El cambio en la resolución de roles requiere aprobación humana explícita antes de escribir código (los pasos auth-touching de `tasks.md` están marcados como tales).
- **Docs**: corregir CHANGES.md (la migración de C-07 es la **007**, no la 005). PA-25 (semántica NEXO) sigue abierta pero no bloquea: `Asignacion.rol` acepta `NEXO` con el tratamiento "cero permisos" del seed de C-04.
