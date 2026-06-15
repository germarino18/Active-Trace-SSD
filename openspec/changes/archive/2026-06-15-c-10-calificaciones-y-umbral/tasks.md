## 1. Modelos y Migración

- [x] 1.1 Crear `CalificacionOrigen` enum (Importado, Manual) en `app/models/calificacion.py`
- [x] 1.2 Crear modelo `Calificacion` con `id`, `tenant_id`, `entrada_padron_id`, `dictado_id`, `actividad`, `nota_numerica`, `nota_textual`, `aprobado`, `origen`, `importado_at` en `app/models/calificacion.py`
- [x] 1.3 Crear modelo `UmbralMateria` con `id`, `tenant_id`, `asignacion_id`, `dictado_id`, `umbral_pct`, `valores_aprobatorios` (JSONB) en `app/models/umbral_materia.py`
- [x] 1.4 Crear migración Alembic 009 con tablas `calificacion` y `umbral_materia`, índices, y seed de permisos/roles si hacen falta
- [x] 1.5 Agregar `UMBRAL_CONFIGURAR` a `AccionAuditoria` en `app/core/acciones_auditoria.py`

## 2. Esquemas Pydantic

- [x] 2.1 Crear `CalificacionResponse` y `CalificacionImportRow` en `app/schemas/calificaciones.py`
- [x] 2.2 Crear `PreviewCalificacionesResponse` con `actividades_detectadas`, `filas`, `total_filas`, `preview_token`
- [x] 2.3 Crear `PreviewCalificacionesRequest` (dictado_id, file como UploadFile)
- [x] 2.4 Crear `ImportCalificacionesConfirm` con `dictado_id`, `preview_token`, `actividades_seleccionadas`
- [x] 2.5 Crear `ImportCalificacionesResponse` con `total_importados`, `aprobados`, `desaprobados`
- [x] 2.6 Crear `UmbralMateriaCreate`, `UmbralMateriaUpdate`, `UmbralMateriaResponse`

## 3. Repositorios

- [x] 3.1 Crear `CalificacionRepository` con `bulk_create`, `find_by_dictado`, `recalcular_aprobado_por_dictado` en `app/repositories/calificacion_repository.py`
- [x] 3.2 Crear `UmbralMateriaRepository` con `find_by_asignacion_dictado`, `upsert`, `delete` en `app/repositories/umbral_materia_repository.py`

## 4. Parser de Archivos

- [x] 4.1 Crear `parse_calificaciones.py` en `app/services/calificaciones/` con función `parse_calificaciones_file`
- [x] 4.2 Implementar detección de columnas numéricas (RN-01: sufijo `(Real)`) y agrupación por actividad
- [x] 4.3 Implementar detección de valores textuales aprobatorios (RN-02)
- [x] 4.4 Implementar detección de TPs sin calificar para F1.2
- [x] 4.5 Implementar validación de límite de filas (10K)

## 5. Servicio de Calificaciones

- [x] 5.1 Crear `CalificacionService` en `app/services/calificaciones/calificacion_service.py`
- [x] 5.2 Implementar `preview_archivo()`: parse file, detect columns, generate preview_token
- [x] 5.3 Implementar `confirmar_importacion()`: validar token, persistir calificaciones, calcular `aprobado` con umbral vigente o defecto 60%, auditar
- [x] 5.4 Implementar `importar_finalizacion_preview()` y `importar_finalizacion_confirm()` para F1.2
- [x] 5.5 Implementar recálculo de `aprobado` al cambiar umbral (re-calcula calificaciones del dictado)

## 6. Servicio de Umbral

- [x] 6.1 Crear `UmbralService` en `app/services/calificaciones/umbral_service.py`
- [x] 6.2 Implementar `obtener_umbral()` con fallback a defecto 60%
- [x] 6.3 Implementar `configurar_umbral()` con upsert + recálculo + auditoría

## 7. Router

- [x] 7.1 Crear `calificaciones.py` en `app/api/v1/routers/` con prefix `/api/admin/calificaciones`
- [x] 7.2 Endpoint `POST /api/admin/calificaciones/preview` — preview de calificaciones (deps: require_permission(CALIFICACIONES_IMPORTAR))
- [x] 7.3 Endpoint `POST /api/admin/calificaciones/importar` — confirmar importación
- [x] 7.4 Endpoint `POST /api/admin/calificaciones/preview-finalizacion` — preview de finalización
- [x] 7.5 Endpoint `POST /api/admin/calificaciones/importar-finalizacion` — confirmar finalización
- [x] 7.6 Endpoint `GET /api/admin/calificaciones/dictados/{dictado_id}` — listar calificaciones de un dictado
- [x] 7.7 Endpoint `PUT /api/admin/calificaciones/umbral` — configurar umbral
- [x] 7.8 Endpoint `GET /api/admin/calificaciones/umbral` — obtener umbral vigente
- [x] 7.9 Registrar router en `app/api/v1/__init__.py` (router registration en `main.py`)

## 8. Tests

- [x] 8.1 Test: preview de calificaciones detecta columnas numéricas y textuales
- [x] 8.2 Test: confirm importa solo actividades seleccionadas
- [x] 8.3 Test: aprobado calculado correctamente con umbral 60%
- [x] 8.4 Test: aprobado con nota textual "Satisfactorio"
- [x] 8.5 Test: preview rechazado sin permiso (403)
- [x] 8.6 Test: preview rechazado para PROFESOR sin asignación (403)
- [x] 8.7 Test: confirm con token inválido (422)
- [x] 8.8 Test: importación de finalización detecta TPs sin calificar
- [x] 8.9 Test: configurar umbral recalcula aprobado existente
- [x] 8.10 Test: umbral por defecto 60% cuando no hay configuración
- [x] 8.11 Test: validación de umbral_pct fuera de rango (0-100)
- [x] 8.12 Test: aislamiento multi-tenant (404 para dictado de otro tenant)
