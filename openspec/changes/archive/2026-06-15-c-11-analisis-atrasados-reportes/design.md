## Context

Activia-trace ya importa calificaciones y configura umbrales de aprobación (C-10), pero carece de una capa de análisis que transforme esos datos en información útil. No existen endpoints para consultar alumnos atrasados, ranking, reportes ni monitores. Todo el análisis actual es manual o externo.

El modelo actual tiene:
- `Calificacion`: nota por alumno×actividad (numérica y/o textual) con campo `aprobado` derivado
- `UmbralMateria`: umbral configurable por asignación×materia (umbral_pct y valores_aprobatorios textuales)
- `EntradaPadron`: alumno con datos demográficos y de cohorte
- `Materia`, `Dictado`, `Comision`: estructura académica (C-06)

No se requieren nuevas tablas. Todo el análisis es query-based sobre estos modelos.

## Goals / Non-Goals

**Goals:**
- Servicio `AnalisisService` con métodos de cómputo puro y consultas contra repositorios existentes
- Endpoints GET para cada funcionalidad (F2.2–F2.9), todos gated por permiso `atrasados:ver`
- Funciones de cómputo puro (testables sin DB) para reglas de negocio (RN-06 a RN-09)
- Monitores con filtros según rol (TUTOR/PROFESOR vs COORDINADOR/ADMIN)
- Auditoría en todas las consultas via audit-log existente

**Non-Goals:**
- No se crean nuevas tablas ni migraciones
- No se modifican modelos existentes (`Calificacion`, `UmbralMateria`, etc.)
- No se implementa UI frontend (esto es cambio exclusivo de backend)
- No se implementa exportación real a archivo (solo endpoint que devuelve datos estructurados listos para ser servidos como CSV/XLSX por el router)
- No se implementan cálculos de nota final ponderada (solo agrupación simple: promedio de actividades configuradas)

## Decisions

### D1: `AnalisisService` como servicio read-only cohesivo
En lugar de crear un servicio por funcionalidad, se crea un único `AnalisisService` con métodos especializados. La cohesión es alta (todos operan sobre el mismo par de entidades) y evita duplicación de lógica de umbral/resolución de defaults.

**Alternativa considerada**: Servicios separados (`AtrasadosService`, `RankingService`, `MonitorService`). Se descarta porque compartirían lógica de resolución de umbral y filtrado por asignaciones, lo que obligaría a una capa compartida o duplicación.

### D2: Funciones de cómputo puro separadas de consultas DB
Cada método público de `AnalisisService` sigue el patrón:
1. Obtener datos crudos del repositorio (CalificacionRepository, UmbralMateriaRepository)
2. Llamar a función pura que recibe datos y devuelve resultado computado
3. No hay lógica de negocio mezclada con queries

**Rationale**: Las funciones puras son triviales de testear sin DB (solo datos de entrada → salida esperada). Los tests de integración verifican solo la consulta, no la lógica.

### D3: Un solo endpoint de monitor con parámetros de rol
Los monitores F2.7, F2.8 y F2.9 se implementan como un único endpoint `/api/v1/analisis/monitor` que acepta filtros opcionales. La diferencia de comportamiento según el rol se resuelve en el servicio:
- TUTOR/PROFESOR: filtra automáticamente por `asignaciones_vigentes` del usuario
- COORDINADOR/ADMIN: permite todos los filtros incluyendo rango de fechas

**Rationale**: Reduce duplicación de endpoints. La lógica de "qué puedo ver" es una preocupación de autorización, no de presentación.

### D4: Default de umbral cuando no existe UmbralMateria
Si no existe `UmbralMateria` para el dictado consultado, se usa `umbral_pct=60` y `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`. Esta lógica ya existe en el spec de `configurar-umbral` y se replica en `AnalisisService` como fallback.

### D5: Detección de TPs sin corregir cruza contra finalización LMS
F2.6 requiere cruzar el reporte de finalización del LMS (importado en F1.2) contra las calificaciones importadas. El servicio recibe las finalizaciones como parámetro (ya consultadas por el repositorio correspondiente) y aplica el filtro RN-08 (solo actividades textuales).

**Nota**: La importación de finalizaciones (F1.2) puede no estar implementada aún. El diseño contempla que el endpoint acepte un parámetro opcional `finalizaciones` y, si no se provee, devuelva un error claro indicando que se requiere importar finalizaciones primero.

### D6: Permiso `atrasados:ver` en todos los endpoints
Se verifica via `require_permission("atrasados:ver")` en cada endpoint. No se definen permisos más granulares por funcionalidad (e.g., `ranking:ver`) porque el cambio completo se concibe como un módulo de análisis unificado.

## Risks / Trade-offs

- **[Rendimiento] Consultas sin índices específicos**: Las queries de monitor pueden recorrer muchas filas de Calificacion. Si el volumen es alto, se requerirán índices compuestos (tenant_id, materia_id, entrada_padron_id). → Mitigación: diseñar las queries con los filtros más comunes primero; crear índices en implementación si el plan EXPLAIN lo justifica.
- **[Datos faltantes] Finalización LMS no disponible**: Si F1.2 no está implementada, F2.6 no puede funcionar. → Mitigación: el endpoint devuelve error 400 con mensaje claro "Se requiere importar reporte de finalización LMS primero".
- **[Volumen] Monitores sin paginación**: Los resultados de monitores pueden ser extensos (cientos de alumnos × docenas de actividades). → Mitigación: todos los endpoints de monitor incluyen paginación offset/limit estándar.
- **[Consistencia] Umbral default vs configurado**: Si un PROFESOR configura el umbral después de que se consultaron reportes, los resultados pueden diferir. Esto es esperable y no se cachea. → Mitigación: siempre se lee el umbral vigente al momento de la consulta.
