## ADDED Requirements

### Requirement: Secciones docentes incluyen ítem "Mensajes" con badge de no-leídos

Las secciones del sidebar correspondientes a TUTOR, PROFESOR, COORDINADOR y ADMIN SHALL incluir un ítem "Mensajes" que navega a `/inbox`, protegido con el permiso `inbox:acceder`. El ítem SHALL mostrar un badge numérico con el conteo de hilos `no_leido: true` cuando `unreadCount > 0`, obtenido de `useInbox().unreadCount`.

#### Scenario: Usuario con mensajes sin leer ve badge en sidebar
- **WHEN** el usuario tiene `inbox:acceder` y `useInbox().unreadCount > 0`
- **THEN** el ítem "Mensajes" en el sidebar muestra un badge con el número de hilos sin leer

#### Scenario: Usuario sin mensajes sin leer no ve badge
- **WHEN** el usuario tiene `inbox:acceder` y `useInbox().unreadCount === 0`
- **THEN** el ítem "Mensajes" en el sidebar no muestra badge

#### Scenario: Usuario sin permiso inbox:acceder no ve el ítem
- **WHEN** el usuario no tiene `inbox:acceder`
- **THEN** el ítem "Mensajes" no aparece en ninguna sección del sidebar
