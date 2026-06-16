## ADDED Requirements

### Requirement: Registro de resultados de coloquio
El sistema SHALL permitir que un usuario con permiso `coloquios:gestionar` registre el resultado (`ResultadoEvaluacion`) de un ALUMNO en una convocatoria. El resultado SHALL contener: `evaluacion_id`, `alumno_id`, y `nota_final` (texto, puede ser numérica o cualitativa). Un ALUMNO PUEDE tener múltiples resultados en distintas convocatorias, pero UN SOLO resultado por convocatoria. El registro de un resultado SHALL ser inmutable (no se puede modificar ni eliminar una vez registrado).

#### Scenario: Registrar resultado de alumno en convocatoria
- **WHEN** un COORDINADOR registra el resultado de un ALUMNO en una convocatoria con `nota_final = "8 (Ocho)"`
- **THEN** se crea un ResultadoEvaluacion, y se registra auditoría con código `COLOQUIO_REGISTRAR_RESULTADO`

#### Scenario: Resultado duplicado es rechazado
- **WHEN** un COORDINADOR intenta registrar un segundo resultado para el mismo ALUMNO en la misma convocatoria
- **THEN** el sistema rechaza la operación con error 422 (resultado ya registrado)

#### Scenario: Modificar resultado registrado es rechazado
- **WHEN** un COORDINADOR intenta modificar un resultado ya registrado
- **THEN** el sistema rechaza la operación con error 405 (no permitido)

#### Scenario: Registrar resultado de alumno no importado es rechazado
- **WHEN** un COORDINADOR intenta registrar resultado de un ALUMNO que no está importado en la convocatoria
- **THEN** el sistema rechaza la operación con error 422

#### Scenario: Aislamiento multi-tenant en resultados
- **WHEN** un COORDINADOR del Tenant A registra un resultado para un ALUMNO del Tenant A
- **THEN** el resultado solo es visible en el Tenant A; un COORDINADOR del Tenant B no puede verlo ni modificarlo

### Requirement: Registro académico consolidado de coloquios
El sistema SHALL exponer un endpoint con permiso `coloquios:ver` que consolide los resultados de coloquios del tenant. La vista SHALL devolver: `alumno` (nombre, legajo), `materia` (desde dictado), `instancia`, `tipo`, `nota_final`, `fecha_reserva`. SHALL soportar filtros opcionales: `dictado_id`, `alumno_id`, `evaluacion_id`.

#### Scenario: COORDINADOR consulta registro académico
- **WHEN** un COORDINADOR consulta el registro académico consolidado sin filtros
- **THEN** el sistema devuelve todos los resultados del tenant, cada uno con datos del alumno, materia, instancia y nota

#### Scenario: Filtrar registro académico por dictado
- **WHEN** un COORDINADOR consulta el registro académico con filtro `dictado_id = X`
- **THEN** el sistema devuelve solo los resultados de convocatorias de ese dictado

#### Scenario: PROFESOR consulta registro de sus dictados
- **WHEN** un PROFESOR consulta el registro académico
- **THEN** el sistema devuelve solo los resultados de convocatorias cuyos dictados le pertenecen `(propio)`
