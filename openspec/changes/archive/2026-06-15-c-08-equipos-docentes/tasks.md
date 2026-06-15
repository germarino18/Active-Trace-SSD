## 1. Esquemas (Pydantic, `app/schemas/equipo.py`)

- [x] 1.1 RED: test que un DTO de asignación masiva (`AsignacionMasivaCreate`: lista de `usuario_id`, contexto materia/carrera/cohorte, `rol`, `desde`/`hasta`) rechaza campos extra (`extra='forbid'`) y exige los obligatorios
- [x] 1.2 GREEN: implementar `AsignacionMasivaCreate` con `model_config = ConfigDict(extra='forbid')`
- [x] 1.3 RED+GREEN: `ClonarEquipoCreate` (contexto origen, cohorte destino, `desde`/`hasta` del nuevo período) y `VigenciaEquipoUpdate` (contexto equipo, `desde?`/`hasta?`), ambos `extra='forbid'`; triangular con un caso de campo extra y uno válido
- [x] 1.4 RED+GREEN: `MisEquiposFiltros` (estado, materia, rol, carrera, cohorte opcionales), `EquipoFiltros` (materia, carrera, cohorte, usuario, rol, responsable) y `EquipoExportItem`/`AsignacionMasivaResultado` (creadas vs. ya-existentes); incluir `estado_vigencia` derivado en los items de respuesta

## 2. Repository (`app/repositories/asignacion_repository.py`)

- [x] 2.1 RED: test (DB real/efímera, sin mock) de `find_mis_equipos_vigentes(tenant_id, usuario_id, filtros)` — devuelve sólo asignaciones vivas y vigentes del usuario, filtra por tenant; un usuario de otro tenant no aparece
- [x] 2.2 GREEN: implementar `find_mis_equipos_vigentes` (filtra por `tenant_id`, `usuario_id`, `deleted_at IS NULL` y vigencia por fechas)
- [x] 2.3 TRIANGULATE: caso con asignaciones vencidas (no devueltas) y caso con filtros de materia/rol aplicados
- [x] 2.4 RED+GREEN+TRIANGULATE: `find_by_filtros(tenant_id, filtros)` para el listado del tenant — acota por tenant, excluye soft-deleted, aplica filtros; triangular con filtro por responsable y con eliminada excluida
- [x] 2.5 RED+GREEN+TRIANGULATE: `find_equipo(tenant_id, materia_id, carrera_id, cohorte_id, solo_vigentes=False)` — asignaciones vivas de la tripleta; triangular `solo_vigentes=True` (excluye vencidas) y tenant ajeno (vacío)
- [x] 2.6 RED+GREEN+TRIANGULATE: `create_many(rows)` — alta en lote grabando `tenant_id` por fila; triangular con lote de 1 y lote de N
- [x] 2.7 RED+GREEN+TRIANGULATE: `update_vigencia_equipo(tenant_id, contexto, desde, hasta)` — actualiza `desde`/`hasta` de todas las vivas del equipo y devuelve filas afectadas; triangular con equipo de otro tenant (0 filas)
- [x] 2.8 RED+GREEN+TRIANGULATE: `buscar_docentes(tenant_id, query)` (RN-30) — `ILIKE` sobre nombre/apellido acotado al tenant; triangular match parcial y sin resultados
- [x] 2.9 REFACTOR: extraer el predicado de vigencia por fechas a un helper reutilizable; tests siguen verdes

## 3. Service (`app/services/equipo_service.py`)

