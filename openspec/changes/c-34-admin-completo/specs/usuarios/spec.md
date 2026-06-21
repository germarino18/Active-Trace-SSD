## ADDED Requirements

### Requirement: Asignación de roles a usuarios vía endpoint dedicado
El sistema SHALL exponer endpoints para asignar y remover roles de un usuario del tenant. La asignación SHALL tener vigencia opcional (`desde`, `hasta`). El permiso requerido SHALL ser `usuarios:gestionar` (mismo guard que el ABM de usuarios).

#### Scenario: Asignar rol a usuario
- **WHEN** un ADMIN invoca `POST /api/admin/usuarios/{id}/roles` con `rol_id` y `desde` opcional
- **THEN** el rol se asigna al usuario y se puede consultar en `GET /api/admin/usuarios/{id}/roles`

#### Scenario: Remover rol de usuario
- **WHEN** un ADMIN invoca `DELETE /api/admin/usuarios/{id}/roles/{rol_id}`
- **THEN** el rol se desasigna del usuario

#### Scenario: Listar roles de usuario
- **WHEN** un ADMIN invoca `GET /api/admin/usuarios/{id}/roles`
- **THEN** se devuelven todos los roles asignados al usuario con su vigencia

### Requirement: Catálogo de roles desde API en el frontend de usuarios
El formulario de creación/edición de usuario en el frontend SHALL obtener el catálogo de roles desde `GET /api/admin/roles` en lugar de usar un campo de texto libre. El selector SHALL mostrar `rol.nombre` y enviar `rol.id`.

#### Scenario: Formulario carga roles desde API
- **WHEN** el ADMIN abre el modal de crear/editar usuario
- **THEN** el selector de roles muestra los roles obtenidos de `/api/admin/roles`
