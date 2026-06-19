## ADDED Requirements

### Requirement: Dashboard principal con KPIs por rol
El `DashboardPage` SHALL mostrar contenido real según el rol del usuario autenticado (desde JWT). MUST incluir al menos: cards de KPI con contadores relevantes al rol, sección de actividad reciente o próximas acciones, y un bento grid responsivo siguiendo el UI kit del DS.

#### Scenario: Dashboard de alumno
- **WHEN** el usuario autenticado tiene rol ALUMNO
- **THEN** el dashboard muestra: materias activas (conteo), promedio general, próximas fechas

#### Scenario: Dashboard de profesor/tutor
- **WHEN** el usuario tiene rol PROFESOR o TUTOR
- **THEN** el dashboard muestra: materias asignadas, alumnos en riesgo (conteo), entregas pendientes

#### Scenario: Dashboard de coordinador/admin
- **WHEN** el usuario tiene rol COORDINADOR o ADMIN
- **THEN** el dashboard muestra: métricas generales del tenant, actividad reciente, accesos rápidos

#### Scenario: Estado de carga
- **WHEN** los datos del dashboard están cargando
- **THEN** las cards muestran skeleton loaders, no texto placeholder ni spinners sueltos

---

### Requirement: Página de perfil
`ProfilePage` SHALL permitir al usuario ver y editar sus datos personales (nombre, apellido, email). MUST incluir sección separada para cambio de contraseña. Los cambios SHALL guardarse solo al confirmar explícitamente.

#### Scenario: Editar nombre
- **WHEN** el usuario modifica su nombre y confirma
- **THEN** los datos se persisten y se muestra feedback de éxito

#### Scenario: Cambio de contraseña con contraseña actual incorrecta
- **WHEN** el usuario ingresa su contraseña actual de forma incorrecta
- **THEN** el backend devuelve error y se muestra inline, sin cerrar sesión

---

### Requirement: Páginas de error 403 y 404
`ForbiddenPage` y `NotFoundPage` SHALL usar el UI kit Obsidian de errores. MUST incluir código de error prominente, descripción en español, y botón de navegación de retorno (volver al dashboard o al inicio).

#### Scenario: Acceso a ruta protegida sin permiso
- **WHEN** el usuario accede a una ruta sin los permisos necesarios
- **THEN** se muestra la página 403 con opción de volver al dashboard

#### Scenario: Ruta inexistente
- **WHEN** el usuario navega a una URL que no existe en el router
- **THEN** se muestra la página 404 con opción de volver al inicio
