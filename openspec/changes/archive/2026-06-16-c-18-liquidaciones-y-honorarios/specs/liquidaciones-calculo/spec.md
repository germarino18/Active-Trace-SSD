## ADDED Requirements

### Requirement: Calcular liquidación del período (FL-08, F10.1, RN-21)

El sistema SHALL calcular la liquidación de honorarios para un período y cohorte determinados. Por cada docente con asignaciones vigentes en el período, se calcula: monto_base (según SalarioBase vigente para su rol), monto_plus (suma de SalarioPlus aplicables según las materias que dicta), y total = base + plus.

#### Scenario: Cálculo exitoso de liquidación general
- **GIVEN** un docente con rol PROFESOR y asignaciones vigentes en el período 2026-06
- **GIVEN** existe SalarioBase para PROFESOR vigente en 2026-06 con monto 150000
- **GIVEN** el docente dicta materias de grupo "PROG" y existe SalarioPlus (PROG, PROFESOR) vigente por 25000
- **WHEN** se ejecuta `POST /api/v1/liquidaciones/calcular?periodo=2026-06&cohorte_id=X`
- **THEN** el sistema crea una Liquidacion con `monto_base=150000, monto_plus=25000, total=175000, es_nexo=false, excluido_por_factura=false`

#### Scenario: Docente facturador excluido del total (RN-35)
- **GIVEN** un docente con `facturador=true`
- **WHEN** se calcula liquidación del período
- **THEN** se crea una Liquidacion con `excluido_por_factura=true`
- **AND** el docente aparece en el segmento "factura" (informativo, no suma al total general)

#### Scenario: Docente con rol NEXO (es_nexo=true)
- **GIVEN** un docente cuyas asignaciones vigentes incluyen el rol NEXO
- **WHEN** se calcula liquidación del período
- **THEN** se crea una Liquidacion con `es_nexo=true`
- **AND** su monto se segmenta aparte pero suma al total general

#### Scenario: Docente con múltiples grupos de materias (acumulación RN-33)
- **GIVEN** un docente dicta materias de grupos "PROG" y "BD"
- **GIVEN** existe SalarioPlus (PROG, PROFESOR) = 25000 y (BD, PROFESOR) = 20000
- **WHEN** se calcula liquidación
- **THEN** `monto_plus = 25000 + 20000 = 45000`

#### Scenario: Docente sin salario base configurado
- **GIVEN** NO existe SalarioBase para el rol del docente vigente en el período
- **WHEN** se calcula liquidación
- **THEN** el sistema lanza error de negocio: "No hay SalarioBase configurado para el rol {rol} en el período {periodo}"

#### Scenario: Docente sin asignaciones vigentes en el período
- **GIVEN** un usuario sin asignaciones vigentes en el período
- **WHEN** se calcula liquidación
- **THEN** el docente no se incluye en la liquidación (no se crea Liquidacion)

#### Scenario: Recalcular liquidación (reemplazo)
- **GIVEN** ya existe una Liquidacion abierta para el docente en el período
- **WHEN** se recalcula
- **THEN** el sistema reemplaza la Liquidacion anterior por la nueva (soft delete + creación)

#### Scenario: No recalcular si la liquidación está cerrada
- **GIVEN** existe una Liquidacion cerrada para el docente en el período
- **WHEN** se intenta recalcular
- **THEN** el sistema responde 409 Conflict: "La liquidación del período ya está cerrada"

### Requirement: Segmentación de la vista (F10.6, RN-36/37/38)

El sistema SHALL presentar la liquidación del período en tres segmentos con KPIs de cabecera.

#### Scenario: Vista segmentada con KPIs
- **WHEN** se consulta `GET /api/v1/liquidaciones?periodo=2026-06&cohorte_id=X`
- **THEN** el sistema devuelve:
  - **general**: liquidaciones de docentes no facturadores (excluye NEXO), con subtotal
  - **nexo**: liquidaciones con `es_nexo=true`, con subtotal
  - **factura**: liquidaciones con `excluido_por_factura=true` (solo informativo)
  - **kpis**: `total_sin_factura` (general + nexo), `total_con_factura` (suma de facturas)

#### Scenario: Filtro por docente específico
- **WHEN** se consulta `GET /api/v1/liquidaciones?periodo=2026-06&usuario_id=X`
- **THEN** el sistema devuelve solo la liquidación del docente X en sus segmentos correspondientes

### Requirement: Historial de liquidaciones (F10.3)

El sistema SHALL permitir consultar liquidaciones cerradas de períodos anteriores.

#### Scenario: Consultar historial
- **WHEN** se consulta `GET /api/v1/liquidaciones/historial?cohorte_id=X`
- **THEN** el sistema devuelve todas las liquidaciones cerradas ordenadas por periodo descendente

#### Scenario: Historial filtrado por rango
- **WHEN** se consulta `GET /api/v1/liquidaciones/historial?desde=2026-01&hasta=2026-06`
- **THEN** el sistema devuelve solo las liquidaciones en ese rango de períodos
