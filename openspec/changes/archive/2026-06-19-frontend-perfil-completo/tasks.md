## 1. Tipos y contrato de API

- [x] 1.1 Crear `frontend/src/features/perfil/types.ts` con `ProfileResponse` (todos los campos de E4 incluyendo `cuil`, `email`, `facturador`) y `ProfilePatchRequest` (solo campos editables, sin `cuil` ni `email`)
- [x] 1.2 Definir el schema Zod extendido en `frontend/src/features/perfil/profileSchema.ts`: validar `dni` (7-8 dígitos), `cbu` (22 dígitos), `alias_cbu` (regex), `banco`/`regional`/`legajo_profesional` (max chars), `nombre`/`apellidos` (non-empty), `facturador` (boolean)

## 2. Hook TanStack Query

- [x] 2.1 Crear `frontend/src/features/perfil/hooks/useProfile.ts` con `useProfileQuery` (GET `/api/v1/perfil`) que retorna los datos del perfil y estado de loading/error
- [x] 2.2 Agregar `useProfileMutation` en el mismo hook: mutation PATCH `/api/v1/perfil` con invalidación del query al completar con éxito

## 3. Refactor ProfilePage — sección Información Personal

- [x] 3.1 Reemplazar el estado local `editing` y el form actual por un `useForm<PersonalForm>` inicializado con `reset()` desde la respuesta del query (campos: `nombre`, `apellidos`, `dni`, `regional`, `legajo_profesional`)
- [x] 3.2 Agregar campos `dni` (editable), `cuil` (siempre `readOnly`), `regional` y `legajo_profesional` al card "Información personal"
- [x] 3.3 Conectar el submit del card "Información personal" a `useProfileMutation` y manejar éxito (salir de edición, banner verde) y error API (mostrar mensaje inline)

## 4. Refactor ProfilePage — sección Datos Bancarios

- [x] 4.1 Agregar nuevo card "Datos bancarios" con su propio `useForm<BankingForm>` independiente (campos: `banco`, `cbu`, `alias_cbu`, `facturador`) con estado de edición propio
- [x] 4.2 Implementar el selector `modalidad_cobro` con opciones "Factura" / "Liquidación" que mapea a `facturador: boolean` al construir el body del PATCH
- [x] 4.3 Conectar el submit del card "Datos bancarios" a `useProfileMutation` y manejar éxito/error de igual forma que el card personal

## 5. Estados de carga y error de la página

- [x] 5.1 Mostrar skeleton o spinner mientras el query inicial está cargando; deshabilitar todos los inputs hasta que los datos estén disponibles
- [x] 5.2 Mostrar un estado de error de página (mensaje + botón "Reintentar") si `useProfileQuery` falla

## 6. Tests

- [x] 6.1 Test unitario de `profileSchema.ts`: validar que CBU de 21 dígitos falla, alias inválido falla, nombre vacío falla, y un payload válido pasa
- [x] 6.2 Test de `useProfile.ts` con MSW (o mock de axios): verificar que el hook llama `GET /api/v1/perfil` y expone los datos; verificar que la mutation llama `PATCH` con el body correcto y excluye `cuil`
- [x] 6.3 Test de renderizado de `ProfilePage`: verificar que CUIL se renderiza como `readOnly`; verificar que el formulario de datos bancarios es independiente del personal (editar uno no afecta el estado del otro)
