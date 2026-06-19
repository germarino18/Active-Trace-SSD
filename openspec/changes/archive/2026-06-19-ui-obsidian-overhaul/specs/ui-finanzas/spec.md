## ADDED Requirements

### Requirement: Liquidaciones de honorarios
`LiquidacionesPage` SHALL mostrar las liquidaciones de honorarios por período, con estado (borrador/aprobada/pagada). El coordinador ve las propias; FINANZAS ve todas. Incluye acción de aprobar/rechazar para el rol FINANZAS.

#### Scenario: Vista de liquidaciones propias (COORDINADOR)
- **WHEN** el coordinador accede a liquidaciones
- **THEN** ve solo sus liquidaciones con monto, período y estado

#### Scenario: Aprobar liquidación (FINANZAS)
- **WHEN** el usuario FINANZAS aprueba una liquidación
- **THEN** el estado cambia a "Aprobada" y se registra en auditoría

#### Scenario: Sin liquidaciones
- **WHEN** no hay liquidaciones para el período
- **THEN** se muestra `EmptyState` con mensaje descriptivo

---

### Requirement: Grilla salarial
`GrillaSalarialPage` SHALL mostrar la escala de valores por categoría docente (horas, plus, etc.). Es de solo lectura para coordinadores; FINANZAS puede editar los valores.

#### Scenario: Ver grilla
- **WHEN** cualquier usuario con acceso a finanzas accede
- **THEN** se muestra la tabla de categorías con sus valores actuales

#### Scenario: Editar valor (solo FINANZAS)
- **WHEN** el usuario FINANZAS modifica un valor y confirma
- **THEN** el nuevo valor se guarda y se registra el cambio en auditoría

---

### Requirement: Facturas asociadas
`FacturasPage` SHALL mostrar las facturas vinculadas a liquidaciones aprobadas. Cada fila incluye: número de factura, monto, fecha, estado (pendiente/pagada). Permite filtrar por período y estado.

#### Scenario: Facturas pendientes de pago
- **WHEN** existen facturas en estado "Pendiente"
- **THEN** se destacan visualmente respecto a las pagadas

#### Scenario: Sin facturas
- **WHEN** no hay facturas en el período seleccionado
- **THEN** se muestra `EmptyState` con sugerencia de cambiar el filtro de período
