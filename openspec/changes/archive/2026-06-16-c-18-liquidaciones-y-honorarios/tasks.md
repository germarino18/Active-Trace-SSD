## 1. Modelos de Datos

- [x] 1.1 Crear modelo `SalarioBase` (E17): tenant_id, rol, monto, desde, hasta — con mixins BaseMixin, TenantMixin, SoftDeleteMixin
- [x] 1.2 Crear modelo `SalarioPlus` (E18): tenant_id, grupo, rol, descripcion, monto, desde, hasta — con mixins
- [x] 1.3 Crear modelo `ClavePlus` (E22): tenant_id, codigo, descripcion, desde, hasta — con mixins, unique (tenant_id, codigo)
- [x] 1.4 Crear modelo `MateriaClavePlus` (E23): tenant_id, materia_id, clave_plus_id, desde, hasta — con mixins, unique (tenant_id, materia_id) entre vivos
- [x] 1.5 Crear modelo `Liquidacion` (E19): tenant_id, cohorte_id, periodo, usuario_id, rol, comisiones, monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado — con mixins
- [x] 1.6 Crear modelo `Factura` (E20): tenant_id, usuario_id, periodo, detalle, referencia_archivo, tamano_kb, estado, cargada_at, abonada_at — con mixins
- [x] 1.7 Exportar los 6 nuevos modelos desde `models/__init__.py`

## 2. Migración Alembic 016

- [x] 2.1 Crear migración `016_create_liquidacion_tables.py` con las 6 tablas, índices únicos (con `postgresql_where=text("deleted_at IS NULL")`), y FKs
- [x] 2.2 Seed permisos `liquidaciones:ver`, `liquidaciones:calcular`, `liquidaciones:configurar-salarios` en la migración (rol FINANZAS)
- [x] 2.3 Ejecutar migración (016→017) y verificar que las tablas se crean correctamente. Se detectó conflicto de revision ID (016 usaba d0e1f2a3b4c5, mismo que 010) — corregido a a6f5588d22a5. Seed de permisos fallaba por buscar rol global (tenant_id IS NULL) cuando roles son per-tenant — corregido en migración 017 + helpers.py.

## 3. Schemas Pydantic

- [x] 3.1 Crear `schemas/liquidaciones.py` con schemas Create/Update/Response para: SalarioBase, SalarioPlus, ClavePlus, MateriaClavePlus, Liquidacion — todos con `extra='forbid'`
- [x] 3.2 Crear `schemas/facturas.py` con schemas Create/Update/Response para Factura — con `extra='forbid'`
- [x] 3.3 Crear schemas de request/response para cálculo de liquidación (LiquidacionCalcularRequest, LiquidacionPeriodoResponse con segmentación general/nexo/factura + KPIs)

## 4. Repositorios

- [x] 4.1 Crear `SalarioBaseRepository(BaseRepository[SalarioBase])` con métodos: `find_vigente_en(rol, fecha)`, `find_all_by_rol()`, `check_solapamiento()`
- [x] 4.2 Crear `SalarioPlusRepository(BaseRepository[SalarioPlus])` con: `find_vigentes_en(grupo, rol, fecha)`, `find_by_grupo_rol()`, `check_solapamiento()`
- [x] 4.3 Crear `ClavePlusRepository(BaseRepository[ClavePlus])` con: `find_by_codigo()`, `find_vigentes_en(fecha)`
- [x] 4.4 Crear `MateriaClavePlusRepository(BaseRepository[MateriaClavePlus])` con: `find_vigente_para_materia(materia_id, fecha)`, `find_by_materia()`, `check_solapamiento()`
- [x] 4.5 Crear `LiquidacionRepository(BaseRepository[Liquidacion])` con: `find_by_periodo(periodo, cohorte_id)`, `find_by_usuario_periodo()`, `find_historial()`, `find_abiertas_por_periodo()`
- [x] 4.6 Crear `FacturaRepository(BaseRepository[Factura])` con: `find_by_usuario()`, `find_by_periodo()`, `find_by_estado()`, filtros combinados

## 5. Servicios

- [x] 5.1 Crear `LiquidacionService` con método `calcular_periodo(periodo, cohorte_id, current_user, request)` que:
  - Obtiene todas las asignaciones vigentes en el período
  - Por cada docente: busca SalarioBase vigente, determina plus según materias dictadas (vía MateriaClavePlus → ClavePlus → SalarioPlus), calcula total
  - Crea/reemplaza Liquidacion (con es_nexo, excluido_por_factura según corresponda)
  - Es transaccional (un solo commit)
