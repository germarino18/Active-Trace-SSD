## Context

El sistema ya cuenta con:
- `Usuario` model (E4) con todos los campos de perfil: nombre, apellidos, dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, estado. PII cifrada con AES-256.
- `User` model (auth) con `email` (no duplicado en `Usuario`).
- `CurrentUser` dependency con `user_id`, `tenant_id`, `roles`, `actor_id` (usuario.id).
- Endpoint `/api/auth/logout` operativo desde C-03.
- Permisos vía `require_permission()` con fail-closed 403.

Lo que NO existe:
- Endpoints públicos para que el usuario vea/edite su propio perfil.
- Modelos de mensajería interna entre usuarios del sistema.
- Permiso `inbox:acceder`.

## Goals / Non-Goals

**Goals:**
- Que cualquier usuario autenticado pueda ver y editar su perfil (GET/PATCH `/api/v1/perfil`).
- Que cualquier usuario autenticado pueda usar una bandeja de mensajes interna: ver hilos, leer mensajes, responder.
- Que el logout existente quede accesible desde el contexto del perfil (documentación, sin cambios de código).
- Cobertura de tests ≥80% líneas, ≥90% reglas de negocio.

**Non-Goals:**
- NO se implementa creación de nuevos hilos (solo respuesta en hilos existentes). Los hilos los origina el sistema (notificaciones) u otros usuarios — eso queda para un change futuro.
- NO se implementan grupos de destinatarios ni mensajes masivos internos.
- NO se implementa notificaciones push/email al recibir un mensaje interno (solo la bandeja).
- NO se implementa adjuntos en mensajes.

## Decisions

### Decisión 1: Perfil reusa modelo Usuario existente
- **Opción A (elegida)**: GET/PATCH `/api/v1/perfil` opera directamente sobre la tabla `usuario` existente. Para el `email`, se hace un JOIN con `users` o una query separada en el servicio. El PATCH rechaza explícitamente `cuil` mediante validación en el schema Pydantic (`extra='forbid'` + campos permitidos explícitos).
- **Opción B**: Crear una vista/materialized view separada. → Descartado: el modelo Usuario ya tiene todo lo necesario, una vista agrega complejidad innecesaria.

### Decisión 2: Modelo de mensajería con HiloParticipante explícito
- **Opción A (elegida)**: Tabla `HiloParticipante` con `(hilo_id, usuario_id)` como PK compuesta y campo `ultima_visto`. Esto permite determinar `no_leido` comparando `ultima_visto` con la fecha del último mensaje.
- **Opción B**: Array de participantes en `HiloConversacion`. → Descartado: dificulta consultar "mis hilos" y trackear lectura por participante.
- **Opción C**: Sin tabla de participantes, derivar de los mensajes. → Descartado: un hilo puede existir antes del primer mensaje, y no tendríamos forma de saber quiénes son participantes sin recorrer mensajes.

### Decisión 3: inbox:acceder como permiso granular
- **Opción A (elegida)**: Nuevo permiso `inbox:acceder` asignado a todos los roles por defecto. Gatea todos los endpoints `/api/v1/inbox/*`.
- **Opción B**: Sin permiso, solo verificar autenticación. → Descartado: consistencia con el resto del sistema donde todos los recursos protegidos pasan por `require_permission()`. Si en el futuro se quiere restringir, el permiso ya está modelado.

### Decisión 4: Logout reusa endpoint existente de C-03
- El endpoint `POST /api/auth/logout` ya está implementado en `auth.py`. Recibe el `refresh_token` en el body, lo revoca, y responde 200. No se crea un nuevo endpoint; se documenta en la API como parte del perfil. El frontend lo consumirá desde el menú de perfil.

### Decisión 5: El mensaje "no_leido" se deriva, no se almacena como flag
- `HiloParticipante.ultima_visto` almacena el timestamp de la última vez que el participante vio el hilo. `no_leido` se computa como `ultima_visto IS NULL OR ultima_visto < (SELECT MAX(fecha_hora) FROM mensaje WHERE hilo_id = X AND remitente_id != <participante>)`. Esto evita inconsistencias de estado.

### Decisión 6: 404 en lugar de 403 para hilos no pertenecientes
- Cuando un usuario intenta acceder a un hilo en el que no es participante, se devuelve 404 (no 403) para no revelar la existencia del hilo (information disclosure). Consistente con el patrón usado en otros módulos del sistema.

## Data Model

### Nuevas tablas

```sql
CREATE TABLE hilo_conversacion (
    id              UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    asunto          VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ  -- soft delete
);

CREATE TABLE hilo_participante (
    hilo_id         UUID NOT NULL REFERENCES hilo_conversacion(id),
    usuario_id      UUID NOT NULL REFERENCES usuario(id),
    ultima_visto    TIMESTAMPTZ,  -- nullable = nunca visto
    PRIMARY KEY (hilo_id, usuario_id)
);

CREATE TABLE mensaje (
    id              UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    hilo_id         UUID NOT NULL REFERENCES hilo_conversacion(id),
    remitente_id    UUID NOT NULL REFERENCES usuario(id),
    contenido       TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ  -- soft delete
);

CREATE INDEX ix_mensaje_hilo_created ON mensaje(hilo_id, created_at);
CREATE INDEX ix_hilo_participante_usuario ON hilo_participante(usuario_id);
```

### Mixins
- `HiloConversacion` y `Mensaje` usan: `BaseMixin`, `TenantMixin`, `SoftDeleteMixin`, `AuditMixin`.
- `HiloParticipante` usa solo columnas básicas (no hereda mixins — PK compuesta natural).

## API Endpoints

| Method | Path | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/v1/perfil` | JWT | Perfil propio |
| PATCH | `/api/v1/perfil` | JWT | Editar perfil propio |
| GET | `/api/v1/inbox/hilos` | JWT + `inbox:acceder` | Hilos del usuario |
| GET | `/api/v1/inbox/hilos/{id}` | JWT + `inbox:acceder` | Mensajes de un hilo |
| POST | `/api/v1/inbox/hilos/{id}/responder` | JWT + `inbox:acceder` | Responder en un hilo |

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| [R1] PII en perfil propio — el PATCH expone datos sensibles en request/response | Todos los endpoints usan HTTPS. Los campos PII viajan desencriptados solo en la respuesta al dueño del perfil. |
| [R2] "no_leido" computado puede ser lento con muchos mensajes | El cómputo es un `MAX(fecha_hora)` sobre mensajes del hilo (con índice), que es O(1) por hilo en la práctica. Si escala, se puede cachear en `HiloConversacion.ultimo_mensaje_at`. |
| [R3] 404 vs 403 en hilos no pertenecientes — el atacante puede inferir existencia por timing | Los 404 se devuelven con el mismo timing independientemente de si el hilo existe o no, y siempre tras verificar tenencia. |

## Open Questions

- (ninguna — decisions cerradas en este diseño)
