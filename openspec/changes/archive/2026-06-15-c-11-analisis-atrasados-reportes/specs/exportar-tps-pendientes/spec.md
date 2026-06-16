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

### Requirement: Resultados exportables en formato estructurado

El sistema SHALL devolver los resultados en formato JSON estructurado, listo para ser convertido a CSV/XLSX por el frontend o middleware de exportación. Cada fila representa una entrega sin corregir.

#### Scenario: Estructura de respuesta
- **WHEN** el endpoint devuelve resultados exitosos
- **THEN** cada ítem incluye: `alumno_id`, `alumno_nombre`, `alumno_legajo`, `actividad`, `fecha_finalizacion`, `materia_id`, `comision`
