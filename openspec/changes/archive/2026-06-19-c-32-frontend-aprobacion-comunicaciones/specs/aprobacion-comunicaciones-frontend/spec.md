## ADDED Requirements

### Requirement: Listar lotes de comunicaciones pendientes de aprobación
La página `AprobacionComunicacionesPage` SHALL mostrar todos los lotes (`lote_id`) de comunicaciones en estado **Pendiente** del tenant, consumiendo `GET /api/v1/comunicaciones/lotes?estado=pendiente`. Solo usuarios con permiso `comunicacion:aprobar` SHALL acceder a esta ruta.

#### Scenario: Lista con lotes pendientes
- **WHEN** un usuario con `comunicacion:aprobar` accede a `/comunicaciones/aprobar`
- **THEN** la página muestra una tabla con los lotes pendientes: lote_id, docente remitente, fecha de creación, cantidad de destinatarios y asunto

#### Scenario: Sin lotes pendientes
- **WHEN** no existen lotes en estado Pendiente
- **THEN** la página muestra un estado vacío con mensaje "No hay comunicaciones pendientes de aprobación"

#### Scenario: Usuario sin permiso es redirigido
- **WHEN** un usuario sin `comunicacion:aprobar` intenta acceder a `/comunicaciones/aprobar`
- **THEN** el route guard lo redirige con un 403 o a la página de acceso denegado

---

### Requirement: Ver preview de un lote antes de aprobar
El aprobador SHALL poder abrir una vista previa del contenido del lote (asunto + cuerpo + lista de destinatarios) antes de decidir, reutilizando el componente `PreviewComunicacionModal`.

#### Scenario: Abrir preview de lote
- **WHEN** el aprobador hace clic en "Ver preview" de un lote
- **THEN** se abre `PreviewComunicacionModal` con el asunto, cuerpo y lista de destinatarios del lote

#### Scenario: Cerrar preview sin acción
- **WHEN** el aprobador cierra el modal sin confirmar
- **THEN** el modal se cierra y no se realiza ninguna acción sobre el lote

---

### Requirement: Aprobar lote completo
El aprobador SHALL poder aprobar todos los mensajes de un lote en un solo click, enviando `POST /api/v1/comunicaciones/lotes/{lote_id}/aprobar`.

#### Scenario: Aprobación exitosa de lote
- **WHEN** el aprobador hace clic en "Aprobar" en un lote y confirma
- **THEN** el sistema llama al endpoint de aprobación, el lote desaparece de la lista de pendientes y se muestra un toast de éxito

#### Scenario: Error al aprobar
- **WHEN** el endpoint de aprobación retorna un error
- **THEN** el sistema muestra un mensaje de error y el lote permanece en la lista

---

### Requirement: Rechazar lote completo
El aprobador SHALL poder rechazar (cancelar) todos los mensajes de un lote, enviando `POST /api/v1/comunicaciones/lotes/{lote_id}/cancelar`.

#### Scenario: Rechazo exitoso de lote
- **WHEN** el aprobador hace clic en "Rechazar" en un lote y confirma en el diálogo
- **THEN** el sistema llama al endpoint de cancelación, el lote desaparece de la lista y se muestra un toast de confirmación

#### Scenario: Cancelar la acción de rechazo
- **WHEN** el aprobador hace clic en "Rechazar" pero cancela en el diálogo de confirmación
- **THEN** no se realiza ninguna acción y el lote permanece en la lista

---

### Requirement: Refrescar lista automáticamente tras acción
Después de aprobar o rechazar un lote, la lista SHALL refrescarse automáticamente via invalidación de caché de TanStack Query.

#### Scenario: Refresh tras aprobar
- **WHEN** la mutación de aprobación completa con éxito
- **THEN** TanStack Query invalida la query de lotes pendientes y la lista se recarga sin navegación manual

#### Scenario: Refresh tras rechazar
- **WHEN** la mutación de cancelación completa con éxito
- **THEN** TanStack Query invalida la query de lotes pendientes y la lista se recarga sin navegación manual
