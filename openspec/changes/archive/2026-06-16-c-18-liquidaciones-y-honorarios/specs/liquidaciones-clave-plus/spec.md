## ADDED Requirements

### Requirement: Catálogo ClavePlus administrable (E22)

El sistema SHALL permitir administrar el catálogo de ClavePlus: códigos que categorizan materias para determinar el plus salarial aplicable. Cada ClavePlus tiene código único por tenant, descripción y vigencia.

#### Scenario: Crear ClavePlus
- **GIVEN** usuario con `liquidaciones:configurar-salarios`
- **WHEN** envía `POST /api/v1/liquidaciones/claves-plus` con `{codigo: "PROG", descripcion: "Materias de Programación", desde: "2026-01-01", hasta: null}`
- **THEN** el sistema responde 201 con el registro creado

#### Scenario: Unicidad de código por tenant
- **WHEN** se intenta crear un ClavePlus con código "PROG" que ya existe en el mismo tenant
- **THEN** el sistema responde 409 Conflict

#### Scenario: Listar ClavePlus
- **WHEN** consulta `GET /api/v1/liquidaciones/claves-plus`
- **THEN** devuelve todos los ClavePlus del tenant

### Requirement: Asignación MateriaClavePlus con vigencia (E23)

El sistema SHALL permitir asignar una ClavePlus a una Materia con vigencia temporal. Una materia SOLO puede tener una MateriaClavePlus vigente en un momento dado. La asignación es la que determina qué plus paga una materia independientemente de la carrera donde se dicte.

#### Scenario: Asignar clave a materia
- **GIVEN** existe una Materia y un ClavePlus
- **WHEN** `POST /api/v1/liquidaciones/materias-clave-plus` con `{materia_id, clave_plus_id, desde: "2026-01-01", hasta: null}`
- **THEN** el sistema responde 201

#### Scenario: Rechazar doble asignación vigente
- **GIVEN** existe MateriaClavePlus vigente para materia X con clave PROG
- **WHEN** se intenta asignar otra clave a materia X con vigencias solapadas
- **THEN** el sistema responde 409 Conflict

#### Scenario: Permitir re-asignación con vigencias no solapadas
- **GIVEN** existe MateriaClavePlus para materia X con `desde=2025-01-01, hasta=2025-12-31`
- **WHEN** se asigna otra clave a materia X con `desde=2026-01-01, hasta=null`
- **THEN** el sistema responde 201 (vigencias no se solapan)

### Requirement: Resolución de clave vigente para una materia en una fecha

El sistema SHALL proveer una función para obtener la ClavePlus vigente de una Materia en una fecha dada.

#### Scenario: Clave vigente encontrada
- **WHEN** se consulta clave vigente para materia X en fecha 2026-06-01
- **GIVEN** existe MateriaClavePlus con `desde <= 2026-06-01 AND (hasta IS NULL OR hasta >= 2026-06-01)`
- **THEN** devuelve la ClavePlus asociada

#### Scenario: Materia sin clave asignada
- **WHEN** se consulta clave vigente para materia X
- **GIVEN** NO existe MateriaClavePlus vigente para esa materia
- **THEN** el sistema lanza excepción de negocio "La materia X no tiene una ClavePlus asignada para la fecha indicada"
