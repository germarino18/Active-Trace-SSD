## ADDED Requirements

### Requirement: Log completo de auditoría
El sistema SHALL mostrar al ADMIN el log completo de auditoría con los campos: fecha y hora, identificador de usuario, materia, tipo de acción, cantidad de registros afectados, dirección IP de origen, agente de usuario. El log SHALL estar limitado a un máximo configurable de registros por consulta (por defecto 200).

#### Scenario: Ver log de auditoría
- **WHEN** el ADMIN accede a la sección "Auditoría > Log"
- **THEN** el sistema muestra el log paginado con los últimos registros

#### Scenario: Filtrar log por rango de fechas
- **WHEN** el ADMIN selecciona un rango de fechas en los filtros
- **THEN** el sistema muestra solo los registros dentro de ese rango

#### Scenario: Filtrar log por tipo de acción
- **WHEN** el ADMIN selecciona un tipo de acción específico en el filtro
- **THEN** el sistema muestra solo los registros de ese tipo de acción

### Requirement: Detalle de registro de auditoría
El sistema SHALL permitir expandir o acceder al detalle completo de un registro de auditoría individual.

#### Scenario: Ver detalle de registro
- **WHEN** el ADMIN hace clic en una fila del log
- **THEN** el sistema muestra el detalle completo del registro con todos los campos
