## ADDED Requirements

### Requirement: Communication to overdue students no longer requires an activity
The system SHALL support sending a communication to overdue students with the activity being OPTIONAL, in addition to the existing per-activity flow. Omitting the activity SHALL NOT prevent sending.

#### Scenario: Send without choosing an activity
- **WHEN** the PROFESOR composes a comunicado to overdue students and does not select an activity
- **THEN** the system SHALL enqueue the communication without tying it to any activity
- **THEN** the message templates SHALL render using only the student/materia/docente variables (no activity-specific variable is required)

#### Scenario: Per-activity flow remains available
- **WHEN** the PROFESOR uses the existing per-dictado comunicado flow that selects an activity
- **THEN** that flow SHALL continue to work unchanged

### Requirement: Communication recipients can be individual or bulk
The system SHALL support communications targeting either a single overdue student (individual) or all overdue students (bulk), via an explicit recipient set.

#### Scenario: Individual recipient
- **WHEN** the recipient set contains exactly one student
- **THEN** the system SHALL enqueue the communication only for that student

#### Scenario: Bulk recipients across materias
- **WHEN** the recipient set contains students from multiple materias
- **THEN** the system SHALL enqueue the communication for all of them, grouping by materia, and SHALL keep routing every message through the approval-gated pipeline