- [x] 5.2 Implementar en `LiquidacionService` el método `cerrar(liquidacion_id, current_user, request)` que:
  - Cambia estado a Cerrada con validación de que no esté ya cerrada
  - Registra AuditLog con accion=LIQUIDACION_CERRAR
- [x] 5.3 Implementar en `LiquidacionService` el método `obtener_vista_periodo(periodo, cohorte_id, usuario_id)` que:
  - Retorna segmentación general/nexo/factura con KPIs
- [x] 5.4 Crear `GrillaSalarialService` con ABM delegado a repositorios para SalarioBase y SalarioPlus, con validación de solapamiento de vigencias
- [x] 5.5 Crear `ClavePlusService` con ABM delegado para ClavePlus y MateriaClavePlus
- [x] 5.6 Crear `FacturaService` con métodos: crear (valida facturador=true), listar (con filtros), abonar (cambio de estado), soft delete

## 6. Router — Liquidaciones

- [x] 6.1 Crear `api/v1/routers/liquidaciones.py` con:
  - `GET /api/v1/liquidaciones` — vista segmentada del período (guard `liquidaciones:ver`)
  - `GET /api/v1/liquidaciones/historial` — historial (guard `liquidaciones:ver`)
  - `POST /api/v1/liquidaciones/calcular` — calcular período (guard `liquidaciones:calcular`)
  - `POST /api/v1/liquidaciones/{id}/cerrar` — cierre inmutable (guard `liquidaciones:cerrar`)
- [x] 6.2 Agregar a `liquidaciones.py` los endpoints CRUD para SalarioBase, SalarioPlus, ClavePlus, MateriaClavePlus (guard `liquidaciones:configurar-salarios`)
- [x] 6.3 Registrar router `liquidaciones.router` en `api/v1/__init__.py` y en `main.py`

## 7. Router — Facturas

- [x] 7.1 Crear `api/v1/routers/facturas.py` con:
  - `GET /api/v1/facturas` — listar con filtros (guard `facturas:gestionar`)
  - `POST /api/v1/facturas` — crear (guard `facturas:gestionar`)
  - `PATCH /api/v1/facturas/{id}` — actualizar (guard `facturas:gestionar`)
  - `DELETE /api/v1/facturas/{id}` — soft delete (guard `facturas:gestionar`)
  - `POST /api/v1/facturas/{id}/abonar` — marcar abonada (guard `facturas:gestionar`)
- [x] 7.2 Registrar router `facturas.router` en `api/v1/__init__.py` y en `main.py`

## 8. Tests

- [x] 8.1 Crear `tests/test_liquidaciones/conftest.py` con fixtures específicos (salario base, plus, clave, materia_clave, liquidacion factories)
- [x] 8.2 Tests de modelos: creación, soft delete, unicidades, FKs, aislamiento multi-tenant
- [x] 8.3 Tests de repositorios: SalarioBase vigente en fecha, check solapamiento, ClavePlus por código, MateriaClavePlus vigente por materia, Liquidacion por período
- [x] 8.4 Tests de LiquidacionService: cálculo exitoso, docente sin base, docente facturador, docente NEXO, acumulación de plus, recálculo reemplaza abierta, rechazo sobre cerrada
- [x] 8.5 Tests de cierre: exitoso con auditoría, rechazo de cerrada, 403 sin permiso, inmutabilidad post-cierre
- [x] 8.6 Tests de FacturaService: creación, validación facturador=true, cambio a abonada, rechazo doble abonado, soft delete, filtros combinados
- [x] 8.7 Tests de routers: endpoints responden 200/201/403/404/409 según corresponda, segmentación de vista, KPIs correctos

## 9. Integración y Verificación

- [x] 9.1 Verificar que todos los nuevos modelos y routers se importan correctamente (test suite carga sin errores de importación)
- [x] 9.2 Ejecutar suite completa de tests (pytest) y verificar que no se rompen tests existentes (231 tests, todos verdes: 99 liquidaciones + 132 avisos/estructura)
- [x] 9.3 Verificar aislamiento multi-tenant en tests (cubierto por test_multi_tenant_isolation_liquidacion y test multi-tenant integración existentes)
