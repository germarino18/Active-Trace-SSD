## Context

C-01 dejó el esqueleto ejecutable: FastAPI arranca, responde `/health`, conecta a PostgreSQL async y tiene logging estructurado + OTel. Pero no hay **una línea de modelo de datos ni de lógica de dominio**. Los directorios `models/`, `schemas/`, `repositories/`, `services/` están vacíos. Los slots `core/tenancy.py`, `core/security.py`, `core/exceptions.py` son placeholders con docstring.

C-02 es el change que **materializa la capa de datos fundacional**. Sin él ningún modelo de negocio puede existir: ni usuarios, ni alumnos, ni materias, ni comunicaciones. Todo en activia-trace cuelga de un tenant — por eso arrancamos por `Tenant`, los mixins compartidos y el repositorio genérico que aplica row-level tenancy automáticamente.

La restricción clave: esto es multi-tenant desde el día 0. Cada query, cada inserción, cada soft delete debe respetar el tenant. El repositorio no confía en que el service recuerde filtrar — el filtro es automático e implícito.

## Goals / Non-Goals

**Goals:**

- Modelo `Tenant` completo: UUID PK, slug único (identificador de negocio para el tenant), settings JSONB, is_active, timestamps auditables, soft delete.
- Mixins reutilizables (`BaseMixin`, `TenantMixin`, `SoftDeleteMixin`, `AuditMixin`) que cualquier modelo futuro extiende.
- `BaseRepository[T]` genérico con CRUD async, filtro automático de tenant, soft-delete aware.
- `TenantContext` via `contextvars` para propagar tenant_id a través de la cadena request sin acoplar a FastAPI.
- Dependencia FastAPI `get_tenant_id()` que resuelve desde request header/session (placeholder hasta C-03).
- AES-256-GCM para cifrar PII en reposo (CBU, DNI, secretos).
- Jerarquía de excepciones con handlers globales que devuelven JSON estandarizado.
- Migración Alembic 001: tabla `tenant` con índices, constraints.
- Tests con PostgreSQL real cubriendo CRUD, aislamiento, soft delete, encryption.

**Non-Goals:**

- Modelos de negocio (User, Alumno, Materia, etc.) → C-03/C-06 en adelante.
- JWT, autenticación, hashing de passwords → C-03.
- RBAC, matriz de permisos, `require_permission` → C-04.
- Auditoría de cambios (audit log) → C-05.
- Endpoints REST de tenant (CRUD expuesto) → change futuro de administración.
- Encadenamiento de migraciones de datos (seed/migrate) → cuando haya datos reales.

## Decisions

### D1 — `contextvars` para propagación de tenant (no `request.state`)

La tenancy NO depende de que exista un objeto `Request` de FastAPI. Los servicios se llaman desde workers, tests, scripts y potencialmente desde la cola de comunicaciones. Usar `request.state` acoplaría la propagación a un contexto HTTP que no siempre existe.

**Solución**: `contextvars.TenantContext` usando `ContextVar[UUID | None]`. Se setea en un middleware FastAPI (cuando hay request HTTP) y se lee desde `get_tenant_id()`. Para workers/scripts se setea manualmente con `TenantContext.set(tenant_id)`.

```python
_tenant_ctx: ContextVar[uuid.UUID | None] = ContextVar("tenant_id", default=None)

class TenantContext:
    @staticmethod
    def get() -> uuid.UUID | None:
        return _tenant_ctx.get()

    @staticmethod
    def set(tenant_id: uuid.UUID) -> None:
        _tenant_ctx.set(tenant_id)

    @staticmethod
    def reset() -> None:
        _tenant_ctx.set(None)
```

**Alternativa descartada**: `request.state` via middleware — solo funciona en endpoints HTTP, no en workers ni tests. **Alternativa descartada**: parámetro explícito en cada método del repositorio — el usuario pide filtro automático, no manual.

### D2 — Repository genérico con TypeVar bound a `Base`

```python
T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None):
        self.session = session
        self._tenant_id = tenant_id
```

Cada método que toca datos aplica `_apply_tenant_scope(query)` automáticamente. El `tenant_id` se obtiene por inyección en el constructor o desde `TenantContext.get()` si no se pasa explícitamente.

**Alternativa descartada**: pasar tenant_id en cada llamada — verboso, propenso a errores humanos, viola el requerimiento de filtro automático.

### D3 — Soft delete con `deleted_at` nullable (no flag booleano)

Usar `deleted_at: DateTime | None` en lugar de `is_deleted: bool`. Ventajas:
- Permite saber CUÁNDO se eliminó (auditoría nativa).
- Facilita la recuperación con el valor exacto para restaurar.
- Se puede implementar un `cleanup` por antigüedad.
- El repositorio excluye `WHERE deleted_at IS NULL` por defecto, con método `include_deleted()` para consultas explícitas.

**Alternativa descartada**: flag booleano — pierde información temporal, no auditable.

### D4 — AES-256-GCM con nonce aleatorio y datos asociados

El módulo `core/security.py` implementa:

```python
def encrypt_value(plaintext: str, key: bytes) -> str:
    nonce = os.urandom(12)  # GCM nonce de 96 bits
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(nonce + encryptor.tag + ciphertext).decode()

def decrypt_value(ciphertext_b64: str, key: bytes) -> str:
    raw = base64.b64decode(ciphertext_b64)
    nonce, tag, ciphertext = raw[:12], raw[12:28], raw[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
```

