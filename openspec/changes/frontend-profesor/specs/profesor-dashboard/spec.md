## ADDED Requirements

### Requirement: Dashboard general del PROFESOR con métricas reales
El sistema SHALL exponer un endpoint que devuelva las métricas agregadas del PROFESOR autenticado: cantidad de materias asignadas, cantidad de alumnos, encuentros y atrasados totales. El `usuario_id` y el `tenant_id` MUST derivarse EXCLUSIVAMENTE de la sesión JWT verificada, nunca de la petición. El alcance MUST limitarse a los dictados donde el usuario tiene una `Asignacion` con `rol = PROFESOR` vigente (estado derivado por fechas). Todas las consultas MUST estar acotadas al `tenant_id` de la sesión.

#### Scenario: Profesor ve métricas de sus dictados
- **WHEN** un PROFESOR autenticado consulta su dashboard
- **THEN** el sistema devuelve materias asignadas, alumnos, encuentros y atrasados totales calculados sólo sobre los dictados con asignación PROFESOR vigente del usuario y su tenant

#### Scenario: No incluye dictados de otros profesores
- **WHEN** existen dictados con asignaciones de otros profesores en el mismo tenant
- **THEN** las métricas del usuario no contabilizan datos de dictados ajenos a sus asignaciones

#### Scenario: Asignación vencida no cuenta
- **WHEN** el profesor tiene una asignación PROFESOR vencida sobre un dictado
- **THEN** ese dictado no se incluye en las métricas del dashboard

#### Scenario: Profesor sin dictados
- **WHEN** un PROFESOR sin asignaciones vigentes consulta su dashboard
- **THEN** el sistema responde métricas en cero sin error

### Requirement: Panel de métricas por dictado
El sistema SHALL exponer un endpoint que devuelva las métricas de un dictado (materia × carrera × cohorte) con exactamente los campos `total_alumnos`, `aprobados`, `atrasados`, `total_actividades`, `promedio_general` y `sin_datos`, reutilizando el cálculo de métricas de materia existente. El acceso MUST estar acotado al `tenant_id` de la sesión y requerir que el dictado pertenezca al alcance del usuario.

#### Scenario: Métricas de un dictado del profesor
- **WHEN** un PROFESOR consulta las métricas de un dictado donde tiene asignación vigente
- **THEN** el sistema devuelve los seis campos de métricas calculados sobre las calificaciones de ese dictado

#### Scenario: Dictado sin calificaciones
- **WHEN** el dictado no tiene calificaciones cargadas
- **THEN** el sistema devuelve `sin_datos = true` y los contadores en cero

#### Scenario: Dictado de otro tenant
- **WHEN** se solicitan métricas de un dictado que no pertenece al tenant de la sesión
- **THEN** el sistema responde 404 y no entrega datos

### Requirement: Frontend de vista PROFESOR consolidada
El frontend SHALL ofrecer al PROFESOR un dashboard general con las métricas reales del endpoint de dashboard (sin valores hardcodeados) y un panel por dictado que muestre las seis métricas y dé acceso por tabs a alumnos, calificaciones/actividades, atrasados, equipo docente, avisos propios, tareas propias y coloquios propios. El frontend MUST obtener los datos vía hooks de servicio y MUST reutilizar los componentes académicos existentes cuando apliquen.

#### Scenario: Dashboard general muestra datos reales
- **WHEN** un PROFESOR abre su dashboard general
- **THEN** se muestran materias asignadas, alumnos, encuentros y atrasados totales obtenidos del endpoint, no marcadores estáticos

#### Scenario: Navegación al panel del dictado
- **WHEN** el PROFESOR selecciona un dictado
- **THEN** se muestra el panel con las seis métricas y los tabs de gestión del dictado
