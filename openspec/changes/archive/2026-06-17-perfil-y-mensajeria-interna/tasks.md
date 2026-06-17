## 1. Setup — Permisos

- [x] 1.1 Add `INBOX_ACCEDER = "inbox:acceder"` to `backend/app/core/permissions.py`
- [x] 1.2 Registrar `inbox:acceder` en la matriz de roles (seed/default permissions) para todos los roles autenticados

## 2. Perfil Propio — Service + Router

- [x] 2.1 Crear schemas Pydantic: `PerfilResponse` (con campos + email desde users) y `PerfilUpdate` (solo campos editables, rechaza cuil con `extra='forbid'`)
- [x] 2.2 Crear `PerfilService` en `backend/app/services/perfil_service.py` con métodos `get_perfil(user_id, tenant_id)` y `update_perfil(user_id, tenant_id, data)`, incluyendo JOIN con `users` para email
- [x] 2.3 Crear router `backend/app/api/v1/routers/perfil.py` con GET `/api/v1/perfil` y PATCH `/api/v1/perfil` (sin permiso extra, solo autenticación)

## 3. Mensajería Interna — Modelos

- [x] 3.1 Crear modelo `HiloConversacion` en `backend/app/models/hilo_conversacion.py` (BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin)
- [x] 3.2 Crear modelo `HiloParticipante` en `backend/app/models/hilo_participante.py` (PK compuesta hilo_id + usuario_id, ultima_visto)
- [x] 3.3 Crear modelo `Mensaje` en `backend/app/models/mensaje.py` (BaseMixin, TenantMixin, SoftDeleteMixin, AuditMixin)
- [x] 3.4 Asegurar que los nuevos modelos se importen en `backend/app/models/__init__.py`

## 4. Mensajería Interna — Migración Alembic

- [x] 4.1 Generar migración Alembic con tablas `hilo_conversacion`, `hilo_participante`, `mensaje` + índices

## 5. Mensajería Interna — Repositorios

- [x] 5.1 Crear `HiloRepository` en `backend/app/repositories/hilo_repository.py` con métodos: `list_by_participante(usuario_id, tenant_id)`, `get_by_id(hilo_id, tenant_id)`, `add_participante(hilo_id, usuario_id)`
- [x] 5.2 Crear `MensajeRepository` en `backend/app/repositories/mensaje_repository.py` con métodos: `list_by_hilo(hilo_id, tenant_id)`, `create(data)`, `get_ultimo_mensaje(hilo_id)`

## 6. Mensajería Interna — Schemas

- [x] 6.1 Crear `backend/app/schemas/mensajeria.py` con: `HiloResponse`, `MensajeResponse`, `ResponderRequest` (contenido: str, max 2000 chars), `HiloListResponse`

## 7. Mensajería Interna — Service

- [x] 7.1 Crear `MensajeriaService` en `backend/app/services/mensajeria_service.py` con métodos:
  - `list_hilos(usuario_id, tenant_id)` → hilos con último mensaje, no_leido
  - `get_hilo(hilo_id, usuario_id, tenant_id)` → mensajes del hilo, validar pertenencia (404 si no)
  - `responder(hilo_id, usuario_id, tenant_id, contenido)` → crear mensaje, actualizar ultima_visto del remitente, marcar no_leido al otro participante

## 8. Mensajería Interna — Router

- [x] 8.1 Crear router `backend/app/api/v1/routers/inbox.py` con gated `require_permission(Perm.INBOX_ACCEDER)`:
  - GET `/api/v1/inbox/hilos`
  - GET `/api/v1/inbox/hilos/{id}`
  - POST `/api/v1/inbox/hilos/{id}/responder`

## 9. Wire Up

- [x] 9.1 Importar e incluir routers `perfil_router` e `inbox_router` en `backend/app/main.py`

## 10. Tests — Perfil Propio

- [x] 10.1 Crear `tests/test_perfil/conftest.py` con fixtures auth + usuario data
- [x] 10.2 Crear `tests/test_perfil/test_schemas.py`: tests de validación PerfilUpdate (campos editables, cuil rechazado, body vacío)
- [x] 10.3 Crear `tests/test_perfil/test_service.py`: tests de get/update perfil, tenant isolation, usuario sin profile retorna 404
- [x] 10.4 Crear `tests/test_perfil/test_router.py`: tests de integración GET (200, 404) y PATCH (200, 422 cuil, 422 vacío)

## 11. Tests — Mensajería Interna

- [x] 11.1 Crear `tests/test_mensajeria/conftest.py` con fixtures: usuarios, hilos, mensajes
- [x] 11.2 Crear `tests/test_mensajeria/test_schemas.py`: tests de validación ResponderRequest (contenido vacío, max length)
- [x] 11.3 Crear `tests/test_mensajeria/test_service.py`: tests list_hilos, get_hilo (pertenencia OK/404), responder, no_leido flag
- [x] 11.4 Crear `tests/test_mensajeria/test_router.py`: tests integración GET hilos, GET hilo/{id}, POST responder, 404 no participante, 401 sin auth
