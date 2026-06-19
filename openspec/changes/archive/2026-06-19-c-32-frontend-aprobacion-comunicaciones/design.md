## Context

El backend de comunicaciones (C-12) ya expone endpoints para listar lotes pendientes, aprobar y cancelar lotes (`/api/v1/comunicaciones/lotes/*`). El componente `PreviewComunicacionModal` existe en `features/academico/components/` y tiene la interfaz correcta para mostrar asunto, cuerpo y lista de destinatarios.

El feature `coordinacion` ya tiene la estructura canónica: `pages/`, `hooks/`, `services/`, `types/`. El AppLayout y sidebar están en `features/layout/` y el router en `App.tsx`.

## Goals / Non-Goals

**Goals:**
- Página `AprobacionComunicacionesPage` en `features/coordinacion/pages/` consumiendo los endpoints de aprobación de C-12.
- Hook `useAprobacionComunicaciones` con TanStack Query para fetch de lotes y mutaciones de aprobar/cancelar.
- Entrada en sidebar para COORDINADOR/ADMIN con badge de cantidad de lotes pendientes.
- Route guard `comunicacion:aprobar` en la nueva ruta.
- Reutilización de `PreviewComunicacionModal` sin modificarlo.

**Non-Goals:**
- Cambios al backend o schema de BD.
- Aprobación individual por destinatario dentro de un lote (el scope del sidebar cubre lotes completos; aprobación individual queda para iteración futura).
- Modificar el flujo de envío desde `ComunicacionAtrasadosPage`.

## Decisions

**D1 — Ubicar el nuevo feature en `features/coordinacion/`**  
La aprobación es una responsabilidad del rol COORDINADOR/ADMIN, no del flujo del PROFESOR. Colocarlo en `coordinacion/` mantiene la separación de responsabilidades por rol y es consistente con el resto de páginas del panel de coordinación.

Alternativa descartada: colocarlo en `features/academico/` junto a `ComunicacionAtrasadosPage` —- mezclaría responsabilidades de roles distintos en un mismo feature.

**D2 — Reutilizar `PreviewComunicacionModal` sin moverlo**  
El componente ya existe en `academico/components/` y tiene la interfaz correcta. Se importa directamente desde esa ruta. Moverlo a `shared/` queda fuera del scope de este change.

**D3 — Badge de pendientes via query separada**  
El badge del sidebar usa `useQuery(['comunicaciones-lotes-pendientes-count'])` con un GET ligero al mismo endpoint que la página (`?estado=pendiente`). Esto evita estado global (Context/Zustand) y permite que el badge se actualice automáticamente por invalidación de caché tras cada aprobación/cancelación. La misma query key se comparte entre el hook del sidebar y el hook de la página, así la invalidación tras mutación actualiza ambos.

**D4 — Confirmación antes de aprobar y rechazar**  
Reutilizar `ConfirmDialog` que ya existe en `features/coordinacion/components/`. Aprobar es acción de alto impacto (inicia envío real de emails); rechazar es irreversible para el lote. Ambos requieren confirmación explícita.

**D5 — Route guard vía `ProtectedRoute` existente**  
El router ya implementa `ProtectedRoute` con `requiredPermission`. Se añade la ruta `/comunicaciones/aprobar` con `requiredPermission="comunicacion:aprobar"` siguiendo el patrón del resto de rutas de coordinación.

## Risks / Trade-offs

- **[Riesgo] Endpoint `GET /lotes?estado=pendiente` podría no existir aún en C-12** → Verificar con el equipo de backend antes de implementar el hook. Si el endpoint tiene otro nombre o path, ajustar en el servicio sin cambiar el contrato del hook.
- **[Riesgo] `PreviewComunicacionModal` acoplado a tipos de `academico/types`** → El modal recibe `destinatarios: ComunicacionDestinatario[]`. Si el tipo de destinatario del lote de aprobación difiere, se necesitará un mapeo en la página antes de pasarlo al modal.
- **[Trade-off] Badge query hace un fetch extra** → Se acepta el costo de un fetch adicional para el count a cambio de no introducir estado global. La query se configura con `staleTime: 30_000` para no saturar el backend.

## Open Questions

- OQ-1: ¿El endpoint de aprobación devuelve el lote actualizado o solo 200 OK? Determina si la invalidación de caché es suficiente o si hay que actualizar manualmente el estado local.
- OQ-2: ¿El badge del sidebar debe mostrar el count en tiempo real (polling) o solo al navegar? Para esta iteración se asume sin polling (refresh al invalidar caché por acción del usuario).
