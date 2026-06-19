## Context

`ProfilePage.tsx` es una pantalla esqueleto: muestra `nombre` y `apellido` con edición inline pero no conecta a ninguna API. El formulario de edición hace `setEditing(false)` sin llamar al backend. El endpoint `PATCH /api/v1/perfil` (C-20) ya existe y acepta todos los campos de F11.1. El modelo `Usuario` (E4) tiene: `nombre`, `apellidos`, `email`, `dni`, `cuil`, `cbu`, `alias_cbu`, `banco`, `regional`, `legajo`, `legajo_profesional`, `facturador`.

**Nota**: F11.1 menciona `sexo` como editable, pero E4 no define ese campo en el modelo de datos. Se omite en esta implementación — debe resolverse como pregunta abierta de dominio antes de agregarlo.

## Goals / Non-Goals

**Goals:**
- Mostrar y permitir editar todos los campos de F11.1 que existen en E4.
- CUIL visible como solo lectura (no incluido en el body del PATCH).
- Conectar el formulario a `GET /api/v1/perfil` (inicialización) y `PATCH /api/v1/perfil` (guardado).
- Validación Zod extendida para los nuevos campos.
- Sección bancaria visualmente separada del resto del perfil.

**Non-Goals:**
- Cambios en el backend o el modelo de datos.
- Campo `sexo` (no existe en E4).
- Subida de avatar.
- Cambio de contraseña mediante la misma API de perfil (sigue siendo un formulario independiente).

## Decisions

### 1. Módulo feature dedicado `features/perfil/`

Se extrae la lógica de la página a un módulo propio:
- `features/perfil/hooks/useProfile.ts` — encapsula GET + PATCH con TanStack Query.
- `features/perfil/types.ts` — `ProfileResponse` y `ProfilePatchRequest`.
- `ProfilePage.tsx` pasa a ser un componente de presentación que consume el hook.

**Alternativa descartada**: mantener todo en `pages/ProfilePage.tsx`. Supera las 200 LOC permitidas y mezcla fetch, tipos y UI.

### 2. Separación visual en tres cards

Layout de la página:
1. **Card lateral** — avatar, nombre completo, roles, tenant (sin cambio de diseño).
2. **Card "Información personal"** — `nombre`, `apellidos`, `dni` (editable), `cuil` (solo lectura), `regional`, `legajo_profesional`.
3. **Card "Datos bancarios"** — `banco`, `cbu`, `alias_cbu`, `modalidad_cobro` (selector "Factura" | "Liquidación" que mapea a `facturador: boolean`).
4. **Card "Cambiar contraseña"** — sin cambios.

**Alternativa descartada**: un único formulario unificado. La longitud visual sería excesiva y mezcla datos de identidad con datos bancarios sensibles.

### 3. Modo edición por sección (no global)

Cada card de contenido tiene su propio estado `editing` y su propio formulario. Esto permite guardar datos personales sin tocar los bancarios y viceversa, reduciendo el riesgo de sobreescritura accidental.

**Alternativa descartada**: edición global (un solo botón "Editar" para toda la página). Fuerza al usuario a confirmar campos bancarios aunque no los haya cambiado.

### 4. Inicialización del formulario con `reset()` tras fetch

`useForm` con `defaultValues: {}` + `reset(data)` en el `onSuccess` del query. Evita que el formulario arranque vacío mientras carga y permite reinicialización si el usuario recarga datos.

### 5. `facturador` expuesto como `modalidad_cobro` en la UI

El campo booleano `facturador` en la API se mapea a un `<select>` con opciones "Factura" (true) y "Liquidación" (false) en el formulario. La conversión ocurre en el hook al construir el body del PATCH.

## Risks / Trade-offs

- **Campos cifrados (CBU, alias, DNI)**: el backend devuelve estos campos descifrados al owner (spec `perfil-propio`). El frontend los recibe en texto plano y los envía de vuelta. Riesgo: si el endpoint alguna vez cambia el contrato de cifrado, la UI no cambia. Mitigación: la spec backend ya lo garantiza explícitamente.
- **Edición por sección con múltiples forms**: si el usuario edita datos personales y bancarios a la vez sin guardar, y navega fuera, pierde ambos cambios sin aviso. Mitigación: guardar por sección reduce la ventana de pérdida; se puede agregar `beforeunload` en una iteración posterior.
- **Campo `sexo` omitido**: F11.1 lo menciona como editable pero E4 no lo tiene. Si el backend lo agrega en el futuro, la UI necesitará actualización. Se documenta como pregunta abierta.
