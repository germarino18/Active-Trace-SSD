## ADDED Requirements

### Requirement: Métricas del tenant conectadas a backend real
`MetricasPage` SHALL consumir datos del endpoint `GET /api/admin/metricas` en lugar de datos mock/data estática. Los KPIs mostrados SHALL ser: total alumnos, alumnos activos, porcentaje en riesgo, promedio de progreso, total docentes, total materias activas.

#### Scenario: Métricas cargadas desde API
- **WHEN** el ADMIN accede a MetricasPage
- **THEN** los StatCards muestran datos obtenidos de `GET /api/admin/metricas`

#### Scenario: Error en API de métricas
- **WHEN** el endpoint de métricas falla
- **THEN** se muestra un estado de error con opción de reintentar

### Requirement: Página de Dictados en el frontend
El panel ADMIN SHALL incluir una página `DictadosPage` que liste los dictados del tenant con columnas: materia, carrera, cohorte, estado, vigencia (desde/hasta). SHALL permitir crear, editar y toggle de estado de dictados. SHALL seguir el patrón `dashboard-crud-page`.

#### Scenario: Listar dictados
- **WHEN** el ADMIN accede a DictadosPage
- **THEN** se muestra tabla paginada con todos los dictados del tenant

#### Scenario: Crear dictado
- **WHEN** el ADMIN completa el formulario de dictado (materia, carrera, cohorte, vigencia opcional) y confirma
- **THEN** el dictado se crea y la tabla se actualiza via TanStack Query invalidation

### Requirement: Selector de roles desde API en UsuarioFormModal
`UsuarioFormModal` SHALL reemplazar el campo texto `rol` por un `select` que carga los roles disponibles desde `GET /api/admin/roles`. Al crear/editar usuario, se envía `rol_id` en lugar del nombre del rol.

#### Scenario: Selector de roles con datos reales
- **WHEN** el ADMIN abre el modal de crear usuario
- **THEN** el campo rol es un dropdown con roles obtenidos de la API

### Requirement: Manejo de errores consistente en páginas ADMIN
Todas las páginas ADMIN SHALL mostrar errores de API usando el componente `EmptyState` o `ErrorBoundary` del design system. Las mutaciones fallidas SHALL mostrar el mensaje de error del backend en el modal/formulario.

#### Scenario: Error en creación de carrera
- **WHEN** el ADMIN intenta crear una carrera con código duplicado
- **THEN** el modal muestra el mensaje de error "Código de carrera ya existe"
