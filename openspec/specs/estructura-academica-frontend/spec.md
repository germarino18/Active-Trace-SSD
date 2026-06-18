# estructura-academica-frontend Specification

## Purpose
TBD - created by archiving change frontend-finanzas-y-admin. Update Purpose after archive.
## Requirements
### Requirement: ABM de carreras
El sistema SHALL permitir al ADMIN listar, crear, editar y cambiar el estado (activa/inactiva) de carreras. Cada carrera SHALL tener: código identificador y nombre descriptivo.

#### Scenario: Listar carreras
- **WHEN** el ADMIN accede a la sección "Estructura académica > Carreras"
- **THEN** el sistema muestra la tabla de carreras con código, nombre y estado

#### Scenario: Crear carrera
- **WHEN** el ADMIN completa el formulario de nueva carrera con código y nombre
- **THEN** el sistema crea la carrera y la muestra en el listado

#### Scenario: Cambiar estado de carrera
- **WHEN** el ADMIN cambia el estado de una carrera de activa a inactiva
- **THEN** el sistema actualiza el estado y la tabla refleja el cambio

### Requirement: ABM de cohortes
El sistema SHALL permitir al ADMIN listar, crear, editar y cambiar el estado de cohortes. Cada cohorte SHALL tener: nombre, año de inicio, fechas de vigencia (desde/hasta), estado.

#### Scenario: Listar cohortes
- **WHEN** el ADMIN accede a la sección "Estructura académica > Cohortes"
- **THEN** el sistema muestra la tabla de cohortes con nombre, año, vigencia y estado

#### Scenario: Crear cohorte
- **WHEN** el ADMIN completa el formulario de nueva cohorte con nombre, año de inicio y vigencia
- **THEN** el sistema crea la cohorte y la muestra en el listado

### Requirement: ABM de materias
El sistema SHALL permitir al ADMIN las operaciones ABM y cambio de estado sobre las tablas del modelo académico: materias, dictados y comisiones.

#### Scenario: Listar materias
- **WHEN** el ADMIN accede a la sección "Estructura académica > Materias"
- **THEN** el sistema muestra la tabla de materias con nombre, código y estado

#### Scenario: Crear materia
- **WHEN** el ADMIN completa el formulario de nueva materia
- **THEN** el sistema crea la materia y la muestra en el listado

### Requirement: Gestión de programas de materias
El sistema SHALL permitir al ADMIN y COORDINADOR subir y asociar el programa oficial de cada materia para una combinación específica de carrera × cohorte.

#### Scenario: Subir programa de materia
- **WHEN** el ADMIN selecciona una materia, carrera y cohorte, y sube un archivo de programa
- **THEN** el sistema asocia el programa a la combinación y lo muestra como disponible

### Requirement: Gestión de fechas de evaluaciones
El sistema SHALL permitir al COORDINADOR y ADMIN registrar y editar las fechas de evaluaciones (parciales, TP, coloquios) por materia, cohorte y número de instancia.

#### Scenario: Registrar fecha de evaluación
- **WHEN** el ADMIN o COORDINADOR completa el formulario de nueva evaluación con materia, tipo, instancia y fecha
- **THEN** el sistema registra la evaluación y la muestra en el calendario

#### Scenario: Ver calendario de evaluaciones
- **WHEN** el ADMIN accede a la vista de calendario de evaluaciones
- **THEN** el sistema muestra las evaluaciones registradas en formato visual por fecha

