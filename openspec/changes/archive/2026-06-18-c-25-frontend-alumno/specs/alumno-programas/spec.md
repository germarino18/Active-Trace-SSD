## ADDED Requirements

### Requirement: Listado de programas por materia
El sistema SHALL mostrar al alumno los programas de las materias que cursa.

#### Scenario: Listado muestra programas disponibles
- **WHEN** el alumno autenticado accede a `/alumno/programas`
- **THEN** el sistema MUST mostrar una lista de materias con su programa asociado
- **AND** cada item MUST incluir: nombre de materia, nombre del programa, fecha de publicación, enlace de descarga si tiene archivo

#### Scenario: Programa sin archivo muestra estado
- **WHEN** el programa de una materia no tiene `referencia_archivo`
- **THEN** el sistema MUST mostrar "Sin programa cargado" en lugar del enlace de descarga

### Requirement: Calendario de fechas académicas
El sistema SHALL mostrar al alumno un calendario con las fechas académicas (parciales, TP, coloquios) de sus materias.

#### Scenario: Calendario muestra fechas del alumno
- **WHEN** el alumno autenticado accede a `/alumno/fechas`
- **THEN** el sistema MUST mostrar las fechas académicas de las materias que cursa
- **AND** cada fecha MUST incluir: materia, tipo (Parcial/TP/Coloquio), fecha, descripción

#### Scenario: Calendario vacío
- **WHEN** no hay fechas académicas cargadas
- **THEN** el sistema MUST mostrar "No hay fechas académicas cargadas"
