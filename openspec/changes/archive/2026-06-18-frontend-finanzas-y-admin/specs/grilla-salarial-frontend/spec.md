## ADDED Requirements

### Requirement: Gestión de salario base por rol
El sistema SHALL permitir a FINANZAS (con permiso `liquidaciones:configurar-salarios`) gestionar la tabla de salarios base. Cada registro SHALL incluir: rol (PROFESOR/TUTOR/NEXO/COORDINADOR), importe, fecha de vigencia desde, fecha de vigencia hasta (opcional).

#### Scenario: Listar salarios base
- **WHEN** el usuario FINANZAS accede a la sección "Grilla salarial > Salario base"
- **THEN** el sistema muestra la tabla con todos los salarios base vigentes e históricos

#### Scenario: Crear nuevo salario base
- **WHEN** el usuario FINANZAS completa el formulario de nuevo salario base con rol, importe y vigencia
- **THEN** el sistema crea el registro y lo muestra en la tabla

#### Scenario: Editar salario base
- **WHEN** el usuario FINANZAS edita un salario base existente
- **THEN** el sistema actualiza el registro y los cálculos de liquidaciones futuras usan el nuevo valor

### Requirement: Gestión de plus
El sistema SHALL permitir gestionar adicionales (plus) identificados por clave única, con los campos: clave, rol, descripción, importe, fecha de vigencia desde, fecha de vigencia hasta (opcional).

#### Scenario: Listar plus
- **WHEN** el usuario FINANZAS accede a la sección "Grilla salarial > Plus"
- **THEN** el sistema muestra la tabla de plus con todos los registros

#### Scenario: Crear nuevo plus
- **WHEN** el usuario FINANZAS completa el formulario de nuevo plus
- **THEN** el sistema crea el registro y lo muestra en la tabla

### Requirement: Validación de vigencia
El sistema SHALL validar que no existan solapamientos de vigencia para el mismo rol en salario base o para la misma clave en plus.

#### Scenario: Error por solapamiento de vigencia
- **WHEN** el usuario FINANZAS crea un salario base para un rol con vigencia que solapa una existente
- **THEN** el sistema muestra un error indicando el conflicto de fechas
