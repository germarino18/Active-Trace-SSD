## ADDED Requirements

### Requirement: Tablón de avisos del alumno
El sistema SHALL mostrar al alumno los avisos publicados cuyo scope incluya su rol, materia o cohorte.

#### Scenario: Tablón muestra avisos aplicables
- **WHEN** el alumno autenticado accede a `/alumno/avisos`
- **THEN** el sistema MUST mostrar los avisos activos (dentro de vigencia) cuyo scope sea Global, o que coincidan con la materia/cohorte del alumno, o cuyo `role_target` incluya ALUMNO
- **AND** los avisos MUST mostrarse ordenados por prioridad (sort) y fecha

#### Scenario: Aviso leído no se muestra como pendiente
- **WHEN** el alumno ya confirmó un aviso (acknowledgment)
- **THEN** el aviso MUST mostrarse como "Leído" o no mostrarse como pendiente

#### Scenario: Aviso fuera de vigencia no se muestra
- **WHEN** el aviso tiene `vigencia_hasta` anterior a la fecha actual
- **THEN** el aviso MUST NO aparecer en el tablón

#### Scenario: Sin avisos muestra empty state
- **WHEN** no hay avisos activos para el alumno
- **THEN** el sistema MUST mostrar "No hay avisos pendientes"

### Requirement: Confirmación de avisos (acknowledgment)
El sistema SHALL permitir al alumno confirmar la lectura de un aviso que tenga `require_ack = true`.

#### Scenario: Confirmación exitosa
- **WHEN** el alumno hace clic en "Confirmar lectura" en un aviso con `require_ack`
- **THEN** el sistema MUST crear un registro de `AcknowledgmentAviso`
- **AND** el aviso MUST desaparecer del tablón de pendientes

#### Scenario: Confirmación no disponible para avisos sin require_ack
- **WHEN** el aviso tiene `require_ack = false`
- **THEN** el sistema MUST NO mostrar el botón "Confirmar lectura"
