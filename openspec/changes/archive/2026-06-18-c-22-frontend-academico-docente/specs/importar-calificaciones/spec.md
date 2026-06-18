## ADDED Requirements

### Requirement: PROFESOR can import grades from a file
The system SHALL allow a PROFESOR to upload an LMS-exported grade file (CSV or XLSX) for a selected materia, preview the detected activities, select which to include, and confirm the import.

#### Scenario: Upload grade file
- **WHEN** the PROFESOR navigates to `/materias/{id}/importar`
- **THEN** the system displays a file upload area accepting `.csv` and `.xlsx` files
- **WHEN** the PROFESOR selects a valid file
- **THEN** the system calls `POST /api/v1/materias/{id}/importar-calificaciones` with the file as `multipart/form-data`
- **THEN** the system shows a loading indicator during upload
- **WHEN** upload succeeds
- **THEN** the system displays a preview table with detected activities (name, type, number of grades) and detected students

#### Scenario: Activity selection in preview
- **WHEN** the preview is displayed
- **THEN** each detected activity has a toggle/checkbox to include or exclude it from the analysis
- **WHEN** all activities are toggled as desired
- **THEN** the PROFESOR clicks "Confirmar importación"
- **THEN** the system calls `POST /api/v1/materias/{id}/importar-calificaciones` with the selected activity IDs

#### Scenario: Invalid file format
- **WHEN** the PROFESOR selects a file that is not CSV or XLSX
- **THEN** the system displays an error message "Formato de archivo no soportado. Use .csv o .xlsx"

#### Scenario: Upload error
- **WHEN** the server returns an error during upload
- **THEN** the system displays the error message returned by the server
- **THEN** the file selection is preserved so the user can retry without re-selecting

### Requirement: PROFESOR can configure threshold percentage
The system SHALL allow a PROFESOR to set the passing threshold percentage for a materia, which affects all overdue/ranking calculations.

#### Scenario: Configure threshold
- **WHEN** the PROFESOR is on the import page or materia configuration area
- **THEN** a threshold input field is displayed with the current value (default 60%)
- **WHEN** the PROFESOR enters a percentage (1-100) and confirms
- **THEN** the system calls `POST /api/v1/materias/{id}/configurar-umbral` with the new threshold value
- **THEN** the system displays a success confirmation

#### Scenario: Invalid threshold value
- **WHEN** the PROFESOR enters a value outside 1-100 range
- **THEN** the system displays a validation error "El umbral debe ser un valor entre 1 y 100"
- **THEN** the input is not submitted
