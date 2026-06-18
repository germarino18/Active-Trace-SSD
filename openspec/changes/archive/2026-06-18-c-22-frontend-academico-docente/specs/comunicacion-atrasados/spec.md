## ADDED Requirements

### Requirement: PROFESOR can preview a communication to overdue students
The system SHALL generate and display a preview of the message that will be sent to selected overdue students.

#### Scenario: Select students and preview
- **WHEN** the PROFESOR navigates to `/materias/{id}/comunicar`
- **THEN** the system displays a list of overdue students with checkboxes for multi-selection
- **WHEN** the PROFESOR selects one or more students
- **THEN** the "Vista previa" button becomes enabled
- **WHEN** the PROFESOR clicks "Vista previa"
- **THEN** the system calls `POST /api/v1/materias/{id}/comunicaciones/preview` with the selected student IDs
- **THEN** the system displays a modal with the generated subject and body
- **THEN** the preview shows the personalized content for each selected student

### Requirement: PROFESOR can send communications
The system SHALL send the previewed communication to the selected students through the message queue system.

#### Scenario: Send communication
- **WHEN** the PROFESOR confirms the preview
- **THEN** the system calls `POST /api/v1/comunicaciones/enviar` with the materia ID and student IDs
- **THEN** the system displays a success message "Comunicación enviada a la cola de despacho"

### Requirement: PROFESOR can track communication status in real-time
The system SHALL display the current status of each sent message with live updates.

#### Scenario: Status tracking view
- **WHEN** communications have been sent for the current materia
- **THEN** the system calls `GET /api/v1/comunicaciones/{id}/status` every 3 seconds
- **THEN** the system displays a status table with columns: student name, current status (Pendiente / Enviando / OK / Fallido / Cancelado)
- **WHEN** a message status changes
- **THEN** the table updates in real-time without page reload
- **WHEN** all messages are in a terminal state (OK, Fallido, or Cancelado)
- **THEN** the polling stops

#### Scenario: Failed communication
- **WHEN** a message status is "Fallido"
- **THEN** the row is visually highlighted in error color
- **THEN** the error details (if available) are shown on hover or click
