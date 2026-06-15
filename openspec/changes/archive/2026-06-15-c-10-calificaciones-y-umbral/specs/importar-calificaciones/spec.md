## ADDED Requirements

### Requirement: Importación de calificaciones desde archivo LMS con preview (F1.1)

El sistema SHALL permitir importar calificaciones de alumnos desde archivos `.xlsx` o `.csv` en un flujo de dos pasos: (1) preview que parsea, detecta columnas numéricas (RN-01: encabezado termina en `(Real)`) y textuales, agrupa por actividad, y devuelve muestra sin persistir; (2) confirm que persiste las calificaciones seleccionadas, calculando `aprobado` derivado según el umbral vigente del dictado o el defecto 60%.

Las columnas numéricas cuyos encabezados terminan en `(Real)` SHALL tratarse como calificaciones de una misma actividad (e.g., `TP1 (Real)` y `TP1 (Real).1` son intentos de la misma actividad). Las columnas con valores textuales (Satisfactorio, Supera lo esperado, etc.) SHALL detectarse como notas textuales.

El endpoint SHALL estar gated por `calificaciones:importar`. Para PROFESOR, el `dictado_id` debe corresponder a sus asignaciones; para COORDINADOR, cualquier dictado del tenant.

#### Scenario: Preview de archivo con columnas numéricas y textuales
- **WHEN** un usuario con `calificaciones:importar` sube un archivo con columnas "TP1 (Real)", "TP1 (Real).1", "Cualitativa" con valores numéricos y "Satisfactorio"/"Insuficiente"
- **THEN** el sistema detecta "TP1 (Real)" y "TP1 (Real).1" como la misma actividad "TP1" con dos intentos numéricos, y "Cualitativa" como actividad textual. Devuelve preview con actividades agrupadas, muestra de filas, y un preview_token

#### Scenario: Preview rechazado sin permiso
- **WHEN** un usuario sin `calificaciones:importar` intenta previsualizar un archivo
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Preview rechazado por dictado no autorizado (PROFESOR)
- **WHEN** un PROFESOR intenta previsualizar para un dictado al que no está asignado
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Confirm importa solo actividades seleccionadas
- **WHEN** un usuario envía preview_token válido con `actividades_seleccionadas: ["TP1"]` y `dictado_id`
- **THEN** el sistema persiste solo las calificaciones de "TP1", calcula `aprobado` según umbral del dictado (o 60%), registra `CALIFICACIONES_IMPORTAR` en audit log

#### Scenario: Confirm con token expirado o inválido
- **WHEN** un usuario envía un preview_token que no existe o expiró
- **THEN** el sistema responde 422 con error de validación

### Requirement: Cálculo de aprobado derivado

El sistema SHALL calcular el campo `aprobado` al momento de importar/configurar umbral:
- Si existe `nota_numerica`: `aprobado = True` si `nota_numerica >= umbral_pct * 0.01 * nota_maxima` (nota_maxima = 10 por defecto, configurable)
- Si solo existe `nota_textual`: `aprobado = True` si el valor está en `valores_aprobatorios` del `UmbralMateria` correspondiente
- Si existe `nota_numerica` y `nota_textual`: se considera aprobado si cumple AL MENOS UNA de las condiciones

#### Scenario: Aprobado por nota numérica
- **WHEN** se importa una calificación con `nota_numerica=7.5` para un dictado con `umbral_pct=60`
- **THEN** `aprobado = True` (7.5 >= 6.0)

#### Scenario: Aprobado por nota textual
- **WHEN** se importa una calificación con `nota_textual="Satisfactorio"` y el umbral tiene `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`
- **THEN** `aprobado = True`

#### Scenario: Desaprobado por debajo del umbral
- **WHEN** se importa una calificación con `nota_numerica=4.0` para un dictado con `umbral_pct=60`
- **THEN** `aprobado = False`

### Requirement: Aislamiento multi-tenant en calificaciones

Toda importación y consulta de calificaciones SHALL estar acotada al `tenant_id` de la sesión.

#### Scenario: Importación a dictado de otro tenant rechazada
- **WHEN** un usuario intenta importar calificaciones para un `dictado_id` de otro tenant
- **THEN** el sistema responde 404 (dictado no encontrado)
