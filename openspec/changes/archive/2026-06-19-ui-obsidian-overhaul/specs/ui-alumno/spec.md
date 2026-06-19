## ADDED Requirements

### Requirement: Mis Materias con cards y progreso
`MisMateriasPage` SHALL mostrar todas las materias del alumno en un grid de cards, cada una con: nombre, profesor, condición (regular/libre/promovido) como badge, barra de progreso de actividades y promedio. El diseño SHALL seguir el layout 5-tab de `ui_kits/activia-trace/` del DS.

#### Scenario: Con materias
- **WHEN** el alumno tiene materias inscriptas
- **THEN** se muestran cards en grid 1/2/3 columnas según breakpoint

#### Scenario: Sin materias
- **WHEN** el alumno no tiene materias inscriptas
- **THEN** se muestra `EmptyState` con ícono de escuela y mensaje descriptivo

#### Scenario: Click en card de materia
- **WHEN** el alumno hace click en una card
- **THEN** navega a `/alumno/materias/:id`

---

### Requirement: Detalle de materia con tabs de contenido
`MateriaDetallePage` SHALL implementar un layout de tabs con al menos: Actividades, Calificaciones, y Material. Cada tab carga su contenido de forma lazy.

#### Scenario: Navegación entre tabs
- **WHEN** el alumno clickea una tab
- **THEN** el contenido cambia sin navegar a otra ruta (state local o query param)

#### Scenario: Tab de actividades vacía
- **WHEN** la materia no tiene actividades cargadas
- **THEN** se muestra `EmptyState` dentro del panel de la tab

---

### Requirement: Inbox y detalle de comunicaciones del alumno
`AlumnoInboxPage` SHALL listar comunicaciones recibidas con remitente, asunto, fecha, y badge de estado (leída/no leída). `AlumnoHilo` SHALL mostrar el hilo completo de mensajes de una comunicación.

#### Scenario: Inbox con comunicaciones no leídas
- **WHEN** el alumno tiene comunicaciones sin leer
- **THEN** se destacan visualmente (badge, peso de fuente) diferenciadas de las leídas

#### Scenario: Inbox vacío
- **WHEN** el alumno no tiene comunicaciones
- **THEN** se muestra `EmptyState` con ícono de bandeja

#### Scenario: Abrir hilo
- **WHEN** el alumno hace click en una comunicación del inbox
- **THEN** navega a la vista de hilo y la comunicación se marca como leída

---

### Requirement: Avisos, coloquios, fechas y programas del alumno
Las páginas `MisAvisos`, `MisColoquios`, `MisFechas` y `MisProgramas` SHALL mostrar sus listas con estado vacío apropiado cuando no hay datos. Los items SHALL usar el DS para cards o filas de lista consistentes.

#### Scenario: Lista con datos
- **WHEN** existen registros para el alumno
- **THEN** se muestran en lista o grid usando componentes del DS

#### Scenario: Lista vacía
- **WHEN** no hay registros
- **THEN** se muestra `EmptyState` con mensaje específico al tipo de contenido

---

### Requirement: Mis Comunicaciones
`MisComunicacionesPage` SHALL mostrar el historial completo de comunicaciones del alumno, agrupadas o filtrables por estado. `ComunicacionDetallePage` SHALL mostrar el detalle completo de una comunicación individual.

#### Scenario: Filtrar por estado
- **WHEN** el alumno selecciona un filtro (ej: "No leídas")
- **THEN** la lista se actualiza mostrando solo las comunicaciones del estado seleccionado
