## Context

Activia-trace necesita gestionar calificaciones de alumnos (notas numéricas y textuales) y umbrales de aprobación configurables por materia. El flujo de importación de calificaciones desde el LMS sigue el mismo patrón de 2 pasos (preview → confirm) que C-09 implementó para el padrón.

Ya existen:
- `Perm.CALIFICACIONES_IMPORTAR` en `app/core/permissions.py`
- `AccionAuditoria.CALIFICACIONES_IMPORTAR` en `app/core/acciones_auditoria.py`
- El permiso está asignado a PROFESOR y COORDINADOR en la migración existente

## Goals / Non-Goals

**Goals:**
- Modelo `Calificacion` con soporte para nota numérica y/o textual, aprobado derivado, origen (Importado/Manual)
- Modelo `UmbralMateria` con umbral_pct configurable por asignación y valores_aprobatorios textuales como JSONB
- Importación de calificaciones desde archivo LMS (F1.1): detección de columnas numéricas (RN-01: sufijo `(Real)`) y textuales (RN-02: Satisfactorio/Supera lo esperado), preview con selección de actividades
- Importación de reporte de finalización (F1.2): detecta TPs entregados sin nota
- Configuración de umbral por materia (F2.1, RN-03) — scope por asignación docente
- Migración Alembic 009 con tablas y seed de permisos/roles
- Aislamiento multi-tenant y RBAC (`calificaciones:importar`) en todos los endpoints

**Non-Goals:**
- Frontend de UI para calificaciones o umbral — solo backend en este change
- Sincronización automática con Moodle — es importación manual por archivo
- Cálculo de estado académico global del alumno — solo calificación individual
- Versionado de umbrales — se actualiza in-place

## Decisions

| Decisión | Opción elegida | Alternativa considerada | Rationale |
|----------|---------------|------------------------|-----------|
| **aprobado como columna derivada** | Almacenado (calculado al importar y al actualizar umbral) | Calculado siempre en read | Consultas más simples (filtros SQL directos), evita N+1. Se recalcula si cambia el umbral del dictado |
| **Preview tokens** | En memoria (class-level dict con TTL 30 min) | Redis/DB | Consistente con C-09. Suficiente para 1-step confirm. Migrar a Redis si escala |
| **Detección de columnas** | RN-01: columnas terminadas en `(Real)` → numéricas. RN-02: valores textuales aprobatorios | Heurística ML | Reglas de negocio explícitas de la KB, no necesitan ML |
| **Origen enum** | SQLAlchemy `Enum` con `Importado` y `Manual` | String simple | Type safety en el modelo |
| **Soft delete en Calificacion** | No (misma estrategia que EntradaPadron) | Sí | Datos de importación que se reemplazan en lote. El histórico se gestiona por importación, no por soft-delete individual |
| **Agrupación de archivos** | Un archivo por dictado | Multi-dictado | Simple, consistente con el flujo del usuario (selecciona materia → sube archivo) |
| **Ruta de API** | `/api/admin/calificaciones` | `/api/v1/calificaciones` | Consistente con `/api/admin/padron` de C-09 |

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| Preview tokens en memoria se pierden en restart del servidor | El confirm falla con 422, el usuario re-subirá el archivo. TTL corto (30 min) |
| Archivo LMS grande (>10K filas) satura memoria | Fijar límite de 10K filas en preview. Si excede, rechazar con mensaje claro y sugerir dividir el archivo |
| Umbral configurable afecta calificaciones existentes | Al cambiar umbral, disparar recálculo batch de `aprobado` en CalificacionService. Registrar evento en audit log |
| Selección de actividades en preview agrega complejidad al flujo 2-step | El preview devuelve actividades detectadas + token. El confirm incluye `actividades_seleccionadas: list[str]`. Si no se envía, se importan todas |
