## Context

El sistema ya cuenta con un log de auditoría append-only (C-05) que captura toda acción significativa con actor, materia, código de acción, detalle JSON, IP y user-agent. También existe el módulo de comunicaciones (C-12) con estados trazables. Sin embargo, no hay endpoints que permitan consultar, agregar o filtrar estos datos — solo existen a nivel de base de datos.

C-19 agrega una **capa de consulta y agregación** sobre datos existentes (`AuditLog` y `Comunicacion`), sin modificar modelos ni tablas. Todo es solo lectura.

El permiso `auditoria:ver` ya existe seedeado desde C-04/C-05. Se requiere lógica de scope `(propio)` para COORDINADOR (solo ve acciones de su alcance vs ADMIN que ve todo).

## Goals / Non-Goals

**Goals:**

- Exponer endpoints REST de consulta sobre `AuditLog` con agregaciones diarias, por docente, por materia y por tipo de acción (F9.1)
- Exponer endpoint de log detallado de últimas acciones con límite configurable (default 200) y filtros combinados (F9.1)
- Exponer endpoint de log completo de auditoría con filtros: rango de fechas, materia, usuario, código de acción, paginación (F9.2)
- Exponer endpoint de estado de comunicaciones agrupado por docente (F9.1)
- Implementar guard `auditoria:ver` con scope `(propio)` para COORDINADOR
- Todas las consultas sobre `AuditLog` y `Comunicacion`, sin modificar su estructura

**Non-Goals:**

- **No** modificar el modelo `AuditLog` ni sus migraciones
- **No** agregar nuevos códigos de acción al catálogo (se usan los existentes)
- **No** modificar el modelo `Comunicacion` ni su máquina de estados
- **No** implementar UI/frontend — solo API REST
- **No** incluir exportación a PDF/CSV (puede agregarse después)

## Decisions

### D1: Agregaciones por consulta directa a DB (sin tablas de resumen)

**Decisión**: Las agregaciones (acciones por día, interacciones por docente×materia, etc.) se computan con consultas SQLAlchemy con `GROUP BY` y funciones de agregación directamente sobre `AuditLog`. No se crean tablas de resumen ni caché.

**Rationale**: El volumen de auditoría del MVP es perfectamente manejable para consultas agregadas directas (miles de registros, no millones). Crear tablas de resumen agregaría complejidad y riesgo de desincronización sin beneficio real. Si el volumen crece, se puede introducir una capa de materialización (vistas materializadas o tabla de resumen con refresh periódico).

**Alternativa considerada**: Tabla `audit_resumen_diario` con upsert diario — descartada por sobreingeniería para el volumen esperado.

### D2: Scope `(propio)` resuelto vía asignaciones del COORDINADOR

**Decisión**: El scope `(propio)` para COORDINADOR se implementa filtrando los `actor_id` de los registros de auditoría contra los `user_id` de las asignaciones donde el COORDINADOR tiene rol de supervisión (materias/carreras donde está asignado). Si el usuario tiene `ADMIN` o `FINANZAS`, no hay filtro de scope.

**Rationale**: Ya existe el modelo `Asignacion` (C-07) con la relación jerárquica. Reusar ese modelo evita crear una tabla de permisos adicional. La consulta cruza `AuditLog.actor_id` con las asignaciones del COORDINADOR para determinar qué registros puede ver.

**Alternativa considerada**: Flag `es_global` en el permiso — descartado porque el scope `(propio)` no es binario, depende del contexto académico del usuario.

### D3: Límite configurable vía query param con max enforce

**Decisión**: El endpoint de últimas acciones acepta un query param `limit` (default 200) con un máximo absoluto de 1000 para evitar abusos. Si se envía un valor mayor a 1000, se trunca silenciosamente a 1000.

**Rationale**: La funcionalidad F9.1 pide un máximo configurable con default 200. Poner un hard-limit de 1000 protege contra consultas maliciosas o accidentales que podrían impactar performance.

### D4: Filtro de "estado de actividad" como atributo derivado

**Decisión**: El filtro de "estado de actividad" (activo/inactivo) mencionado en F9.1/F9.2 no se aplica directamente sobre `AuditLog` (que no tiene ese campo) sino que se resuelve consultando si el `actor_id` tiene asignaciones vigentes en el período. Un usuario sin asignaciones vigentes se considera "inactivo".

**Rationale**: El estado de actividad es una propiedad del usuario en relación a sus asignaciones, no un atributo del registro de auditoría. Derivarlo desde `Asignacion` es semánticamente correcto y evita denormalizar datos.

## Risks / Trade-offs

- **[Performance] Consultas agregadas sobre `AuditLog` sin índices específicos**: `AuditLog` tiene índices por `tenant_id` y `fecha_hora`. Las agregaciones por `actor_id` o `materia_id` pueden requerir índices adicionales. → **Mitigación**: Revisar el plan de consultas y agregar índices compuestos si es necesario (ej: `(tenant_id, actor_id, fecha_hora)` para agregaciones por docente).
- **[Scope] La resolución de scope `(propio)` agrega un JOIN contra `Asignacion`**: Puede impactar performance en tenants con muchos registros. → **Mitigación**: El join es contra la tabla de asignaciones vigentes del COORDINADOR, que es un conjunto acotado. Monitorear en staging.
- **[Consistencia] Los estados de comunicación se leen del modelo `Comunicacion` que puede tener registros en tránsito**: El worker de C-12 puede estar actualizando estados concurrentemente. → **Mitigación**: Las lecturas son en el momento del request; es aceptable para un panel informativo.
