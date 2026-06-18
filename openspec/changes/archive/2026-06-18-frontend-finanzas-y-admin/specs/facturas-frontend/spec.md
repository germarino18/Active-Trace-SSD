## ADDED Requirements

### Requirement: Listado de facturas
El sistema SHALL mostrar un listado de comprobantes presentados por docentes que facturan, con filtros por: docente, estado (pendiente/abonada), rango de fechas y búsqueda libre. La tabla SHALL mostrar: fecha de carga, docente, período facturado, detalle, archivo adjunto, tamaño del archivo, estado, datos de pago.

#### Scenario: Listar facturas con filtros
- **WHEN** el usuario FINANZAS accede a la sección "Facturas"
- **THEN** el sistema muestra el listado paginado de comprobantes con filtros aplicables
- **WHEN** el usuario selecciona un filtro de estado "Pendiente"
- **THEN** el sistema filtra la tabla mostrando solo comprobantes pendientes

#### Scenario: Búsqueda libre en facturas
- **WHEN** el usuario FINANZAS ingresa texto en el campo de búsqueda libre
- **THEN** el sistema filtra la tabla por docente o detalle que contengan el texto ingresado

### Requirement: ABM de facturas
El sistema SHALL permitir crear, editar y eliminar comprobantes. El formulario SHALL incluir: docente, período facturado, detalle, archivo adjunto (PDF/imagen), estado (pendiente por defecto).

#### Scenario: Crear factura con archivo adjunto
- **WHEN** el usuario FINANZAS completa el formulario de nueva factura con docente, período, detalle y archivo adjunto
- **THEN** el sistema crea el comprobante y lo muestra en el listado

#### Scenario: Editar factura
- **WHEN** el usuario FINANZAS edita una factura existente
- **THEN** el sistema actualiza los datos del comprobante

#### Scenario: Eliminar factura con confirmación
- **WHEN** el usuario FINANZAS hace clic en eliminar una factura
- **THEN** el sistema muestra un modal de confirmación
- **WHEN** el usuario confirma
- **THEN** el sistema elimina el comprobante y actualiza el listado

### Requirement: Cambio de estado de factura
El sistema SHALL permitir cambiar el estado de un comprobante entre "Pendiente" y "Abonada" mediante una acción directa desde el listado.

#### Scenario: Marcar factura como abonada
- **WHEN** el usuario FINANZAS hace clic en "Marcar como abonada" en una factura pendiente
- **THEN** el sistema cambia el estado a "Abonada" y actualiza la fila en la tabla

### Requirement: Visualización de archivo adjunto
El sistema SHALL permitir visualizar o descargar el archivo adjunto de una factura mediante un enlace en la tabla.

#### Scenario: Descargar archivo adjunto
- **WHEN** el usuario FINANZAS hace clic en el nombre del archivo adjunto
- **THEN** el sistema descarga el archivo
