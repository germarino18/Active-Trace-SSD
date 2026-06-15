## Why

La plataforma necesita gestionar calificaciones de alumnos y configurar umbrales de aprobación por materia para determinar automáticamente el estado "aprobado/desaprobado". Actualmente no hay modelo de datos ni flujo para importar notas desde el LMS ni para definir umbrales configurables por asignación docente.

## What Changes

- Nuevos modelos `Calificacion` (nota numérica/textual, aprobado derivado, origen Importado/Manual) y `UmbralMateria` (umbral_pct, valores_aprobatorios como JSONB)
- Importación de calificaciones desde archivo LMS (F1.1): detecta columnas numéricas (RN-01: sufijo `(Real)`) y textuales (RN-02: Satisfactorio/Supera lo esperado), preview con selección de actividades
- Importación de reporte de finalización (F1.2): detecta TPs entregados sin nota
- Configuración de umbral por materia (F2.1, RN-03: defecto 60%) — scope por asignación docente
- Nueva acción de auditoría `CALIFICACIONES_IMPORTAR`
- Migración 009 con tablas `calificacion` y `umbral_materia`

## Capabilities

### New Capabilities
- `importar-calificaciones`: Importación de calificaciones desde archivo LMS con detección de columnas numéricas/textuales, preview en 2 pasos y selección de actividades (F1.1)
- `importar-finalizacion`: Importación de reporte de finalización con detección de TPs entregados sin calificar (F1.2)
- `configurar-umbral`: Configuración de umbral de aprobación por asignación docente con valor por defecto 60% y lista de valores aprobatorios textuales (F2.1)

### Modified Capabilities
- `audit-log`: Nueva acción `CALIFICACIONES_IMPORTAR` para auditar importaciones de calificaciones

## Impact

- Backend: Nuevos modelos SQLAlchemy, migración Alembic 009, repositorios, servicios, schemas Pydantic, router `/api/admin/calificaciones`
- Permisos: `calificaciones:importar` (ya existe en clase Perm)
- Auditoría: nuevo código en `AccionAuditoria` (ya existe)
- Frontend: Ningún cambio inmediato — solo backend en este change
