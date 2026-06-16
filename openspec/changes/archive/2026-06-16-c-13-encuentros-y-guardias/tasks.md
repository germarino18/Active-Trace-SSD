## 1. Modelos y Migración

- [x] 1.1 Crear `backend/app/models/slot_encuentro.py` con modelo `SlotEncuentro` (id, tenant_id, dictado_id FK→Dictado, asignacion_id FK→Asignacion nullable, titulo, hora, dia_semana enum, fecha_inicio, cant_semanas entero default 0, fecha_unica nullable, meet_url, vig_desde, vig_hasta)
- [x] 1.2 Crear `backend/app/models/instancia_encuentro.py` con modelo `InstanciaEncuentro` (id, tenant_id, slot_id FK→SlotEncuentro nullable, dictado_id FK→Dictado, asignacion_id FK→Asignacion nullable, fecha, hora, titulo, estado enum Programado|Realizado|Cancelado, meet_url, video_url nullable, comentario nullable)
- [x] 1.3 Crear `backend/app/models/guardia.py` con modelo `Guardia` (id, tenant_id, asignacion_id FK→Asignacion no nullable, dictado_id FK→Dictado, dia enum, horario texto, estado enum Pendiente|Realizada|Cancelada, comentarios nullable, creada_at)
- [x] 1.4 Crear migración Alembic `011_create_encuentro_guardia_tables.py` con tablas `slot_encuentro`, `instancia_encuentro`, `guardia`, índices en `(tenant_id, dictado_id)` y `(tenant_id, asignacion_id)`
- [x] 1.5 Registrar modelos en `backend/app/models/__init__.py`
- [x] 1.6 Crear `backend/app/schemas/encuentros.py` con schemas Pydantic: `SlotEncuentroCreate`, `SlotEncuentroRead`, `SlotEncuentroUpdate`, `InstanciaEncuentroCreate`, `InstanciaEncuentroRead`, `InstanciaEncuentroUpdate`, `BloqueHTMLResponse`
- [x] 1.7 Crear `backend/app/schemas/guardias.py` con schemas Pydantic: `GuardiaCreate`, `GuardiaRead`, `GuardiaUpdate`, `GuardiaExportRow`

## 2. Repositories

- [x] 2.1 Crear `backend/app/repositories/encuentro_repository.py` con `SlotEncuentroRepository`: create, get_by_id, list_by_dictado, update, soft_delete; e `InstanciaEncuentroRepository`: create, get_by_id, list_by_dictado, list_by_slot, list_by_tenant (con filtros opcionales), update_estado, bulk_create (para generación upfront)
- [x] 2.2 Crear `backend/app/repositories/guardia_repository.py` con `GuardiaRepository`: create, get_by_id, list_by_tenant (con filtros: dictado_id, asignacion_id, estado, dia), list_by_asignacion, update, list_for_export

## 3. Services

- [x] 3.1 Crear `backend/app/services/encuentros.py` con `EncuentrosService`: `crear_slot` (genera instancias si cant_semanas > 0), `crear_instancia_unica` (slot con cant_semanas=0 + fecha_unica), `editar_instancia` (valida transiciones de estado), `generar_bloque_html`, `listar_instancias` (con scope por tenant y filtro por dictado), `listar_admin` (vista transversal, solo COORDINADOR/ADMIN)
- [x] 3.2 Crear `backend/app/services/guardias.py` con `GuardiasService`: `registrar`, `editar`, `listar` (TUTOR filtrado por su asignacion_id, COORDINADOR/ADMIN global), `exportar_csv`
- [x] 3.3 Incluir en services: verificación de permiso `encuentros:gestionar`, auditoría con códigos `ENCUENTRO_CREAR` / `ENCUENTRO_EDITAR` / `ENCUENTRO_CANCELAR` / `GUARDIA_REGISTRAR`, validación de reglas (slot rechazado si cant_semanas > 52, instancia cancelada no se reactiva, etc.)

## 4. HTML Generation

- [x] 4.1 Implementar `generar_bloque_html` en `EncuentrosService`: consulta instancias activas del dictado ordenadas por fecha, aplica plantilla string.Template, devuelve string HTML con tabla semántica

## 5. Guardia Export

- [x] 5.1 Implementar `exportar_csv` en `GuardiasService`: consulta guardias con filtros, genera CSV con StreamingResponse, columnas: día, horario, materia, docente, estado, comentarios

## 6. Routers / API

- [x] 6.1 Crear `backend/app/api/v1/routers/encuentros.py` con endpoints:
  - `POST /api/v1/encuentros/slots` — crear slot (recurrente o único)
  - `GET /api/v1/encuentros/slots/{id}` — detalle de slot
  - `PUT /api/v1/encuentros/slots/{id}` — editar slot
  - `DELETE /api/v1/encuentros/slots/{id}` — eliminar slot (soft delete)
  - `GET /api/v1/encuentros/instancias` — listar instancias (filtro `dictado_id` obligatorio para PROFESOR, opcional para COORDINADOR/ADMIN)
  - `GET /api/v1/encuentros/instancias/{id}` — detalle de instancia
  - `PUT /api/v1/encuentros/instancias/{id}` — editar instancia (estado, meet_url, video_url, comentario)
  - `GET /api/v1/encuentros/bloque-html?dictado_id=` — generar bloque HTML para LMS
- [x] 6.2 Crear `backend/app/api/v1/routers/guardias.py` con endpoints:
  - `POST /api/v1/guardias` — registrar guardia
  - `GET /api/v1/guardias` — listar guardias (TUTOR filtrado por su asignación, COORDINADOR/ADMIN global)
  - `GET /api/v1/guardias/{id}` — detalle de guardia
  - `PUT /api/v1/guardias/{id}` — editar guardia (estado, comentarios)
  - `GET /api/v1/guardias/export` — exportar guardias a CSV
- [x] 6.3 Wirear routers en `backend/app/main.py` (import + include_router)

## 7. Permisos

- [x] 7.1 Verificar que el permiso `encuentros:gestionar` existe en los seeds de permisos de C-04. Si no existe, agregarlo a la tabla `permiso` y asignarlo a los roles PROFESOR, COORDINADOR y ADMIN.

## 8. Tests

- [x] 8.1 Crear `backend/tests/test_encuentros/test_models.py`: creación de SlotEncuentro e InstanciaEncuentro, generación de instancias por slot recurrente, validación de transiciones de estado de instancia
- [x] 8.2 Crear `backend/tests/test_encuentros/test_repository.py`: CRUD slots, bulk_create instancias, listados con filtros por dictado/estado
- [x] 8.3 Crear `backend/tests/test_encuentros/test_service.py`: creación de slot recurrente con N instancias, slot único, edición de instancia con transiciones válidas/inválidas, generación de bloque HTML
- [x] 8.4 Crear `backend/tests/test_encuentros/test_router.py`: tests de integración contra API (200/403/404/422)
- [x] 8.5 Crear `backend/tests/test_guardias/test_models.py`: creación de Guardia, valores por defecto
- [x] 8.6 Crear `backend/tests/test_guardias/test_repository.py`: CRUD guardias, filtros, list_by_asignacion
- [x] 8.7 Crear `backend/tests/test_guardias/test_service.py`: registro, edición, scope por tenant y por asignacion (TUTOR solo ve las suyas), export CSV
- [x] 8.8 Crear `backend/tests/test_guardias/test_router.py`: tests de integración contra API (200/403/404/422)
- [x] 8.9 Ejecutar suite completa de tests y verificar que no se rompen tests existentes
