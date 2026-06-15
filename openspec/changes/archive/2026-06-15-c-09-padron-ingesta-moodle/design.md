## Context

Activia-Trace necesita un módulo de Padrón para gestionar alumnos inscriptos por dictado. El módulo debe soportar importación desde Moodle Web Services con fallback manual `.xlsx`/`.csv`, versionado con trazabilidad histórica, y operación de vaciado scope-isolated por `(usuario_id × dictado_id)` (RN-04).

Actualmente el sistema tiene:
- Modelos de estructura académica (C-06) con `Dictado` como entidad raíz que vincula materia × carrera × cohorte
- Modelo `Usuario` con perfil de negocio, PII cifrado AES-256
- Sistema de auditoría append-only con action codes estandarizados
- RBAC con permisos `modulo:accion`
- Moodle WS mencionado en la arquitectura pero sin implementación cliente

## Goals / Non-Goals

**Goals:**
- Modelar `VersionPadron` y `EntradaPadron` con versionado: una versión activa por dictado
- Importación de padrón desde `.xlsx`/`.csv` con preview previa y upsert destructivo
- Integración Moodle WS para sync de usuarios/actividades (nocturna + on-demand)
- Operación de vaciado de datos scope-isolated (RN-04)
- Cifrado AES-256 del email en EntradaPadron
- Auditoría `PADRON_CARGAR` y `PADRON_VACIAR`
- Aislamiento multi-tenant (tenant_id en ambas tablas)

**Non-Goals:**
- Importación de calificaciones desde Moodle (es C-10)
- Sincronización bidireccional (solo pull desde Moodle)
- Interfaz de frontend para el módulo (se hará en change de frontend correspondiente)
- Gestión de grupos/comisiones más allá de la columna `comision`
- Módulo de liquidaciones (C-18, bloqueado por PA-22/PA-23)

## Decisions

### D1 — dictado_id en VersionPadron en lugar de (materia_id, cohorte_id)

Siguiendo ADR-006 (re-anclaje de entidades downstream a Dictado), `VersionPadron` referencia a `dictado_id` en lugar del par `(materia_id, cohorte_id)`. Esto alinea el modelo con el resto de entidades (Asignacion, Encuentro, etc.) y simplifica las queries: para obtener el padrón de un dictado se filtra por `dictado_id` directo, sin JOIN intermedio.

**Alternativa considerada**: mantener `(materia_id, cohorte_id)` como estaba en el ERD original. Se descarta para mantener consistencia con ADR-006 y con la migración de C-06 que ya re-ancló todas las entidades downstream a `dictado_id`.

### D2 — RN-05 (upsert destructivo) reconciliado con el modelo versionado

RN-05 dice "reemplaza COMPLETAMENTE el anterior de esa materia". El modelo E6 dice "se conserva historial de versiones". Se reconcilian así:

- Una importación crea una **nueva** `VersionPadron` con `activa=true`
- La versión anterior del mismo `dictado_id` pasa a `activa=false` (se desactiva, no se borra)
- A nivel aplicación se comporta como "reemplazo": las queries DEBEN filtrar por `activa=true` exclusivamente
- El historial queda disponible para trazabilidad/auditoría

**Alternativa considerada**: hard-delete de la versión anterior + sus entradas. Se descarta porque viola el principio de auditoría append-only (regla dura 13).

### D3 — EntradaPadron.email cifrado AES-256

El email del alumno en `EntradaPadron` se almacena cifrado con AES-256, reutilizando el mismo `EncryptedString` type que se usa en `Usuario.dni`/`cuil`/`cbu`. Esto es PII y está sujeto a la regla dura 12.

**Alternativa considerada**: no cifrar el email porque ya existe en `users.email`. Pero como `EntradaPadron` es una snapshot desnormalizada para histórico, y puede contener emails de alumnos que aún no tienen cuenta, debe protegerse.

### D4 — Permisos RBAC del módulo Padrón

