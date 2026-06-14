## Context

La identidad de auth ya existe (`users`, de C-02/C-03): `id`, `tenant_id`, `email`, `password_hash`, `display_name`, `is_active`, `roles` (ARRAY varchar tenant-global), `totp_secret`, `totp_enabled_at`, con mixins Base/Tenant/SoftDelete/Audit y unicidad parcial `(tenant_id, email)` sobre filas vivas. El RBAC fino existe (C-04): catálogo `rol`/`permiso`/`rol_permiso` sembrado por tenant en la migración 003, resuelto en runtime por `PermissionResolver.get_effective_permissions(tenant_id, role_codes)` → `RolPermisoRepository.find_permisos_for_roles`, cacheado por request. El claim `roles` se emite en `TokenService.create_access_token` desde `user.roles` y se lee en `get_current_user` hacia `CurrentUser.roles`, que es lo que consume `require_permission(...)`.

La KB pide dos entidades que aún no existen: `Usuario` (E4, perfil de persona con PII cifrada) y `Asignacion` (E5, Usuario↔Rol↔contexto con vigencia). Esto choca con dos puntos: (a) `users` ya es la identidad y tiene un `roles` plano; (b) no hay infraestructura de cifrado a nivel ORM (aunque sí existen primitivas AES-256-GCM en `app/core/security.py` y la `ENCRYPTION_KEY` ya está en `Settings`). Las dos preguntas de diseño se resolvieron en una sesión de exploración con el usuario (engram `opsx/c-07-usuarios-y-asignaciones/design-decisions`) y este documento las trata como restricciones cerradas.

Dominio CRÍTICO (auth/RBAC/core-models). Hay 216 tests de auth/RBAC que actúan como safety net y deben permanecer verdes. El cambio en la fuente de los roles requiere aprobación humana explícita antes de escribir código.

## Goals / Non-Goals

**Goals:**
- Introducir el perfil `Usuario` (E4) como tabla nueva 1:1 con `users`, con PII (`dni`, `cuil`, `cbu`, `alias_cbu`) cifrada AES-256 at-rest y nunca expuesta en logs/responses.
- Introducir `Asignacion` (E5) con rol, contexto académico, jerarquía `responsable_id` y vigencia temporal; `estado_vigencia` derivado por fechas (no almacenado).
- Convertir a `Asignacion` vigente en la fuente de verdad de los roles efectivos, alimentando el JWT y `CurrentUser` sin cambiar la firma de `PermissionResolver`.
- ABM `/api/admin/usuarios` (gate `usuarios:gestionar`) y CRUD `/api/asignaciones` (gate nuevo `equipos:asignar`), con soft-delete y conservación histórica.
- Migración 007 idempotente con backfill de `users.roles` → `asignacion`, y seed del permiso `equipos:asignar`.

**Non-Goals:**
- Acotar permisos por contexto (materia/carrera/cohorte/dictado). En C-07 el RBAC sigue siendo **tenant-global** vía el catálogo `rol_permiso`. El contexto de `Asignacion` se persiste pero solo sirve a features de equipos (F4.2–F4.5), que son de un change futuro.
- Resolver PA-25 (semántica del rol NEXO). `Asignacion.rol` acepta `NEXO` con "cero permisos" igual que el seed de C-04.
- Resolver PA-22/PA-23 (liquidaciones / claves de Plus): fuera de alcance.
- Eliminar la tabla `users` o fusionar identidad y perfil. `users` queda solo auth.
- Construir cifrado AES desde cero: se reutilizan las primitivas existentes en `app/core/security.py`.

## Decisions

### D1 — `Usuario` (E4) es una tabla NUEVA `usuario`, FK 1:1 a `users.id` (no se extiende `users`)
`users` permanece solo-auth (sin columnas PII nuevas). Nueva tabla `usuario`:

