## ADDED Requirements

### Requirement: Exportar trabajos prácticos sin corregir (F2.6, RN-07/RN-08)

El sistema SHALL permitir exportar el listado de entregas detectadas como pendientes de corrección. La detección cruza el reporte de finalización del LMS (actividades finalizadas por el alumno) contra las calificaciones importadas. SOLO se incluyen actividades de escala textual (RN-08). El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Exportación exitosa con datos
- **WHEN** un usuario consulta `GET /api/v1/analisis/tps-sin-corregir/export?materia_id=X`
- **THEN** el sistema devuelve listado de entregas sin corregir con: alumno, actividad, fecha de finalización

#### Scenario: Sin entregas pendientes
- **WHEN** todas las entregas finalizadas tienen calificación registrada
- **THEN** el sistema devuelve lista vacía

#### Scenario: Filtro solo actividades textuales
- **WHEN** existen finalizaciones para actividades numéricas sin calificar
- **THEN** esas actividades NO se incluyen en el resultado (RN-08)

#### Scenario: Sin reporte de finalización LMS
- **WHEN** no se ha importado el reporte de finalización LMS para la materia
- **THEN** el sistema responde 400 con mensaje "Se requiere importar reporte de finalización LMS primero"

### Requirement: Monitor general de alumnos — vista coordinación/admin (F2.7)

El sistema SHALL proveer una vista transversal de todos los alumnos del tenant con su estado de actividades. Los filtros disponibles son: materia, regional, comisión, búsqueda libre por alumno, estado de actividad (aprobada/desaprobada/faltante), criterio de clasificación. El endpoint SHALL estar gated por `atrasados:ver` y limitado a roles COORDINADOR y ADMIN.

#### Scenario: Consulta sin filtros
- **WHEN** un COORDINADOR consulta `GET /api/v1/analisis/monitor/general`
- **THEN** el sistema devuelve todos los alumnos del tenant con su estado global

#### Scenario: Consulta filtrada por materia y comisión
- **WHEN** un COORDINADOR consulta con `materia_id=X&comision_id=Y`
- **THEN** el sistema devuelve solo alumnos de esa materia y comisión

#### Scenario: Consulta filtrada por estado
- **WHEN** un ADMIN consulta con `estado=atrasado`
- **THEN** el sistema devuelve solo alumnos atrasados según RN-06

#### Scenario: Consulta con búsqueda de alumno
- **WHEN** un COORDINADOR consulta con `q=García`
- **THEN** el sistema devuelve alumnos cuyo nombre o apellido contiene "García"

#### Scenario: Acceso denegado a TUTOR
- **WHEN** un TUTOR intenta acceder al monitor general
- **THEN** el sistema responde 403 Forbidden
