## ADDED Requirements

### Requirement: Sidebar muestra items correctos para TUTOR
El sidebar DEBE mostrar solo los items de navegación para los cuales el TUTOR tiene el permiso correspondiente. Los permisos wildcard (`*`) DEBEN ser reemplazados por permisos específicos.

| Item | Path | Permiso |
|---|---|---|
| Dashboard | `/dashboard` | *(público)* |
| Mis Alumnos | `/tutor/alumnos` | *(nuevo, ver D2)* |
| Atrasados | `/materias` | `atrasados:ver` |
| Entregas sin corregir | `/entregas-sin-corregir` | *(nuevo)* |
| Encuentros | `/encuentros` | `encuentros:gestionar` |
| Guardias | `/guardias` | *(nuevo)* |
| Comunicación | `/materias` | `comunicacion:ver` |
| Mi Perfil | `/profile` | *(público)* |

#### Scenario: TUTOR ve items correctos
- **WHEN** un usuario con rol TUTOR inicia sesión
- **THEN** el sidebar DEBE mostrar: Dashboard, Mis Alumnos, Atrasados, Entregas sin corregir, Encuentros, Guardias, Comunicación, Mi Perfil
- **AND** NO DEBE mostrar: Calificaciones, Equipos Docentes, Avisos, Tareas, Coloquios, Programas, Fechas Académicas, Monitores, Liquidaciones, Grilla Salarial, Facturas, Estructura Académica, Usuarios, Auditoría, Métricas

#### Scenario: COORDINADOR sigue viendo items completos
- **WHEN** un usuario con rol COORDINADOR inicia sesión
- **THEN** el sidebar DEBE seguir mostrando todos los items que tenía antes del cambio
- **AND** `atrasados:ver` DEBE matchear porque COORDINADOR tiene ese permiso asignado

#### Scenario: ADMIN sigue viendo items completos
- **WHEN** un usuario con rol ADMIN inicia sesión
- **THEN** el sidebar DEBE seguir mostrando todos los items que tenía antes del cambio

### Requirement: Sidebar tiene nuevo item "Mis Alumnos"
El sidebar DEBE incluir un item "Mis Alumnos" con icono `group` que navegue a `/tutor/alumnos`.

#### Scenario: TUTOR ve item Mis Alumnos
- **WHEN** el TUTOR abre el sidebar
- **THEN** DEBE ver el item "Mis Alumnos" con icono `group` que apunta a `/tutor/alumnos`

### Requirement: Sidebar tiene nuevo item "Entregas sin corregir"
El sidebar DEBE incluir un item "Entregas sin corregir" con icono `assignment_late` que navegue a `/entregas-sin-corregir`.

#### Scenario: TUTOR ve item Entregas sin corregir
- **WHEN** el TUTOR abre el sidebar
- **THEN** DEBE ver el item "Entregas sin corregir" con icono `assignment_late` que apunta a `/entregas-sin-corregir`

### Requirement: Sidebar tiene nuevo item "Guardias"
El sidebar DEBE incluir un item "Guardias" con icono `shield` que navegue a `/guardias`.

#### Scenario: TUTOR ve item Guardias
- **WHEN** el TUTOR abre el sidebar
- **THEN** DEBE ver el item "Guardias" con icono `shield` que apunta a `/guardias`
