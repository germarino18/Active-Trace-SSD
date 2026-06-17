## Why

El sistema ya cuenta con un registro de auditoría append-only (C-05) que captura toda acción significativa, pero no existe una interfaz que permita visualizar, filtrar y analizar esos datos. Los COORDINADORES, ADMIN y FINANZAS necesitan un panel de supervisión para monitorear la actividad de los docentes, detectar inactividad, rastrear comunicaciones fallidas y auditar el uso del sistema — todo sin acceso a la base de datos.

## What Changes

- **Nuevo endpoint** `GET /api/v1/auditoria/acciones-por-dia` — serie temporal de acciones agrupadas por día, con filtro opcional por usuario, materia y rango de fechas.
- **Nuevo endpoint** `GET /api/v1/auditoria/comunicaciones-por-docente` — distribución de estados de comunicación (Pendiente/Enviando/OK/Fallido/Cancelado) agrupada por docente y materia.
- **Nuevo endpoint** `GET /api/v1/auditoria/interacciones-por-docente-materia` — métricas de uso desglosadas por tipo de acción (análisis, preview, importación, envío, limpieza, umbral, etc.) por docente y materia.
- **Nuevo endpoint** `GET /api/v1/auditoria/ultimas-acciones` — log detallado de las últimas N acciones (máximo configurable vía query param, defecto 200), con filtros por rango de fechas, materia, usuario y estado de actividad.
- **Endpoint existente extendido** — consultas sobre `AuditLog` con filtros combinados (rango de fechas, materia, usuario, código de acción).
- **Permiso `auditoria:ver`** ya existe en el sistema (seed de C-04/C-05); se aplica como guard en todos los endpoints, con scope `(propio)` para COORDINADOR (solo ve acciones de usuarios de su alcance).
- **Solo lectura** — ningún endpoint de este change modifica datos. Todos los cambios son consultas sobre `AuditLog` y `Comunicacion`.
- **BREAKING**: Ninguno. No se modifican modelos, schemas ni tablas existentes.

## Capabilities

### New Capabilities
- `panel-interacciones`: Panel de interacciones del sistema con agregaciones por día, docente, materia y tipo de acción (F9.1).
- `log-auditoria-completo`: Log completo de auditoría con filtros combinados y paginación (F9.2).

### Modified Capabilities
- Ninguna. El spec `audit-log` existente (C-05) define el modelo de datos y su enforcement append-only; este change agrega capacidades de consulta y agregación sobre ese mismo modelo, sin modificar sus requisitos.

## Impact

- **Nuevos archivos**: `backend/app/api/v1/routers/auditoria.py`, `backend/app/services/auditoria_service.py`, `backend/app/schemas/auditoria.py`, `backend/tests/test_auditoria/`
- **Modelos**: Sin cambios. Consultas sobre `AuditLog` y `Comunicacion` existentes.
- **Permisos**: `auditoria:ver` ya seedeado. COORDINADOR con scope `(propio)` — requiere verificación en el service.
- **Dependencias**: C-05 (audit-log) provee el modelo AuditLog. C-07 (usuarios) provee asignaciones para resolver scope `(propio)`.
