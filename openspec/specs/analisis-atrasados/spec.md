## ADDED Requirements

### Requirement: Detectar alumnos atrasados por materia (F2.2, RN-06)

El sistema SHALL permitir consultar los alumnos atrasados de una materia. Un alumno se considera atrasado si cumple AL MENOS UNA de estas condiciones: tiene actividades sin entregar (no existe Calificacion para alguna actividad esperada) o tiene nota registrada inferior al umbral configurado (nota_numerica < umbral_pct * nota_maxima / 100, o nota_textual fuera de valores_aprobatorios). El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Consulta exitosa de atrasados
- **WHEN** un usuario con `atrasados:ver` consulta `GET /api/v1/analisis/atrasados?materia_id=X`
- **THEN** el sistema devuelve lista de alumnos atrasados con nombre, legajo, actividades faltantes y actividades desaprobadas

#### Scenario: Sin alumnos atrasados
- **WHEN** todos los alumnos de la materia tienen todas las actividades aprobadas
- **THEN** el sistema devuelve lista vacía

#### Scenario: Atrasado por actividades faltantes
- **WHEN** un alumno no tiene Calificacion para una actividad esperada de la materia
- **THEN** el sistema lo incluye como atrasado con la actividad listada como faltante

#### Scenario: Atrasado por nota inferior al umbral
- **WHEN** un alumno tiene Calificacion con nota_numerica=4.0 y el umbral de la materia es 60%
- **THEN** el sistema lo incluye como atrasado con la actividad listada como desaprobada

#### Scenario: Consulta rechazada sin permiso
- **WHEN** un usuario sin `atrasados:ver` intenta consultar atrasados
- **THEN** el sistema responde 403 Forbidden

### Requirement: Ranking de actividades aprobadas por materia (F2.3, RN-09)

El sistema SHALL permitir consultar el ranking de alumnos ordenado por cantidad de actividades aprobadas descendente. Solo se incluyen alumnos con AL MENOS UNA actividad aprobada (RN-09). El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Ranking exitoso
- **WHEN** un usuario consulta `GET /api/v1/analisis/ranking?materia_id=X`
- **THEN** el sistema devuelve tabla ordenada con alumno, cantidad de aprobadas y total de actividades

#### Scenario: Ranking excluye alumnos sin aprobadas
- **WHEN** un alumno tiene 0 actividades aprobadas
- **THEN** el alumno no aparece en el ranking

#### Scenario: Empate en ranking
- **WHEN** dos alumnos tienen la misma cantidad de aprobadas
- **THEN** se ordenan alfabéticamente por apellido y nombre

#### Scenario: Materia sin calificaciones
- **WHEN** no existen Calificacion para la materia consultada
- **THEN** el sistema devuelve lista vacía

### Requirement: Reportes rápidos por materia (F2.4, RN-03/RN-06)

El sistema SHALL proveer una vista consolidada con métricas clave de una materia: total de alumnos, cantidad de aprobados, cantidad de atrasados, cantidad de actividades, promedio general. El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Reporte con datos completos
- **WHEN** un usuario consulta `GET /api/v1/analisis/reportes/materia/{materia_id}`
- **THEN** el sistema devuelve: total_alumnos, aprobados, atrasados, total_actividades, promedio_general

#### Scenario: Reporte sin datos
- **WHEN** no existen Calificacion ni UmbralMateria para la materia
- **THEN** el sistema devuelve métricas en cero con indicador `sin_datos: true`

#### Scenario: Reporte usa umbral configurado o default
- **WHEN** existe UmbralMateria para el dictado
- **THEN** el sistema usa ese umbral; si no existe, usa 60% como default

### Requirement: Notas finales agrupadas por alumno (F2.5)

El sistema SHALL agrupar las actividades configuradas de una materia y calcular una nota final por alumno. La nota final es el promedio simple de las notas numéricas de las actividades configuradas. Si una actividad no tiene nota numérica, se excluye del cálculo. El endpoint SHALL estar gated por `atrasados:ver`.

#### Scenario: Cálculo exitoso de nota final
- **WHEN** un usuario consulta `GET /api/v1/analisis/notas-finales?materia_id=X`
- **THEN** el sistema devuelve lista de alumnos con nota final calculada y cantidad de actividades consideradas

#### Scenario: Alumno sin actividades configuradas
- **WHEN** un alumno no tiene Calificacion para ninguna actividad configurada
- **THEN** el sistema devuelve `nota_final: null` para ese alumno

#### Scenario: Mezcla de notas numéricas y textuales
- **WHEN** un alumno tiene actividades con nota numérica y otras con solo nota textual
- **THEN** solo las numéricas se usan en el promedio; las textuales se excluyen
