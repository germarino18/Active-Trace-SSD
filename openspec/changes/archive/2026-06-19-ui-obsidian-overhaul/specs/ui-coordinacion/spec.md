## ADDED Requirements

### Requirement: Gestión de equipos docentes
`EquiposListPage` y `EquipoDetallePage` SHALL listar y detallar los equipos docentes. `ClonarEquipoPage` SHALL permitir clonar un equipo a un nuevo período. `AsignacionIndividualPage` y `AsignacionMasivaPage` SHALL gestionar la asignación de profesores/tutores a materias.

#### Scenario: Lista de equipos
- **WHEN** el coordinador accede a equipos
- **THEN** se listan con nombre, período, cantidad de miembros y estado

#### Scenario: Clonar equipo
- **WHEN** el coordinador selecciona un equipo y elige "Clonar"
- **THEN** se muestra formulario para seleccionar el nuevo período y confirmar

#### Scenario: Asignación masiva
- **WHEN** el coordinador carga el CSV de asignaciones y confirma
- **THEN** se procesan las asignaciones y se muestra resumen de éxitos/errores

---

### Requirement: Gestión de encuentros
`EncuentrosListPage`, `EncuentroCrearPage` y `EncuentroDetallePage` SHALL cubrir el ciclo completo de encuentros (clases sincrónicas). La lista SHALL incluir filtros por estado (pendiente/realizado/cancelado).

#### Scenario: Crear encuentro
- **WHEN** el coordinador completa el formulario de nuevo encuentro
- **THEN** el encuentro aparece en la lista con estado "Pendiente"

#### Scenario: Filtrar por estado
- **WHEN** el coordinador selecciona filtro "Realizados"
- **THEN** la lista muestra solo encuentros con estado realizado

---

### Requirement: Gestión de convocatorias (coloquios)
`ConvocatoriasListPage`, `ConvocatoriaCrearPage` y `ConvocatoriaDetallePage` SHALL gestionar las convocatorias a coloquios. El detalle SHALL mostrar la lista de alumnos inscriptos.

#### Scenario: Lista de convocatorias
- **WHEN** el coordinador accede
- **THEN** se listan con nombre, fecha, materia y cantidad de inscriptos

#### Scenario: Crear convocatoria
- **WHEN** el coordinador completa nombre, fecha y materia
- **THEN** la convocatoria se crea en estado "Abierta"

---

### Requirement: Gestión de tareas del equipo
`TareasListPage`, `TareaCrearPage` y `TareaDetallePage` SHALL gestionar tareas asignables a miembros del equipo. `MisTareasPage` muestra las tareas propias del coordinador.

#### Scenario: Crear tarea con asignado
- **WHEN** el coordinador crea una tarea y selecciona un asignado
- **THEN** la tarea aparece en el listado y en MisTareasPage del asignado

#### Scenario: Tarea vencida
- **WHEN** la fecha límite de una tarea pasó sin completarse
- **THEN** se muestra con badge "Vencida" en color error

---

### Requirement: Programas y avisos
`ProgramasListPage`, `ProgramaCrearPage`, `AvisosListPage`, `AvisoCrearPage` y `AvisoEditarPage` SHALL seguir el patrón CRUD estándar del DS. Los avisos pueden ser de tipo informativo o urgente (con badge de color diferente).

#### Scenario: Aviso urgente
- **WHEN** el coordinador crea un aviso con tipo "Urgente"
- **THEN** el aviso aparece con badge rojo en la lista y en la vista del alumno

---

### Requirement: Fechas académicas y vigencia
`FechasAcademicasPage` SHALL mostrar el calendario de fechas importantes del período. `ModificarVigenciaPage` SHALL permitir extender o cerrar el período de vigencia de una comisión.

#### Scenario: Ver fechas del período
- **WHEN** el coordinador accede a fechas académicas
- **THEN** se muestra la lista de fechas ordenada cronológicamente

---

### Requirement: Monitores de coordinación
`MonitorCoordinacionPage` y `MonitorGeneralPage` SHALL mostrar dashboards de seguimiento. El monitor de coordinación es scoped al equipo del coordinador; el general es para todo el tenant.

#### Scenario: Monitor de coordinación
- **WHEN** el coordinador accede
- **THEN** ve métricas de su equipo: alumnos, tutores, encuentros, tareas pendientes

#### Scenario: Monitor general (solo ADMIN/NEXO)
- **WHEN** un usuario con rol ADMIN o NEXO accede
- **THEN** ve métricas de todos los equipos del tenant
