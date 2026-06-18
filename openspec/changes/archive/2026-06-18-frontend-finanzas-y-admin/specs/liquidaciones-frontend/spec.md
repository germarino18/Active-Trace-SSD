## ADDED Requirements

### Requirement: Vista de liquidaciones del período
El sistema SHALL mostrar una vista de liquidaciones del período seleccionado, con las siguientes segmentaciones:
- **General**: todos los docentes del tenant
- **NEXO**: solo docentes con rol NEXO (liquidación separada)
- **Factura**: solo docentes que facturan (sin inclusión en liquidación general)

Cada segmentación SHALL mostrar una tabla con columnas: docente, rol, comisiones a cargo, salario base, plus aplicables, total a cobrar.

#### Scenario: Visualizar liquidación general
- **WHEN** el usuario FINANZAS selecciona un período y accede a la vista general
- **THEN** el sistema muestra la tabla con todos los docentes activos del período, con salario base, plus y total calculado

#### Scenario: Filtrar por segmento NEXO
- **WHEN** el usuario FINANZAS selecciona la pestaña "NEXO"
- **THEN** el sistema filtra la tabla mostrando solo docentes con rol NEXO

#### Scenario: Filtrar por segmento Factura
- **WHEN** el usuario FINANZAS selecciona la pestaña "Factura"
- **THEN** el sistema filtra la tabla mostrando solo docentes que facturan

### Requirement: KPIs de liquidación
El sistema SHALL mostrar KPIs en la cabecera de la vista de liquidaciones, incluyendo: cantidad total de docentes en la liquidación, monto total a pagar, cantidad de docentes con factura pendiente, y cantidad de períodos cerrados disponibles en el historial.

#### Scenario: Ver KPIs de la liquidación actual
- **WHEN** el usuario FINANZAS accede a la vista de liquidaciones
- **THEN** el sistema muestra los KPIs calculados para el período activo

### Requirement: Cierre de liquidación
El sistema SHALL permitir al usuario FINANZAS cerrar una liquidación del período actual. Una vez cerrada, la liquidación SHALL ser inmutable y pasar al historial.

#### Scenario: Cerrar liquidación con confirmación
- **WHEN** el usuario FINANZAS hace clic en "Cerrar liquidación"
- **THEN** el sistema muestra un modal de confirmación
- **WHEN** el usuario confirma
- **THEN** el sistema envía la solicitud de cierre y actualiza la vista mostrando la liquidación como cerrada

#### Scenario: Error al cerrar liquidación
- **WHEN** el usuario FINANZAS confirma el cierre
- **THEN** si el backend rechaza la operación, el sistema muestra un mensaje de error con el motivo

### Requirement: Historial de liquidaciones
El sistema SHALL permitir al usuario FINANZAS y ADMIN acceder al historial de liquidaciones cerradas de períodos anteriores, con opción de ver el detalle de cada una.

#### Scenario: Acceder al historial
- **WHEN** el usuario FINANZAS selecciona la pestaña "Historial"
- **THEN** el sistema muestra el listado de liquidaciones cerradas ordenado por período descendente

#### Scenario: Ver detalle de liquidación cerrada
- **WHEN** el usuario hace clic en una liquidación cerrada
- **THEN** el sistema muestra la vista de detalle con todos los datos de la liquidación en modo solo lectura

### Requirement: Exportar liquidación
El sistema SHALL permitir exportar la liquidación del período (activa o cerrada) en formato descargable.

#### Scenario: Exportar liquidación
- **WHEN** el usuario FINANZAS hace clic en "Exportar"
- **THEN** el sistema descarga la planilla de liquidación del período actual
