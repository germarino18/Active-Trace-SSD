## Why

El rol **TUTOR** es un actor central del sistema (ver `03_actores_y_roles.md`) pero actualmente no puede operar el frontend porque el sidebar filtra items usando permisos wildcard (`atrasados:*`, `encuentros:*`) que no matchean con los permisos específicos del TUTOR (`atrasados:ver`, `encuentros:gestionar`). Además faltan items clave ("Guardias", "Entregas sin corregir") y la vista "Mis alumnos". El backend ya está implementado para todas estas capacidades — solo falta la capa frontend.

## What Changes

- **Sidebar**: reemplazar permisos wildcard (`*`) por permisos específicos que el TUTOR sí tiene
- **Nuevos items de menú**: "Guardias" y "Entregas sin corregir" visibles para TUTOR
- **Vista "Mis Alumnos"**: nueva página `/tutor/alumnos` con listado de alumnos asignados al tutor por materia
- **Vista de atrasados**: habilitar `VistaAtrasadosPage` (ya existe) para TUTOR con scope propio
- **Vista de entregas sin corregir**: habilitar `EntregasSinCorregirPage` (ya existe) para TUTOR con scope propio
- **Registro de guardias**: formulario desde frontend conectado al endpoint existente
- **Confirmación de avisos**: botón de ack inline para TUTOR usando `POST /api/v1/avisos/:id/ack`
- **Cambios 100% frontend**: no se toca backend

## Capabilities

### New Capabilities
- `tutor-sidebar`: Items de navegación visibles para TUTOR con permisos correctos y nuevos atajos
- `tutor-mis-alumnos`: Vista de alumnos asignados al tutor logueado, con datos de contacto y materias
- `tutor-guardias`: Registro de guardias del tutor desde el frontend
- `tutor-avisos`: Confirmación de avisos (acknowledgment) por parte del TUTOR

### Modified Capabilities
- *(ninguna — no hay specs existentes que modificar)*

## Impact

- **Frontend**: Sidebar (`AppLayout.tsx`, `Sidebar.tsx`), routing (`App.tsx`), nuevas páginas en `features/tutor/`, posible ajuste menor en `features/academico/pages/` para scope TUTOR
- **API**: solo se consumen endpoints existentes — sin cambios en backend
- **Auth/RBAC**: no se cambia la matriz de permisos — solo se corrige el matching en frontend
