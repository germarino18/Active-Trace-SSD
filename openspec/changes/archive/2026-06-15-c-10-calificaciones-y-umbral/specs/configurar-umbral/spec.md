## ADDED Requirements

### Requirement: Configurar umbral de aprobación por materia (F2.1, RN-03)

El sistema SHALL permitir a un PROFESOR configurar el umbral de aprobación mínimo (porcentaje) para sus materias asignadas, así como la lista de valores textuales aprobatorios. El alcance (`scope`) es por `asignacion_id`: un PROFESOR solo puede configurar umbrales para dictados donde tiene asignación vigente.

El umbral por defecto SHALL ser 60% (`umbral_pct=60`). Si no existe `UmbralMateria` para una asignación×dictado, el sistema SHALL usar 60% como valor por omisión y `["Satisfactorio", "Supera lo esperado"]` como valores aprobatorios textuales por defecto.

#### Scenario: PROFESOR configura umbral de su materia
- **WHEN** un PROFESOR envía PUT con `asignacion_id`, `dictado_id`, `umbral_pct=70` y `valores_aprobatorios=["Satisfactorio", "Excelente"]`
- **THEN** el sistema crea o actualiza el `UmbralMateria`, recalcula `aprobado` en todas las `Calificacion` del dictado, y registra en audit log

#### Scenario: Umbral por defecto cuando no hay configuración
- **WHEN** no existe `UmbralMateria` para un dictado
- **THEN** el sistema usa `umbral_pct=60` y valores aprobatorios por defecto

#### Scenario: Configuración rechazada para dictado no asignado
- **WHEN** un PROFESOR intenta configurar umbral para un dictado sin asignación
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Validación de umbral_pct fuera de rango
- **WHEN** un usuario envía `umbral_pct` menor a 0 o mayor a 100
- **THEN** el sistema responde 422 con error de validación

### Requirement: Recalcular aprobado al cambiar umbral

Cuando se crea o actualiza un `UmbralMateria`, el sistema SHALL recalcular el campo `aprobado` de todas las `Calificacion` del mismo `dictado_id` que tengan `origen="Importado"`.

#### Scenario: Recalcular después de cambio de umbral
- **WHEN** un umbral se actualiza de 60% a 80%
- **THEN** las calificaciones del dictado con notas entre 6.0 y 7.9 cambian de `aprobado=True` a `aprobado=False`
