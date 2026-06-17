## ADDED Requirements

### Requirement: ABM de SalarioPlus por grupo y rol con vigencia temporal (F10.4, RN-31/RN-33)

El sistema SHALL permitir administrar SalarioPlus: registros de adicional salarial por grupo de materia y rol, con vigencia temporal. Un docente puede acumular plus de distintos grupos si dicta materias de varios de ellos (RN-33).

#### Scenario: Crear SalarioPlus exitoso
- **GIVEN** un usuario autenticado con permiso `liquidaciones:configurar-salarios`
- **WHEN** envía `POST /api/v1/liquidaciones/salarios-plus` con `{grupo: "PROG", rol: "PROFESOR", descripcion: "Materias de Programación", monto: 25000.00, desde: "2026-01-01", hasta: null}`
- **THEN** el sistema crea el registro y responde 201

#### Scenario: Listar SalarioPlus con filtros
- **WHEN** un usuario consulta `GET /api/v1/liquidaciones/salarios-plus?grupo=PROG&rol=PROFESOR`
- **THEN** el sistema devuelve los registros que coinciden con ambos filtros

#### Scenario: Listar plus vigentes en fecha
- **WHEN** un usuario consulta `GET /api/v1/liquidaciones/salarios-plus?vigente_en=2026-06-01`
- **THEN** el sistema devuelve solo registros con `desde <= 2026-06-01 AND (hasta IS NULL OR hasta >= 2026-06-01)`

#### Scenario: Soft delete SalarioPlus
- **WHEN** un usuario elimina `DELETE /api/v1/liquidaciones/salarios-plus/{id}`
- **THEN** el sistema aplica soft delete

### Requirement: Unicidad de vigencia por (grupo, rol)

No pueden existir dos SalarioPlus con el mismo grupo y rol con vigencias superpuestas.

#### Scenario: Rechazar solapamiento
- **GIVEN** existe SalarioPlus para (PROG, PROFESOR) con `desde=2026-01-01, hasta=null`
- **WHEN** se intenta crear otro SalarioPlus para (PROG, PROFESOR) con `desde=2026-03-01, hasta=null`
- **THEN** el sistema responde 409 Conflict

### Requirement: Aislamiento multi-tenant en SalarioPlus

SalarioPlus de diferentes tenants NO se entremezclan.

#### Scenario: Aislamiento
- **GIVEN** tenant A tiene SalarioPlus (PROG, PROFESOR)
- **WHEN** usuario del tenant B lista SalarioPlus
- **THEN** no aparece el registro del tenant A
