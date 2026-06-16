## Context

El módulo de comunicaciones cierra el flujo central del PROFESOR (importar → analizar → comunicar). Depende de C-11 (análisis de atrasados) que ya detecta qué alumnos están en riesgo. Ahora necesitamos un mecanismo para que docentes y coordinadores envíen notificaciones masivas con tracking de estado, preview obligatorio y aprobación configurable por tenant.

El sistema opera sobre PostgreSQL, con SQLAlchemy 2.0 async, y FastAPI. Ya existe un directorio `backend/workers/` con `__init__.py` vacío. No hay dependencias externas de mensajería aún — el worker será propio (asyncio) según el espíritu de ADR-003 (worker propio alcanza para MVP).

## Goals / Non-Goals

**Goals:**

- Modelar la entidad `Comunicacion` con su máquina de estados (Pendiente → Enviando → Enviado/Error/Cancelado)
- Implementar un worker asíncrono que consuma la cola y despache mensajes
- Proveer preview obligatorio antes de encolar cualquier envío (RN-16)
- Soportar envío masivo con cola (RN-15)
- Soportar aprobación humana configurable por tenant (RN-17): permiso `comunicacion:aprobar`, aprobación por lote o individual
- Soportar plantillas con variables de sustitución (`{alumno_nombre}`, `{materia}`, etc.)
- Exponer API REST `/api/v1/comunicaciones/*` con guard `comunicacion:enviar`
- Auditar con código `COMUNICACION_ENVIAR`
- Cifrar el destinatario (email) en reposo

**Non-Goals:**

- **No** implementar el envío real de emails (SMTP, SendGrid, etc.) — el worker definirá la interfaz de envío pero la implementación del transporter se hará vía configuración/integración posterior
- **No** incluir mensajería interna (inbox) — eso pertenece a C-20
- **No** incluir el tablón de avisos — eso pertenece a C-15
- **No** reemplazar ni modificar el módulo de análisis de atrasados (C-11)

## Decisions

### D1: Worker basado en asyncio (sin Celery/ARQ)

**Decisión**: El worker de comunicaciones será un loop asyncio que corre como proceso separado, usando la misma base de datos como cola (polling de registros Pendiente).

**Rationale**: Para el MVP, la carga estimada es baja (decenas a cientos de comunicaciones por día, no miles por minuto). Una cola basada en DB con polling periódico es suficiente y evita agregar Redis/RabbitMQ como dependencia. Si el volumen crece, se puede migrar a Celery+Redis sin cambiar el modelo de datos ni la interfaz del worker.

**Alternativa considerada**: Celery con Redis — descartado por sobreingeniería para MVP. ARQ — descartado porque agrega Redis como dependencia.

### D2: Máquina de estados en el modelo con validación explícita

**Decisión**: Los estados se validan en el Service (no en la DB) mediante un `StateMachine` helper que define transiciones válidas. Las transiciones inválidas lanzan `ValueError`.

**Rationale**: Tener la máquina de estados en código permite agregar lógica condicional por transición (ej: al pasar a Enviado, registrar `enviado_at`). La DB almacena el estado actual como string, sin constraints CHECK complejos.

**Alternativa considerada**: CHECK constraints en PostgreSQL — más seguras pero menos flexibles y difíciles de mantener con lógica condicional.

### D3: Implementación de plantillas con string.Template

**Decisión**: Usar `string.Template` de la stdlib para las plantillas con variables de sustitución. Las variables disponibles serán: `$alumno_nombre`, `$alumno_apellido`, `$materia`, `$docente_nombre`.

**Rationale**: Es parte de la stdlib, no agrega dependencias, y es suficientemente expresivo para las necesidades del MVP (sustitución simple). Si se necesita lógica condicional en plantillas, se puede migrar a Jinja2 más adelante.

### D4: Aprobación configurable por tenant como flag

**Decisión**: Se agrega un flag booleano `aprobacion_comunicaciones` en la configuración del tenant. Si está activo, las comunicaciones masivas quedan en Pendiente hasta que un usuario con permiso `comunicacion:aprobar` las apruebe (transición Pendiente → Enviando).

**Rationale**: La regla de negocio RN-17 requiere que sea configurable por tenant. Un flag en la tabla `Tenant` es la forma más simple y evita crear una tabla de configuración genérica prematura.

### D5: `comunicacion:aprobar` como permiso independiente

**Decisión**: Se crea un nuevo permiso `comunicacion:aprobar` independiente de `comunicacion:enviar`. Esto permite que un COORDINADOR pueda aprobar envíos sin necesariamente poder enviarlos él mismo, y viceversa.

**Rationale**: La matriz de permisos (C-04) ya soporta permisos finos `modulo:accion`. Sembrar este nuevo permiso es consistente con el diseño existente.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **R1**: DB como cola no escala a alto volumen | El polling es configurable (intervalo default 5s). Si el volumen crece, la interfaz del worker permite migrar a Celery+Redis sin cambiar el modelo `Comunicacion` |
| **R2**: El worker falla y los mensajes quedan "colgados" en Enviando | Timeout por mensaje: si un mensaje está en Enviando por más de 5 minutos, el worker lo reintenta (máx 3 intentos) y luego pasa a Error |
| **R3**: El cifrado del destinatario impide búsquedas | Se almacena el hash SHA-256 del destinatario en un campo `destinatario_hash` para búsquedas exactas, además del campo cifrado para visualización |
| **R4**: Aprobación lote/individual agrega complejidad UI | La API expone endpoints separados: `POST /{lote_id}/aprobar` (lote completo) y `POST /{id}/aprobar` (individual). El frontend decide cómo exponerlo |
