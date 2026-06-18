## ADDED Requirements

### Requirement: Panel de métricas de uso
El sistema SHALL mostrar al ADMIN y COORDINADOR (con permiso `auditoria:ver`) un panel con métricas de uso del sistema, incluyendo:

- **Acciones por día**: gráfico de serie temporal de actividad por usuario
- **Estado de comunicaciones**: distribución de estados (Pendiente / Enviando / OK / Fallido / Cancelado) por docente y materia
- **Interacciones por docente y materia**: métricas detalladas de uso por tipo de acción (análisis de desempeño, vista previa, importación, envío, limpieza de datos, configuración de umbral, emails generados, lotes procesados)

#### Scenario: Ver acciones por día
- **WHEN** el ADMIN accede al panel de métricas
- **THEN** el sistema muestra un gráfico de barras o líneas con acciones por día

#### Scenario: Ver estado de comunicaciones
- **WHEN** el ADMIN accede a la sección "Estado de comunicaciones"
- **THEN** el sistema muestra la distribución de estados agrupada por docente y materia

#### Scenario: Ver interacciones por docente
- **WHEN** el ADMIN selecciona un docente en el panel de métricas
- **THEN** el sistema muestra el desglose de interacciones por tipo de acción para ese docente

### Requirement: Filtros del panel de métricas
El sistema SHALL permitir filtrar el panel de métricas por: rango de fechas, materia, usuario y estado de actividad.

#### Scenario: Filtrar métricas por rango de fechas
- **WHEN** el ADMIN selecciona un rango de fechas en los filtros del panel
- **THEN** el sistema actualiza todos los gráficos y tablas para mostrar solo datos dentro de ese rango