Tres permisos nuevos con naming `modulo:accion`:

| Permiso | Acción |
|---------|--------|
| `padron:importar` | Importar padrón (PROFESOR para sus materias, COORDINADOR global) |
| `padron:vaciar` | Vaciar datos de materia (scope usuario_id × dictado_id) |
| `padron:ver` | Visualizar padrón de un dictado |

**Alternativa considerada**: permisos planos como `PADRON_IMPORTAR` sin prefijo. Se descarta porque el resto del sistema ya usa `modulo:accion` y la consistencia es requisito.

### D5 — Route prefix y estructura del router

- Prefix: `/api/admin/padron`
- Guard base: `require_permission(Perm.PADRON_VER)` en el router (los endpoints específicos exigen su propio permiso más restrictivo)
- Endpoints:
  - `POST /api/admin/padron/preview` — previsualizar archivo (sin persistir)
  - `POST /api/admin/padron/importar` — importar y activar nueva versión
  - `POST /api/admin/padron/dictados/{dictado_id}/vaciar` — vaciar datos
  - `GET /api/admin/padron/dictados/{dictado_id}` — obtener padrón activo
  - `GET /api/admin/padron/versiones` — historial de versiones
  - `POST /api/admin/padron/sync/moodle` — sync on-demand desde Moodle

### D6 — Import en dos pasos (preview + confirm)

Para la importación manual (F1.3), se usa un flujo de dos pasos:
1. **Preview**: el usuario sube el archivo, el sistema parsea las filas, valida estructura de columnas, devuelve un resumen (N filas, columnas detectadas, errores de parseo). NO persiste nada.
2. **Confirm**: el usuario envía un token del preview, el sistema crea la nueva `VersionPadron` con sus `EntradaPadron`, desactiva la versión anterior.

**Alternativa considerada**: import directo en un solo paso. Se descarta porque la preview es requisito explícito (F1.3) y reduce errores de carga.

### D7 — Moodle WS Client pattern

El cliente Moodle WS se implementa como clase `MoodleClient` en `integrations/moodle_ws.py` que:
- Se configura por tenant (URL base + token, almacenados cifrados en DB de config)
- Expone métodos: `sync_usuarios(dictado_id)`, `sync_actividades(dictado_id)`
- Errores de conexión/autenticación mapean a `502` HTTP con metadatos de reintento
- Usa `httpx.AsyncClient` con timeout configurable
- La sync nocturna se dispara via un worker background (misma cola de comunicaciones)

### D8 — Vaciado scope-isolated (RN-04)

La operación de vaciado elimina ÚNICAMENTE los datos del usuario que la ejecuta en esa materia:
- Para PROFESOR: solo sus propios datos (verificado contra tablas de equipo docente)
- Para COORDINADOR: puede vaciar cualquier dictado de su tenant
- Scope: `(usuario_id × dictado_id)`, verificado contra la asignación del usuario al dictado
- Se registra `PADRON_VACIAR` en audit log con `filas_afectadas`

## Risks / Trade-offs

- **R1 — Consistencia del preview**: entre el preview y el confirm, otro usuario podría importar un padrón. El confirm debe verificar que no haya una versión más nueva que la del preview.
  - **Mitigación**: el preview devuelve un hash del estado actual; el confirm lo verifica y rechaza si cambió.
- **R2 — Moodle WS caído**: la dependencia externa impacta en disponibilidad.
  - **Mitigación**: cache de última sync exitosa, cola de reintentos, fallback manual por archivos.
- **R3 — Cifrado de email en consultas**: el email cifrado no se puede filtrar por búsqueda de texto.
  - **Mitigación**: se busca por `nombre + apellidos` o UUID; el email solo se muestra desencriptado en respuestas individuales autorizadas.
- **R4 — Versión activa huérfana**: si falla la creación de entradas después de crear la versión, puede quedar una versión activa sin entradas.
  - **Mitigación**: usar transacción; si falla cualquier paso, rollback completo.
