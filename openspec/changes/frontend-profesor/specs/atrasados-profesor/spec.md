## ADDED Requirements

### Requirement: Clasificación de alumnos en Aprobado y Atrasado por el profesor
El sistema SHALL clasificar a los alumnos de un dictado en **Aprobado** o **Atrasado**, reutilizando el cálculo de atrasados existente (faltantes y desaprobadas). Dentro de Atrasado, el sistema MUST distinguir **desaprobado** (existe registro de calificación con nota insuficiente) de **atrasado-null** (no existe registro de calificación para una Actividad cuya `fecha_limite` ya pasó). Una actividad sin `fecha_limite` no produce atrasado-null. La clasificación MUST estar acotada al `tenant_id` de la sesión.

#### Scenario: Alumno aprobado
- **WHEN** un alumno tiene registro y nota suficiente en todas las actividades esperadas y no tiene faltantes vencidos
- **THEN** el sistema lo clasifica como Aprobado

#### Scenario: Atrasado por desaprobado
- **WHEN** un alumno tiene una calificación registrada con nota insuficiente según el umbral
- **THEN** el sistema lo clasifica como Atrasado, subtipo desaprobado

#### Scenario: Atrasado-null por fecha límite vencida
- **WHEN** un alumno no tiene calificación para una Actividad cuya `fecha_limite` ya pasó
- **THEN** el sistema lo clasifica como Atrasado, subtipo atrasado-null, indicando la actividad faltante

#### Scenario: Faltante sin fecha límite no es atrasado-null
- **WHEN** un alumno no tiene calificación para una actividad que no tiene `fecha_limite` definida
- **THEN** el sistema no lo clasifica como atrasado-null por esa actividad

### Requirement: Comunicado a alumnos atrasado-null
El sistema SHALL permitir al PROFESOR generar un comunicado dirigido a los alumnos atrasado-null indicando la actividad y la materia, utilizando el pipeline de comunicaciones existente (preview, envío masivo y aprobación). La identidad del emisor y el `tenant_id` MUST derivarse de la sesión. Al ser dominio CRÍTICO, la generación del comunicado MUST quedar sujeta al circuito de aprobación de comunicaciones.

#### Scenario: Generar comunicado a atrasado-null
- **WHEN** el PROFESOR dispara un comunicado para los alumnos atrasado-null de un dictado
- **THEN** el sistema prepara el comunicado referenciando la actividad y la materia, y lo encola en el pipeline de comunicaciones con su circuito de aprobación

#### Scenario: Comunicado acotado al tenant
- **WHEN** se intenta generar el comunicado para un dictado de otro tenant
- **THEN** el sistema responde 404 y no genera nada

### Requirement: Frontend de atrasados del profesor
El frontend SHALL mostrar en el tab de atrasados del dictado la separación entre Aprobado y Atrasado, y dentro de Atrasado distinguir desaprobado de atrasado-null, ofreciendo la acción de generar comunicado para los atrasado-null. La vista MUST reutilizar los componentes académicos de atrasados/comunicación existentes cuando apliquen.

#### Scenario: Vista separa estados
- **WHEN** el PROFESOR abre el tab de atrasados de un dictado
- **THEN** se muestran los alumnos separados en Aprobado y Atrasado, distinguiendo dentro de Atrasado los subtipos desaprobado y atrasado-null

#### Scenario: Acción de comunicado a atrasado-null
- **WHEN** el PROFESOR elige generar comunicado para los atrasado-null
- **THEN** el frontend dispara el flujo de comunicación referenciando actividad y materia
