## 1. Servicio y tipos

- [x] 1.1 Crear `features/coordinacion/services/aprobacion-comunicaciones.service.ts` con funciones `getLotesPendientes()`, `aprobarLote(loteId)` y `cancelarLote(loteId)` apuntando a `/api/v1/comunicaciones/lotes`
- [x] 1.2 Agregar los tipos necesarios en `features/coordinacion/types/index.ts`: `LoteComunicacion`, `LoteComunicacionResumen`

## 2. Hook TanStack Query

- [x] 2.1 Crear `features/coordinacion/hooks/useAprobacionComunicaciones.ts` con `useQuery(['comunicaciones-lotes-pendientes'])` para listar lotes y `useMutation` para aprobar y cancelar, con invalidación de caché `['comunicaciones-lotes-pendientes']` al completar cada mutación
- [x] 2.2 Agregar `useQuery(['comunicaciones-lotes-pendientes-count'])` (o reutilizar la misma query key) para el badge del sidebar con `staleTime: 30_000`

## 3. Página principal

- [x] 3.1 Crear `features/coordinacion/pages/AprobacionComunicacionesPage.tsx` con tabla de lotes pendientes: columnas lote_id, remitente, fecha, destinatarios, asunto
- [x] 3.2 Implementar estado vacío cuando no hay lotes pendientes
- [x] 3.3 Conectar botón "Ver preview" que abre `PreviewComunicacionModal` (importado de `features/academico/components/`) con el asunto, cuerpo y destinatarios del lote
- [x] 3.4 Conectar botón "Aprobar" con `ConfirmDialog` y mutación `aprobarLote`
- [x] 3.5 Conectar botón "Rechazar" con `ConfirmDialog` y mutación `cancelarLote`
- [x] 3.6 Mostrar toast de éxito/error tras cada acción (reutilizar el mecanismo de toast existente en el proyecto)

## 4. Router y route guard

- [x] 4.1 Agregar ruta `/comunicaciones/aprobar` en `App.tsx` envuelta en `ProtectedRoute` con `requiredPermission="comunicacion:aprobar"`, renderizando `AprobacionComunicacionesPage`

## 5. Sidebar

- [x] 5.1 Agregar entrada "Aprobar Comunicaciones" en el sidebar (`AppLayout` o el componente de nav de coordinación) para los roles COORDINADOR y ADMIN, con ícono `approval` (material symbols) y ruta `/comunicaciones/aprobar`
- [x] 5.2 Conectar badge numérico en la entrada del sidebar con el count de lotes pendientes via `useAprobacionComunicaciones` (o hook equivalente)

## 6. Tests

- [x] 6.1 Escribir tests para `AprobacionComunicacionesPage`: lista con lotes, estado vacío, apertura de preview, flujo de aprobación con confirmación, flujo de rechazo con confirmación
- [x] 6.2 Escribir tests para el hook `useAprobacionComunicaciones`: fetch de lotes, mutación de aprobación invalida caché, mutación de cancelación invalida caché
