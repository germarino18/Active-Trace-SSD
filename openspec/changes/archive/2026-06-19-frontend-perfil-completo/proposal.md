## Why

`ProfilePage.tsx` solo expone `nombre`, `apellido` y email en modo lectura, dejando fuera todos los campos de F11.1: identificación fiscal, datos bancarios, regional, modalidad de cobro y matrícula profesional. Además, la página no consume la API real (`PATCH /api/v1/perfil`, ya implementado en C-20): el submit es un no-op. Esta brecha impide que docentes y coordinadores completen su perfil para la liquidación de honorarios.

## What Changes

- Ampliar el formulario de `ProfilePage.tsx` con los campos faltantes de F11.1:
  - **CUIL** — solo lectura, siempre visible.
  - **DNI** — editable.
  - **Sexo** — campo desplegable editable.
  - **Banco**, **CBU**, **Alias CBU** — datos bancarios editables.
  - **Regional** — campo de texto editable.
  - **Modalidad de cobro** — selector Factura / Liquidación (mapea a `facturador: boolean`).
  - **Matrícula / Registro profesional** (`legajo_profesional`) — campo de texto editable.
- Conectar el formulario a la API real:
  - `GET /api/v1/perfil` vía hook TanStack Query para inicializar valores.
  - `PATCH /api/v1/perfil` vía mutation para persistir cambios.
- Extender el schema Zod con validaciones para los nuevos campos.
- Agregar sección "Datos bancarios" visualmente separada en el layout.
- Mostrar errores de API y feedback de éxito/error en el formulario.

## Capabilities

### New Capabilities

- `perfil-completo-frontend`: Página de perfil completa con todos los campos F11.1, integración real con la API `perfil` (GET + PATCH), validación Zod extendida y sección de datos bancarios.

### Modified Capabilities

- `perfil-propio`: La spec existente cubre el backend (GET + PATCH). Se agrega un requerimiento de contrato de respuesta que incluye los campos nuevos del modelo (`sexo`, `modalidad_cobro`) que el frontend necesita consumir — aunque ya están en el modelo de datos, la spec no los documentaba explícitamente como parte del response.

## Impact

- **Frontend**: `src/pages/ProfilePage.tsx` (refactor completo del formulario).
- **Frontend hooks**: nuevo `useProfile` en `features/perfil/` para encapsular GET + PATCH con TanStack Query.
- **Frontend types**: nuevos tipos `ProfileResponse`, `ProfilePatchRequest` en `features/perfil/types.ts`.
- **Sin cambios en backend**: el endpoint `PATCH /api/v1/perfil` ya acepta todos los campos de F11.1 (C-20).
- **Sin cambios de schema**: el modelo `Usuario` (E4) ya contempla todos los campos necesarios.
