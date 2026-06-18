## ADDED Requirements

### Requirement: PROFESOR can detect uncorrected deliveries
The system SHALL allow a PROFESOR to upload a completion report and detect activities that were submitted but not yet graded.

#### Scenario: Upload completion report
- **WHEN** the PROFESOR navigates to `/materias/{id}/entregas-pendientes`
- **THEN** the system displays a file upload area accepting completion report files
- **WHEN** the PROFESOR uploads a completion report
- **THEN** the system calls `POST /api/v1/materias/{id}/detectar-entregas` with the file
- **THEN** the system displays a table of potentially uncorrected deliveries: student name, activity name, submission date, grade status (pendiente)

#### Scenario: Empty detection result
- **WHEN** no uncorrected deliveries are detected
- **THEN** the system displays "No se detectaron entregas sin corregir"

### Requirement: PROFESOR can export uncorrected deliveries
The system SHALL allow the PROFESOR to download the list of uncorrected deliveries as a file.

#### Scenario: Export list
- **WHEN** uncorrected deliveries are displayed
- **THEN** an "Exportar" button is visible
- **WHEN** the PROFESOR clicks "Exportar"
- **THEN** the system calls `GET /api/v1/materias/{id}/entregas-pendientes/export`
- **THEN** the browser downloads the file
