## MODIFIED Requirements

### Requirement: Detectar alumnos atrasados por materia (F2.2, RN-06)

El sistema SHALL permitir consultar los alumnos atrasados de una materia. La clasificación de "aprobado / atrasado" SHALL anclarse **exclusivamente** al campo booleano `aprobado` de cada `Calificacion`, y SHALL ser idéntica en todas las superficies (panel de atrasados, métricas agregadas, dashboard del profesor). El umbral configurado (`umbral_pct`, `valores_aprobatorios`) NO gobierna esta clasificación.

Para un conjunto de **actividades esperadas** `E` de un dictado, un alumno está **APROBADO** si y solo si, para toda actividad `a ∈ E`, existe una fila `Calificacion` del alumno para `a` con `aprobado == True`. En cualquier otro caso está **ATRASADO**. Específicamente, un alumno es atrasado si cumple AL MENOS UNA condición: tiene una actividad esperada sin fila de calificación (faltante) o tiene una fila con `aprobado == False` (desaprobada). El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Consulta exitosa de atrasados
- **WHEN** un usuario con `atrasados:ver` consulta los atrasados de una materia
- **THEN** el sistema devuelve lista de alumnos atrasados con nombre, legajo, actividades faltantes y actividades desaprobadas

#### Scenario: Sin alumnos atrasados
- **WHEN** todos los alumnos de la materia tienen una fila con `aprobado == True` en cada actividad esperada
- **THEN** el sistema devuelve lista vacía

#### Scenario: Atrasado por actividad faltante
- **WHEN** un alumno no tiene fila `Calificacion` para una actividad esperada de la materia
- **THEN** el sistema lo incluye como atrasado con la actividad listada como faltante

#### Scenario: Atrasado por fila con aprobado=False
- **WHEN** un alumno tiene una fila `Calificacion` con `aprobado == False`
- **THEN** el sistema lo incluye como atrasado con esa actividad listada como desaprobada, **independientemente de su nota numérica o textual**

#### Scenario: Aprobado con nota baja pero aprobado=True
- **WHEN** un alumno tiene una fila con `nota_numerica` por debajo del umbral configurado pero `aprobado == True`, y tiene `aprobado == True` en todas las demás actividades esperadas
- **THEN** el sistema lo clasifica como **aprobado** (la nota no anula la decisión de aprobación)

#### Scenario: Atrasado con nota alta pero aprobado=False
- **WHEN** un alumno tiene una fila con `nota_numerica` por encima del umbral configurado pero `aprobado == False`
- **THEN** el sistema lo clasifica como **atrasado** (con esa actividad como desaprobada)

#### Scenario: Alumno sin ninguna calificación
- **WHEN** un alumno no tiene ninguna fila `Calificacion` para las actividades esperadas
- **THEN** el sistema lo clasifica como atrasado, con todas las actividades esperadas listadas como faltantes

#### Scenario: Mezcla de faltante y desaprobada
- **WHEN** un alumno tiene una actividad esperada sin fila y otra fila con `aprobado == False`
- **THEN** el sistema lo clasifica como atrasado, listando la primera como faltante y la segunda como desaprobada

#### Scenario: Paridad entre métricas y panel de atrasados
- **WHEN** se calculan las métricas agregadas (`aprobados` / `atrasados`) y la clasificación nominal de alumnos sobre el mismo conjunto de calificaciones, sin actividades faltantes
- **THEN** el conteo de aprobados de las métricas coincide exactamente con la cantidad de alumnos clasificados como aprobado en el panel, y los atrasados también coinciden

#### Scenario: Consulta rechazada sin permiso
- **WHEN** un usuario sin `atrasados:ver` intenta consultar atrasados
- **THEN** el sistema responde 403 Forbidden

### Requirement: Reportes rápidos por materia (F2.4, RN-03/RN-06)

El sistema SHALL proveer una vista consolidada con métricas clave de una materia: total de alumnos, cantidad de aprobados, cantidad de atrasados, cantidad de actividades, promedio general. El conteo de `aprobados` / `atrasados` SHALL usar la regla del campo booleano `aprobado` (idéntica a la detección de atrasados), de modo que coincida con el panel de atrasados. El campo `promedio_general` SHALL seguir calculándose como promedio simple de las `nota_numerica` presentes, sin verse afectado por este cambio. El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Reporte con datos completos
- **WHEN** un usuario consulta los reportes rápidos de una materia
- **THEN** el sistema devuelve: total_alumnos, aprobados, atrasados, total_actividades, promedio_general

#### Scenario: Aprobados coinciden con el panel de atrasados
- **WHEN** se consulta el reporte rápido y el panel de atrasados de la misma materia (sin actividades faltantes)
- **THEN** `aprobados` del reporte es igual a la cantidad de alumnos en estado aprobado del panel, y `atrasados` coincide con el resto

#### Scenario: Reporte sin datos
- **WHEN** no existen `Calificacion` ni `UmbralMateria` para la materia
- **THEN** el sistema devuelve métricas en cero con indicador `sin_datos: true`

#### Scenario: promedio_general no cambia con la nueva regla
- **WHEN** se calcula el reporte de una materia con notas numéricas
- **THEN** `promedio_general` es el promedio simple de las `nota_numerica` presentes, sin influencia del cambio en la clasificación aprobado/atrasado
