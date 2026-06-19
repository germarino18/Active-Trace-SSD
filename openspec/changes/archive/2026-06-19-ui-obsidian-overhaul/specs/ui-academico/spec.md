## ADDED Requirements

### Requirement: Lista de materias del profesor con navegación a tabs
`MateriaListPage` (acceso por rol PROFESOR) SHALL mostrar las materias asignadas al usuario como cards navegables. Al seleccionar una materia, se navega a la vista de gestión con 5 tabs. Esta es la vista central del flujo académico del profesor.

#### Scenario: Profesor con materias asignadas
- **WHEN** el profesor autenticado tiene materias en su dictado
- **THEN** se muestran como cards con nombre de materia, cohorte, y conteo de alumnos

#### Scenario: Sin materias asignadas
- **WHEN** el profesor no tiene materias en el período activo
- **THEN** se muestra `EmptyState` con mensaje descriptivo

---

### Requirement: Layout de 5 tabs por materia
Al acceder a una materia, SHALL mostrarse un layout de tabs con las 5 funcionalidades del flujo académico: Importar Calificaciones, Alumnos Atrasados, Comunicar, Entregas Pendientes, Monitor. El tab activo se persiste en query param para que la URL sea compartible.

#### Scenario: Navegación entre tabs
- **WHEN** el profesor selecciona un tab
- **THEN** el contenido cambia y la URL refleja el tab activo (ej: `?tab=atrasados`)

#### Scenario: URL con tab activo
- **WHEN** se carga la URL con `?tab=comunicar`
- **THEN** la tab "Comunicar" está activa al montar el componente

---

### Requirement: Tab Importar Calificaciones
`ImportarCalificacionesPage` SHALL permitir cargar un archivo CSV de Moodle con drag-and-drop y file picker. MUST mostrar una tabla de preview antes de confirmar la importación. El botón de confirmar SHALL estar deshabilitado si el preview tiene errores.

#### Scenario: Drag & drop de archivo válido
- **WHEN** el profesor arrastra un CSV válido al área de carga
- **THEN** se muestra la tabla de preview con las filas a importar

#### Scenario: Archivo con errores de formato
- **WHEN** el CSV tiene columnas incorrectas o datos inválidos
- **THEN** se muestran las filas con error destacadas en rojo y el botón de confirmar está deshabilitado

#### Scenario: Importación confirmada
- **WHEN** el profesor confirma la importación
- **THEN** se muestra progreso y al finalizar: conteo de importados/errores

---

### Requirement: Tab Alumnos Atrasados
`VistaAtrasadosPage` SHALL mostrar la lista de alumnos que están por debajo del umbral de actividades completadas. MUST incluir: nombre, legajo, porcentaje de progreso, actividades faltantes. Permite selección individual o masiva para comunicar.

#### Scenario: Lista de atrasados
- **WHEN** hay alumnos por debajo del umbral
- **THEN** se muestran ordenados por porcentaje de progreso ascendente

#### Scenario: Sin alumnos atrasados
- **WHEN** todos los alumnos están al día
- **THEN** se muestra `EmptyState` con mensaje positivo

#### Scenario: Selección para comunicar
- **WHEN** el profesor selecciona alumnos y hace click en "Comunicar"
- **THEN** navega a la tab de Comunicar con los alumnos pre-seleccionados

---

### Requirement: Tab Comunicar a Atrasados
`ComunicacionAtrasadosPage` SHALL permitir redactar y enviar mensajes a los alumnos seleccionados. MUST mostrar lista de destinatarios (editable), campo de asunto, cuerpo del mensaje, y preview antes de enviar.

#### Scenario: Preview de comunicación
- **WHEN** el profesor completa el mensaje y hace click en "Preview"
- **THEN** se muestra un modal con el mensaje tal como lo verá el alumno

#### Scenario: Envío confirmado
- **WHEN** el profesor confirma el envío
- **THEN** las comunicaciones se encolan y se muestra feedback de cuántas se enviaron

---

### Requirement: Tab Entregas Pendientes
`EntregasSinCorregirPage` SHALL listar las entregas de los alumnos que aún no tienen corrección. Cada fila SHALL mostrar: alumno, actividad, fecha de entrega, link a la entrega.

#### Scenario: Con entregas pendientes
- **WHEN** existen entregas sin corregir
- **THEN** se listan ordenadas por fecha de entrega ascendente

#### Scenario: Sin pendientes
- **WHEN** todas las entregas están corregidas
- **THEN** se muestra `EmptyState` con mensaje positivo

---

### Requirement: Tab Monitor de Seguimiento
`MonitorSeguimientoPage` SHALL mostrar un resumen visual del estado del grupo: distribución por condición, progreso promedio por actividad, alumnos en riesgo. Usa StatCards del DS para los KPIs.

#### Scenario: Vista de métricas del grupo
- **WHEN** el profesor accede al Monitor
- **THEN** se muestran StatCards con: total alumnos, % regulares, % en riesgo, promedio general
