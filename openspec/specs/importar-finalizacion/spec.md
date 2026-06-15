## ADDED Requirements

### Requirement: Importación de reporte de finalización (F1.2)

El sistema SHALL permitir importar un reporte de finalización desde archivo `.xlsx` o `.csv` que detecta TPs (trabajos prácticos) entregados pero sin calificación asignada. El flujo SHALL ser de dos pasos (preview → confirm) consistente con F1.1.

El sistema SHALL detectar automáticamente columnas que representan TPs (encabezados que contienen "TP" o "Trabajo Práctico") y marcar aquellas filas donde el alumno entregó pero no tiene nota (celda vacía o con marcador "Sin calificar" / "Pendiente").

#### Scenario: Preview detecta TPs sin calificar
- **WHEN** un usuario con `calificaciones:importar` sube un archivo con columnas "TP1", "TP2" y filas con algunas celdas vacías
- **THEN** el sistema devuelve preview con columnas detectadas, filas, y un resumen de TPs sin calificar por alumno

#### Scenario: Confirm crea calificaciones con origen Importado
- **WHEN** el usuario confirma la importación con un preview_token válido
- **THEN** el sistema crea registros `Calificacion` con `origen="Importado"` y `nota_numerica=NULL`, `nota_textual=NULL`, `aprobado=False` para los TPs sin calificar

#### Scenario: Preview rechazado sin permiso
- **WHEN** un usuario sin `calificaciones:importar` intenta previsualizar
- **THEN** el sistema responde 403 Forbidden
