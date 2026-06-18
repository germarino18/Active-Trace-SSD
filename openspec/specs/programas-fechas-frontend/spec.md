## ADDED Requirements

### Requirement: Upload and associate subject programs
The system SHALL allow ADMIN and COORDINADOR to upload an official program document (file) and associate it with a specific subject × career × cohort combination, with a descriptive title (F5.3).

#### Scenario: Upload program
- **WHEN** a COORDINADOR uploads a PDF file with title "Programa Álgebra 2026" for subject "Álgebra", career "Ingeniería", cohort "MAR-2026"
- **THEN** the system creates a ProgramaMateria record with a reference to the uploaded file
- **AND** shows the program in the programs list

#### Scenario: View programs list
- **WHEN** a COORDINADOR accesses `/programas`
- **THEN** the system shows a table of all programs with columns: materia, carrera, cohorte, título, fecha_subida
- **AND** provides a download link for the file

#### Scenario: Delete program
- **WHEN** an ADMIN confirms deletion of a program
- **THEN** the system removes the program reference

### Requirement: Manage academic exam dates
The system SHALL allow COORDINADOR and ADMIN to register and edit exam dates (partial exams, practical work, colloquiums) by subject, cohort, and instance number, with tabular and calendar views (F5.4).

#### Scenario: Create exam date
- **WHEN** a COORDINADOR creates an exam date for subject "Álgebra", type "Parcial", instance "1", date "2026-09-15", cohort "MAR-2026"
- **THEN** the system creates the exam date and shows it in the list
- **AND** the date appears in the calendar view

#### Scenario: Edit exam date
- **WHEN** a COORDINADOR changes an exam date from "2026-09-15" to "2026-09-22"
- **THEN** the system updates the date
- **AND** shows a success toast

#### Scenario: Calendar view
- **WHEN** a COORDINADOR switches to calendar view
- **THEN** the system shows exam dates on a monthly calendar, color-coded by type (partial/TP/colloquium)

### Requirement: Generate LMS content fragment
The system SHALL generate a formatted content fragment with exam dates ready for LMS publication.

#### Scenario: Generate dates HTML
- **WHEN** a COORDINADOR clicks "Generar contenido para aula virtual"
- **THEN** the system returns HTML content with all exam dates for the selected subject×cohort
