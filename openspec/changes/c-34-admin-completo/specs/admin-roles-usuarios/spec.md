## ADDED Requirements

### Requirement: Endpoints de asignación de roles a usuarios
El sistema SHALL exponer bajo `/api/admin/usuarios/{id}/roles` los siguientes endpoints, todos gated por `usuarios:gestionar`:
- `GET` — lista roles asignados al usuario con su vigencia
- `POST` — asigna un rol al usuario (body: `{rol_id, desde?, hasta?}`)
- `DELETE /{rol_id}` — remueve la asignación de un rol del usuario

La asignación SHALL usar la tabla `usuario_rol` (o equivalente) con FK a `usuario` y `rol`. Un usuario PUEDE tener múltiples roles simultáneamente.

#### Scenario: Asignar rol a usuario
- **WHEN** un ADMIN invoca `POST /api/admin/usuarios/{id}/roles` con `rol_id` válido
- **THEN** el rol se asigna al usuario y aparece en la lista de roles del usuario

#### Scenario: Múltiples roles
- **WHEN** un ADMIN asigna dos roles diferentes al mismo usuario
- **THEN** ambos roles aparecen en la lista de roles del usuario

#### Scenario: Remover rol
- **WHEN** un ADMIN invoca `DELETE /api/admin/usuarios/{id}/roles/{rol_id}`
- **THEN** ese rol ya no aparece en la lista de roles del usuario

#### Scenario: Usuario sin roles
- **WHEN** un ADMIN consulta roles de un usuario sin asignaciones
- **THEN** el sistema devuelve lista vacía (no error)