Formato: `base64(nonce(12) + tag(16) + ciphertext)` — todo en una sola string transportable.

**Alternativa descartada**: AES-CBC — requiere padding manual, no tiene autenticación integrada (susceptible a padding oracle attacks). GCM provee autenticación + cifrado en un solo paso.

### D5 — Jerarquía de excepciones con herencia plana

```
AppException (base, HTTP 500)
├── NotFoundException (HTTP 404)
├── ForbiddenException (HTTP 403)
├── TenantMismatchException (HTTP 403)
├── ValidationException (HTTP 422)
└── UnauthorizedException (HTTP 401) — reservado para C-03
```

Cada excepción lleva `message: str`, `code: str` y `details: dict | None`. El handler global captura `AppException` y produce:
```json
{"error": {"code": "not_found", "message": "...", "details": null}}
```

**Alternativa descartada**: excepciones genéricas HTTPException de FastAPI — no hay tipado de dominio, no se puede diferenciar NotFound de un módulo vs otro en los handlers.

### D6 — Migración 001 con toda la tabla `tenant` completa

Una sola migración Alembic que crea:
```sql
CREATE TABLE tenant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    settings JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by_id UUID,
    updated_by_id UUID
);
CREATE UNIQUE INDEX ix_tenant_slug ON tenant(slug) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX ix_tenant_slug_deleted ON tenant(slug, deleted_at);
```

El `slug` es único entre activos (partial unique index), pero puede repetirse si está soft-deleteado (así se permite re-crear un tenant con el mismo slug después de eliminarlo).

**Alternativa descartada**: varias migraciones chicas por cada mixin — más ruido que valor. Una migración 001 consolidada es más legible y fácil de rollback.

### D7 — TDD estricto con PostgreSQL real

- Base de datos de test via service `postgres` en docker-compose con `DATABASE_URL_TEST`.
- Fixtures de pytest: `db_session` (sesión async aislada con rollback al final), `test_tenant` (crea un tenant de test), `another_tenant` (segundo tenant para test de aislamiento).
- Cada test es independiente: se ejecuta dentro de una transacción que se revierte al final (rollback, no truncate). Esto permite paralelismo y no contamina el estado entre tests.

## Risks / Trade-offs

- **[Repository genérico puede ser demasiado rígido si un modelo necesita queries muy específicas]** → Mitigación: `BaseRepository` ofrece `find_by()` con filtros arbitrarios; si no alcanza, el repositorio específico extiende la clase base con métodos adicionales. No se sacrifica flexibilidad.
- **[contextvars no se "limpia" automáticamente entre requests si falla el middleware]** → Mitigación: el middleware envuelve en try/finally con `TenantContext.reset()`. En workers, el loop principal hace reset antes de procesar cada mensaje.
- **[AES-256-GCM sin rotación de claves]** → Trade-off aceptado: la clave se deriva de `ENCRYPTION_KEY` (entorno). Rotación requiere recifrar todos los campos — eso es un change futuro, no bloquea C-02.
- **[UUID como PK tiene impacto de performance en índices vs autoincremental]** → Trade-off aceptado: las PKs UUID son más seguras (no exponen secuencia), mejor para multi-tenant (no hay colisión entre tenants), y PostgreSQL los maneja bien con `gen_random_uuid()`. Ver ADR-005.
- **[created_by_id/updated_by_id apuntan a User que aún no existe]** → Mitigación: las FK son `nullable=True` hasta C-03. La migración no declara la constraint FK aún (se agrega en C-03 cuando User exista). Sin esto, Alembic no podría aplicar la migración 001 por falta de la tabla `user`.
- **[Soft delete complica las unique constraints]** → Mitigación: partial unique indexes `WHERE deleted_at IS NULL` permiten unicidad solo entre registros activos. Para casos que requieren unicidad global, se usa un unique index compuesto con `deleted_at` (que siempre es NULL o un timestamp único).

## Migration Plan

- Aplicar migración 001: `alembic upgrade head` crea la tabla `tenant`.
- Rollback: `alembic downgrade -1` elimina la tabla.
- Los tests crean y destruyen su propia data en una transacción que hace rollback al final — no requieren migration ni afectan datos reales.
- No hay datos semilla en C-02 (el tenant se crea en el onboarding de cada institución, que es un change futuro).

## Open Questions

- **¿El slug debe ser generado automáticamente desde el name o ingresado manualmente?** Se decide en C-02 apply: mantener ambos campos y validar el formato del slug (lowercase, sin espacios, max 100 chars). El servicio de creación de tenant decide la lógica de generación.
- **¿Se expone un endpoint CRUD de tenant en C-02?** No — el modelo y repositorio existen, pero el router de administración de tenants se implementa en un change futuro (cuando exista el flujo de onboarding). C-02 solo construye la capa de datos.
- **¿Encryption key source exacta?** `ENCRYPTION_KEY` como hex string de 64 caracteres (32 bytes = 256 bits). Se deriva con `bytes.fromhex()` en el arranque. Validación: longitud exacta o error en startup.