- [x] 3.1 RED: test de `mis_equipos(current_user, filtros)` — usa `current_user.id`/`tenant_id` (nunca un param), mapea a respuesta con `estado_vigencia` derivado
- [x] 3.2 GREEN: implementar `mis_equipos` delegando en el repository
- [x] 3.3 RED+GREEN+TRIANGULATE: `asignacion_masiva(data, current_user, request)` — valida usuarios y contexto contra el tenant (404 si ajeno), omite los ya-asignados (mismo contexto+rol) sin duplicar, crea el resto vía `create_many`, emite UN `ASIGNACION_MODIFICAR` con filas afectadas; triangular: alta limpia, un docente ya asignado omitido, referencia ajena → NotFound
- [x] 3.4 RED+GREEN+TRIANGULATE: `clonar_equipo(data, current_user, request)` (RN-12) — clona sólo vigentes del origen al destino preservando usuario/rol/responsable/comisiones, aplica fechas nuevas, no duplica equivalentes ya presentes, emite UN `ASIGNACION_MODIFICAR`; triangular: clonado de vigentes, vencidas excluidas, equivalente en destino omitido, tenant ajeno → NotFound
- [x] 3.5 RED+GREEN+TRIANGULATE: `modificar_vigencia(data, current_user, request)` — actualiza vigencia del equipo en bloque, emite UN `ASIGNACION_MODIFICAR` con filas afectadas; triangular: actualización efectiva y equipo vacío (0 filas, sin error)
- [x] 3.6 RED+GREEN+TRIANGULATE: `exportar_equipo(contexto, current_user)` — arma filas CSV (docente, rol, materia, carrera, cohorte, desde, hasta, estado) acotado al tenant, sin auditar; triangular: equipo con asignaciones y equipo de otro tenant (vacío/404)
- [x] 3.7 REFACTOR: factorizar la validación de contexto/usuarios contra el tenant compartida por masiva y clonado; tests verdes

## 4. Router (`app/api/v1/routers/equipos.py`)

- [x] 4.1 RED: test de integración — `GET /api/equipos/mis-equipos` con sesión válida devuelve sólo lo del usuario; sin sesión → 401
- [x] 4.2 GREEN: montar router `/api/equipos`, endpoint `mis-equipos` autorizado por sesión (sin `equipos:asignar`), `usuario_id` desde `current_user`
- [x] 4.3 RED+GREEN: endpoints de coordinación (`GET /` listado, `POST /asignacion-masiva`, `POST /clonar`, `PATCH /vigencia`, `GET /export`, `GET /docentes` autocompletado) con `Depends(require_permission(Perm.EQUIPOS_ASIGNAR))`; test que sin el permiso → 403 (fail-closed) y con el permiso ejecuta acotado al tenant
- [x] 4.4 RED+GREEN: las operaciones de bloque hacen un único `await db.commit()` (transaccional); test que un fallo de validación no deja commit parcial
- [x] 4.5 GREEN: endpoint de export devuelve `text/csv` con `Content-Disposition: attachment`; test del content-type y de una fila por asignación
- [x] 4.6 GREEN: registrar el router en el app factory (`app/main.py` o equivalente)

## 5. Aislamiento de tenant y auditoría (verificación cruzada)

- [x] 5.1 RED+GREEN: test de aislamiento — un coordinador del tenant A no puede listar/masiva/clonar/exportar equipos del tenant B (404), y `mis-equipos` nunca cruza tenants
- [x] 5.2 RED+GREEN: test que cada operación masiva (masiva, clonado, vigencia) registra exactamente UN evento `ASIGNACION_MODIFICAR` y que las operaciones de lectura (mis-equipos, listado, export) NO auditan
- [x] 5.3 Verificar cobertura ≥90% en `equipo_service.py` y los métodos nuevos del repository (reglas de negocio); ≥80% líneas global del módulo

## 6. Cierre

- [x] 6.1 Correr la suite completa del backend; toda verde
- [x] 6.2 Confirmar que no se creó migración Alembic (C-08 no toca schema) y que `Perm.EQUIPOS_ASIGNAR` / `AccionAuditoria.ASIGNACION_MODIFICAR` se reusaron sin redefinir
- [x] 6.3 Marcar el change C-08 como `[x]` en `CHANGES.md`
