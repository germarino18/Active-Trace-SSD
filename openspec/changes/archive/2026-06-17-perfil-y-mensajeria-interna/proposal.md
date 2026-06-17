## Why

Los usuarios del sistema (docentes, coordinadores, administradores) no tienen forma de mantener sus datos personales y bancarios actualizados, ni de comunicarse entre sí a través de la plataforma. Esto genera errores en liquidaciones (datos bancarios desactualizados) y obliga a usar canales externos (WhatsApp, email) para la comunicación interna entre roles del sistema.

## What Changes

- **Perfil propio (F11.1)**: endpoint GET `/api/v1/perfil` para que cualquier usuario autenticado vea sus datos; endpoint PATCH `/api/v1/perfil` para editar campos editables (nombre, datos fiscales, bancarios, regional, email, modalidad de cobro, identificación profesional). CUIL es solo lectura.
- **Bandeja de mensajes interna (F3.4, F11.2, FL-10)**: endpoints GET `/api/v1/inbox/hilos` (hilos recibidos con resumen), GET `/api/v1/inbox/hilos/{id}` (mensajes de un hilo), POST `/api/v1/inbox/hilos/{id}/responder` (responder dentro del hilo). Mensajería entre usuarios registrados del mismo tenant, paralela al sistema de comunicaciones salientes a alumnos.
- **Cierre de sesión explícito (F11.3)**: reuse del endpoint `/api/auth/logout` ya implementado en C-03. No se crea un nuevo endpoint; se documenta su uso desde el perfil.
- **Nuevo modelo `Mensaje` / `HiloConversacion`** para mensajería interna, con FK a `usuario` (remitente), tenant-scoped, soft delete.
- **Nuevo permiso `inbox:acceder`** para la bandeja de mensajes (asignado a todos los roles autenticados).

## Capabilities

### New Capabilities
- `perfil-propio`: Consulta y actualización del perfil del usuario autenticado. GET/PATCH sobre `/api/v1/perfil`. Edición de campos personales, fiscales y bancarios; CUIL read-only. Todos los roles autenticados pueden usarlo.
- `mensajeria-interna`: Bandeja de mensajes interna entre usuarios registrados del mismo tenant. Hilos de conversación, responder dentro del hilo. GET hilos, GET mensajes de un hilo, POST responder.

### Modified Capabilities
<!-- Ninguna — perfil-propio y mensajeria-interna son capabilities net-new -->

## Impact

- **Nuevos modelos**: `HiloConversacion` y `Mensaje` en `backend/app/models/` con migración Alembic.
- **Nuevos schemas**: Pydantic request/response para perfil y mensajería en `backend/app/schemas/`.
- **Nuevos servicios**: `PerfilService` y `MensajeriaService` en `backend/app/services/`.
- **Nuevos repositorios**: `MensajeRepository` / `HiloRepository` en `backend/app/repositories/`.
- **Nuevos routers**: `perfil.py` y `inbox.py` en `backend/app/api/v1/routers/`.
- **Nuevo permiso**: `inbox:acceder` añadido a `core/permissions.py`.
- **Nueva migración**: Alembic para tablas `hilo_conversacion` y `mensaje`.
- **Logout**: reuse del endpoint existente `/api/auth/logout` (C-03), sin cambios.
- **Dependencia**: Requiere C-07 (usuarios base + auth) completado.
