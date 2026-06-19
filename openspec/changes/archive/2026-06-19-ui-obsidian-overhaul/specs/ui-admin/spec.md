## ADDED Requirements

### Requirement: Gestión de usuarios (ABM)
`UsuariosPage` SHALL implementar la tabla de usuarios del tenant con paginación, búsqueda por nombre/email, y acciones de crear, editar y desactivar. El modal de creación/edición SHALL usar React Hook Form + Zod.

#### Scenario: Tabla con usuarios
- **WHEN** existen usuarios en el tenant
- **THEN** se muestran en tabla con columnas: nombre, email, rol, estado, acciones

#### Scenario: Crear usuario
- **WHEN** el admin completa el formulario y confirma
- **THEN** el usuario se crea y aparece en la tabla sin recargar la página

#### Scenario: Desactivar usuario
- **WHEN** el admin hace click en "Desactivar" y confirma en el dialog
- **THEN** el usuario pasa a estado inactivo (soft delete — no se borra)

---

### Requirement: Gestión de estructura académica (Carreras, Cohortes, Materias)
`CarrerasPage`, `CohortesPage` y `MateriasPage` SHALL seguir el patrón `dashboard-crud-page`: tabla paginada + modal de formulario + confirm dialog de borrado. Todas usan el DS para sus componentes de UI.

#### Scenario: Crear registro
- **WHEN** el admin completa el formulario en el modal y confirma
- **THEN** el registro se crea y la tabla se actualiza via TanStack Query invalidation

#### Scenario: Intentar borrar con dependencias
- **WHEN** el admin intenta borrar una carrera con cohortes activas
- **THEN** el backend devuelve error y se muestra mensaje descriptivo en el modal

---

### Requirement: Estructura académica visual
`EstructuraAcademicaPage` SHALL mostrar la jerarquía Carrera → Cohorte → Materia de forma visual (árbol o acordeón). Permite navegación a cada nivel.

#### Scenario: Vista de árbol
- **WHEN** el admin accede a la estructura
- **THEN** se muestra la jerarquía completa con collapse/expand por nivel

---

### Requirement: Log de auditoría
`AuditoriaPage` SHALL mostrar el log de eventos del tenant con filtros por: fecha, usuario, tipo de evento. Los eventos SHALL mostrarse en orden cronológico descendente con tipografía monospace para timestamps.

#### Scenario: Filtrar por tipo de evento
- **WHEN** el admin selecciona un tipo de evento en el filtro
- **THEN** la tabla se actualiza mostrando solo esos eventos

#### Scenario: Sin eventos en el rango
- **WHEN** los filtros no retornan eventos
- **THEN** se muestra `EmptyState` con sugerencia de ampliar el rango de fechas

---

### Requirement: Métricas del tenant
`MetricasPage` SHALL mostrar KPIs globales del tenant: total alumnos, alumnos activos, porcentaje de riesgo, promedio de progreso. Usa StatCards del DS. Los datos son de solo lectura.

#### Scenario: Vista de métricas
- **WHEN** el admin accede a métricas
- **THEN** se muestran StatCards con valores actualizados y un período de referencia visible