| columna | tipo | notas |
|---|---|---|
| `id` | UUID PK | BaseMixin |
| `tenant_id` | UUID FK→tenant | TenantMixin (redundante con `users.tenant_id`, necesario para scoping por defecto en repos — regla dura #9) |
| `user_id` | UUID FK→users.id | UNIQUE, `ondelete=CASCADE` — el vínculo 1:1 |
| `nombre` | String | texto plano |
| `apellidos` | String | texto plano |
| `dni` | `EncryptedString` | **cifrado AES-256** |
| `cuil` | `EncryptedString` | **cifrado AES-256** |
| `cbu` | `EncryptedString` | **cifrado AES-256** |
| `alias_cbu` | `EncryptedString` | **cifrado AES-256** |
| `banco` | String nullable | texto plano |
| `regional` | String nullable | texto plano |
| `legajo` | String nullable | atributo de negocio, NO PK, NO credencial (regla dura #14) |
| `legajo_profesional` | String nullable | atributo de negocio opcional |
| `facturador` | Boolean | default false |
| `estado` | String(20) | enum Activo|Inactivo, default Activo |
| + SoftDeleteMixin + AuditMixin | | igual que los modelos de dominio |

`email` de E4 NO se duplica: vive solo en `users.email` (ya es la clave `(tenant_id, email)` de login). Así se evita cifrar el email y resolver lookups sobre ciphertext.

**Alternativa descartada (Opción A — agregar PII a `users`)**: mezcla preocupaciones auth y negocio en una sola tabla, contamina la tabla más sensible del sistema con PII y complica el modelo de auth ya estable. Descartada por separación de responsabilidades.

### D2 — Infraestructura de cifrado: `EncryptedString` (TypeDecorator) sobre primitivas existentes
Nuevo `app/core/crypto.py` con un `TypeDecorator` de SQLAlchemy `EncryptedString` que:
- En `process_bind_param` (escritura): cifra con `encrypt_value(plaintext, key)` (AES-256-GCM, nonce aleatorio por valor, ya implementado en `app/core/security.py`).
- En `process_result_value` (lectura): descifra con `decrypt_value(ciphertext_b64, key)`.
- Obtiene la clave vía `get_encryption_key()` (lee `Settings.encryption_key` / `ENCRYPTION_KEY`, ya validada como 64 hex / 32 bytes).
- El tipo de columna subyacente es `String`/`Text` (almacena base64 del `nonce+ciphertext`).

**Descubrimiento clave**: las primitivas AES-256-GCM y la `ENCRYPTION_KEY` YA existen; C-07 solo agrega el wrapper ORM. Esto reduce el riesgo de criptografía hecha a mano.

**Alternativa descartada (cifrar/descifrar manual en cada Service)**: disperso, propenso a olvidos (PII en texto plano por un camino no cubierto). El `TypeDecorator` cifra de forma transversal e invisible a la capa de negocio.

PII nunca en logs/responses: los schemas Pydantic de respuesta NO incluyen `dni`/`cuil`/`cbu`/`alias_cbu` salvo en endpoints que lo requieran explícitamente y con permiso; los logs estructurados no serializan el modelo `Usuario` completo.

### D3 — `Asignacion` (E5) es la fuente de verdad de los roles, reemplazando `users.roles`
Nueva tabla `asignacion`:

| columna | tipo | notas |
|---|---|---|
| `id` | UUID PK | BaseMixin |
| `tenant_id` | UUID FK→tenant | TenantMixin |
| `usuario_id` | UUID FK→usuario.id | `ondelete=CASCADE` |
| `rol` | String(50) | enum: PROFESOR|TUTOR|COORDINADOR|NEXO|ADMIN|FINANZAS|ALUMNO (acepta los 7 códigos sembrados en C-04) |
| `dictado_id` | UUID FK→dictado.id nullable | contexto raíz (ADR-006); el docstring de `Dictado` ya anticipa este re-anclaje |
| `materia_id` | UUID FK→materia.id nullable | contexto (nullable = rol de tenant global) |
| `carrera_id` | UUID FK→carrera.id nullable | contexto |
| `cohorte_id` | UUID FK→cohorte.id nullable | contexto |
| `comisiones` | ARRAY(VARCHAR) | lista de comisiones, default `{}` |
| `responsable_id` | UUID FK→usuario.id nullable | jerarquía docente (a quién rinde cuentas) |
| `desde` | Date | inicio de vigencia |
| `hasta` | Date nullable | fin de vigencia (NULL = abierta) |
| + SoftDeleteMixin + AuditMixin | | soft-delete siempre (regla dura #13) |

`estado_vigencia` (Vigente|Vencida) es **derivado, NO almacenado**: `Vigente` ⇔ `desde <= hoy AND (hasta IS NULL OR hoy <= hasta)`. Se calcula en el Service/repository, no es columna.

Roles efectivos de un usuario = `DISTINCT asignacion.rol` donde la asignación está viva (`deleted_at IS NULL`) y vigente, para ese `usuario_id` + `tenant_id`. Un nuevo `AsignacionRepository.find_roles_vigentes(tenant_id, usuario_id)` provee esa lista; alimenta:
- `TokenService.create_access_token`: el claim `roles` se computa desde asignaciones vigentes en lugar de `user.roles`.
- `get_current_user` / `CurrentUser.roles`: misma fuente (lee el claim del JWT, que ya viene derivado).

`PermissionResolver.get_effective_permissions(tenant_id, role_codes)` y `RolPermisoRepository` **no cambian de firma**: siguen recibiendo una lista de códigos de rol. El contexto de `Asignacion` NO acota la resolución de permisos en C-07.

**Decisión sobre `users.roles`**: se **deprecia, no se elimina** en esta migración. Queda como columna pero deja de leerse en runtime (la fuente pasa a `asignacion`). Mantenerla evita una migración destructiva sobre la tabla de auth y permite rollback; un change futuro puede dropearla una vez confirmado que nada la lee. (Alternativa: dropearla ya — descartada por riesgo sobre la tabla CRÍTICA de auth y para conservar el dato durante la transición.)

### D4 — Migración 007 con backfill y seed
`backend/alembic/versions/007_create_usuario_asignacion.py`, `revision = "a7b8c9d0e1f2"`, `down_revision = "f6a7b8c9d0e1"` (cabeza actual: 006). Una sola migración por el cambio de schema (regla dura #15). `upgrade()`:
1. `create_table("usuario", ...)` + índice único parcial `(tenant_id, user_id)` sobre filas vivas.
2. `create_table("asignacion", ...)` + índices: `(tenant_id, usuario_id)` y `(tenant_id, rol)` para resolución de roles.
3. Seed del permiso `equipos:asignar` (módulo `equipos`) por cada tenant vivo, replicando el loop de seed de la migración 003 (`INSERT ... ON CONFLICT DO NOTHING`), y `rol_permiso` para COORDINADOR y ADMIN (es_propio=False).
4. **Backfill**: por cada `users` vivo y cada `users.roles[i]`, crear una fila `usuario` mínima (si no existe) y una `asignacion` con ese `rol`, contexto NULL, `desde = users.created_at::date`, `hasta = NULL`. (El backfill de `usuario` crea el shell de perfil; los campos PII quedan vacíos hasta que se completen vía el ABM.)

`downgrade()`: borra el seed de `equipos:asignar` (rol_permiso → permiso), dropea `asignacion` y luego `usuario`. (El backfill no se revierte a `users.roles` porque la columna nunca se borró.)

### D5 — Permiso `equipos:asignar` y gates de endpoints
- `app/core/permissions.py`: agregar `Perm.EQUIPOS_ASIGNAR = "equipos:asignar"`.
- ABM `/api/admin/usuarios`: gate `require_permission(Perm.USUARIOS_GESTIONAR)` (ya existe en el catálogo, rol ADMIN). Flujo Routers→Services→Repositories→Models (regla dura #11). Fail-closed (regla dura #10).
- CRUD `/api/asignaciones`: gate `require_permission(Perm.EQUIPOS_ASIGNAR)`.
- Identidad y tenant SIEMPRE desde el JWT verificado (regla dura #8); repos filtran por tenant por defecto (regla dura #9).

## Risks / Trade-offs

- **[Cross-cutting auth — romper los 216 tests de RBAC]** → El cambio de fuente de roles toca `TokenService` y `get_current_user`. Mitigación: capturar baseline (correr la suite y registrar "N passing") ANTES de tocar; los pasos auth-touching de `tasks.md` están marcados como CRÍTICO con revisión humana previa; el backfill garantiza que todo usuario existente tenga asignaciones equivalentes a su `users.roles` actual, de modo que los roles efectivos no cambien tras migrar.
- **[Backfill incompleto o no idempotente]** → si la migración corre dos veces o sobre data parcial, podrían duplicarse asignaciones. Mitigación: `ON CONFLICT DO NOTHING` con índices únicos apropiados y test de up/down limpio contra la DB de test.
- **[PII filtrada por un camino no cubierto]** → un endpoint o log nuevo podría serializar el modelo completo. Mitigación: cifrado transversal vía `TypeDecorator` (no hay texto plano at-rest), schemas de respuesta que omiten PII por defecto, y un test que verifica ciphertext at-rest y ausencia de PII en respuestas/logs.
- **[`estado_vigencia` derivado vs. consultas]** → al no almacenarse, cada resolución de roles filtra por fechas. Mitigación: índice `(tenant_id, usuario_id)` en `asignacion`; el volumen por usuario es bajo. Acotar permisos por contexto queda fuera de alcance, lo que evita joins caros en el hot path de auth.
- **[`legajo` confundido con credencial]** → riesgo de que alguien lo use como selector de sesión. Mitigación: `legajo` es nullable, no único forzoso como credencial, y la identidad sigue siendo el UUID interno (regla dura #14); explícito en spec.

## Migration Plan

1. Crear `app/core/crypto.py` (`EncryptedString`) sobre las primitivas existentes.
2. Crear modelos `usuario` y `asignacion`; registrarlos en `app/models/__init__.py`.
3. Escribir migración 007 (tablas + índices + seed `equipos:asignar` + backfill); test up/down limpio.
4. Agregar `Perm.EQUIPOS_ASIGNAR`.
5. Cambiar la fuente de roles (CRÍTICO, con aprobación): `AsignacionRepository.find_roles_vigentes`, luego `TokenService` y `get_current_user`. Re-correr el safety net.
6. Repositories/Services/Routers/Schemas para `usuarios` y `asignaciones`.
7. Corregir CHANGES.md (migración 007, no 005) y marcar C-07.

**Rollback**: `alembic downgrade -1` revierte la migración 007 (dropea `asignacion`/`usuario` y el seed). Como `users.roles` no se borra, el runtime puede volver a leer la columna si se revierte el código del paso 5.

## Open Questions

- **PA-25 (semántica NEXO)**: sigue abierta; NO bloquea C-07 (NEXO = cero permisos por el seed de C-04). A confirmar en un change futuro.
- **Drop de `users.roles`**: queda deprecada en C-07; cuándo dropearla definitivamente es decisión de un change posterior una vez verificado que nada la lee.
- **`api-security-best-practices` skill** no está instalada localmente (CLAUDE.md la lista como pendiente). Sería el skill natural para revisar la capa de cifrado/PII en apply. Gap a resolver antes de implementar la parte de seguridad.
