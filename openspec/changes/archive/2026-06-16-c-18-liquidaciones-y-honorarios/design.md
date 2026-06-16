## Context

Activia Trace necesita un módulo de liquidaciones para que FINANZAS pueda gestionar honorarios docentes. El sistema ya cuenta con: multi-tenancy row-level, RBAC fino, soft delete, cifrado AES-256, auditoría append-only, y repositorio genérico con scope de tenant. El modelo `Usuario` ya incluye `facturador` booleano. Los permisos `liquidaciones:cerrar` y `facturas:gestionar` ya están seedeados para el rol FINANZAS. La acción de auditoría `LIQUIDACION_CERRAR` ya está definida.

El dominio de liquidaciones introduce 6 nuevas entidades (E17–E23 del modelo de datos), lógica de cálculo con vigencia temporal, segmentación contable (factura vs no-factura vs NEXO), y cierre inmutable. Es un módulo CRITICO (governance) por manejar datos financieros.

## Goals / Non-Goals

**Goals:**
- Proveer ABM completo de grilla salarial: SalarioBase, SalarioPlus, ClavePlus, MateriaClavePlus — todos con vigencia temporal.
- Calcular liquidación por período: monto base vigente por rol + suma de plus aplicables = total, por docente.
- Segmentar la vista de liquidación en 3 bloques: general (PROFESOR/TUTOR/COORDINADOR no facturadores), NEXO (sumado al total), y factura (solo informativo, excluido del total).
- Cerrar liquidación de forma inmutable con auditoría.
- Gestionar facturas de docentes facturadores (ABM + cambio de estado Pendiente→Abonada).
- Seguir los patrones existentes del proyecto: Clean Architecture, repositorio genérico con tenant scope, guards RBAC, servicios con DI, audit logging, soft delete.

**Non-Goals:**
- No incluye frontend (será parte de C-24).
- No incluye integración con sistemas externos de pagos/contabilidad.
- No incluye generación de recibos ni PDFs de liquidación.
- No cubre devengamiento diario ni liquidación proporcional por períodos parciales (solo mensual completo).
- No incluye workflow de aprobación de liquidaciones (solo cierre unimolecular por FINANZAS).

## Decisions

### D1 — Modelar ClavePlus como entidad independiente (no hardcode)
**Decisión**: `ClavePlus` es un catálogo administrable con código, descripción y vigencia. `MateriaClavePlus` asigna una clave a una materia con vigencia.
**Rationale**: El dominio define que la clave `grupo` del `SalarioPlus` mapea a un conjunto de materias configurable por tenant (E18, E22, E23). Modelarlo como entidad permite que FINANZAS administre las categorías sin cambiar código.
**Alternativa considerada**: Plus con grupo como string libre sobre `Asignacion`. Descartado porque no permite consistencia ni consulta eficiente de "qué plus aplica a esta materia".

### D2 — Cálculo de liquidación en servicio transaccional, no en DB
**Decisión**: `LiquidacionService.calcular_periodo()` itera docentes con asignaciones vigentes en el período, busca SalarioBase y SalarioPlus aplicables, calcula total, y persiste cada Liquidacion en una sola transacción.
**Rationale**: El cálculo requiere lógica de negocio (qué base aplica según rol, qué plus aplican según materias del docente). Hacerlo en SQL sería frágil y dificil de testear. El servicio recibe repositorios por DI y genera una transacción atómica.
**Alternativa considerada**: Stored procedure o función SQL. Descartado por: (a) no sigue el patrón del proyecto (lógica en Services), (b) difícil de testear, (c) no aporta beneficio real sobre una transacción Python.

### D3 — Liquidacion como registro por docente×período
**Decisión**: Cada `Liquidacion` es un registro individual por `(usuario_id, periodo, cohorte_id)` con monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado.
**Rationale**: Coincide con E19 del modelo de datos. Permite consultas eficientes por período, filtros por segmento (NEXO/factura), y cierre individual o por lote.
**Alternativa considerada**: Liquidación como documento agregado con líneas de detalle. Descartado porque el dominio no requiere desglose transaccional — el detalle (base + plus) se puede obtener de los datos fuente.

### D4 — ClavePlus resuelta desde Materia×Dictado, no desde Asignacion
**Decisión**: Para calcular qué plus aplica a un docente, se parte de sus `Asignacion` vigentes en el período, se obtienen las `Materia` asociadas, se busca `MateriaClavePlus` vigente para cada materia, y se agrupa por `ClavePlus` para sumar los `SalarioPlus` correspondientes.
**Rationale**: Un docente puede tener múltiples materias de distintos grupos. La cadena Asignacion→Materia→MateriaClavePlus→ClavePlus→SalarioPlus captura correctamente la acumulación de plus.
**Nota**: Las asignaciones referencian `materia_id` directamente (no `dictado_id`) porque en C-07 no se re-ancló a dictado. Esto es correcto para este change.

### D5 — Cierre inmutable vía guardia de estado + restricción en service
**Decisión**: El cambio de estado Abierta→Cerrada solo se permite vía `LiquidacionService.cerrar()`. Una vez Cerrada, cualquier intento de modificación lanza `BusinessRuleViolation`. No se usa trigger de DB — se controla en la capa de servicio, siguiendo el patrón existente.
**Rationale**: Consistente con RN-22. El servicio rechaza updates/ deletes sobre liquidaciones cerradas antes de llegar al repositorio.

### D6 — Permisos nuevos
**Decisión**: Se usan `liquidaciones:cerrar` y `facturas:gestionar` (ya seedeados). Se agrega `liquidaciones:configurar-salarios` para ABM de grilla salarial (seed en migración 016). `liquidaciones:ver` para consulta de liquidaciones.
**Rationale**: Separación de concerns: FINANZAS puede ver sin cerrar, o cerrar sin configurar salarios.

## Risks / Trade-offs

- **[R01] Cálculo no asincrónico**: El cálculo de liquidación para un período completo podría ser lento con muchos docentes. → **Mitigación**: El cálculo es transaccional y se hace en el request. Si el performance es problema, se puede mover a worker en el futuro (no blocking ahora).
- **[R02] Datos financieros sensibles**: Liquidaciones y facturas contienen montos. → **Mitigación**: Los modelos no tienen PII (no aplica cifrado adicional). El acceso está restringido a FINANZAS vía RBAC. Audit logging obligatorio en cada operación.
- **[R03] Consistencia de vigencia temporal**: SalarioBase, SalarioPlus, ClavePlus y MateriaClavePlus tienen vigencias solapadas. → **Mitigación**: El service de cálculo usa la función `vigente_en(fecha)` que busca el registro con `desde <= fecha AND (hasta IS NULL OR hasta >= fecha)`. Si hay múltiples vigentes (inconsistencia), se toma el más reciente por `desde` y se loguea warning.
- **[R04] Governance CRITICO**: El módulo maneja dinero. → **Mitigación**: Seguir estrictamente las reglas de governance CRITICO: propuesta revisada, tests obligatorios, auditoría en toda escritura, cierre inmutable.
