## ADDED Requirements

### Requirement: Listado de usuarios del tenant
El sistema SHALL mostrar al ADMIN un listado paginado de todos los usuarios del tenant, con filtros por: rol, estado (activo/inactivo), búsqueda por nombre o email.

#### Scenario: Listar usuarios con filtro por rol
- **WHEN** el ADMIN accede a la sección "Usuarios"
- **THEN** el sistema muestra la tabla paginada de usuarios
- **WHEN** el ADMIN selecciona un rol en el filtro
- **THEN** el sistema filtra la tabla por ese rol

#### Scenario: Buscar usuario por nombre
- **WHEN** el ADMIN ingresa texto en el campo de búsqueda
- **THEN** el sistema filtra los usuarios cuyo nombre o email contengan el texto

### Requirement: Creación de usuarios
El sistema SHALL permitir al ADMIN crear nuevos usuarios del tenant con los campos: nombre, apellido, email, rol, y estado inicial.

#### Scenario: Crear usuario exitosamente
- **WHEN** el ADMIN completa el formulario de nuevo usuario con todos los campos requeridos
- **THEN** el sistema crea el usuario y lo muestra en el listado

#### Scenario: Error por email duplicado
- **WHEN** el ADMIN intenta crear un usuario con un email ya existente
- **THEN** el sistema muestra un error indicando que el email ya está registrado

### Requirement: Edición de usuarios
El sistema SHALL permitir al ADMIN editar los datos de un usuario existente, incluyendo cambio de rol y estado.

#### Scenario: Editar rol de usuario
- **WHEN** el ADMIN edita un usuario y cambia su rol
- **THEN** el sistema actualiza el rol y los permisos del usuario se recalcular en el próximo acceso
