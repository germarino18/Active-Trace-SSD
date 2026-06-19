## MODIFIED Requirements

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
- **WHEN** el coordinador completa el formulario
- **THEN** la convocatoria aparece en la lista con estado activo

## ADDED Requirements

### Requirement: Panel de aprobación de comunicaciones en sidebar
El sidebar de COORDINADOR y ADMIN SHALL incluir una entrada "Aprobar Comunicaciones" con ícono de bandeja y badge numérico que indica la cantidad de lotes pendientes de aprobación, navegando a `/comunicaciones/aprobar`.

#### Scenario: Badge con lotes pendientes
- **WHEN** existen N lotes en estado Pendiente de aprobación
- **THEN** el sidebar muestra la entrada "Aprobar Comunicaciones" con un badge que indica N

#### Scenario: Badge ausente sin pendientes
- **WHEN** no existen lotes pendientes
- **THEN** la entrada "Aprobar Comunicaciones" aparece sin badge numérico

#### Scenario: Navegación a la página de aprobación
- **WHEN** el COORDINADOR o ADMIN hace clic en "Aprobar Comunicaciones"
- **THEN** la app navega a `/comunicaciones/aprobar` y renderiza `AprobacionComunicacionesPage`
