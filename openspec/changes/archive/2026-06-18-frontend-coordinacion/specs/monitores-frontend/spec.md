## ADDED Requirements

### Requirement: General monitor
The system SHALL provide ADMIN and COORDINADOR (with `auditoria:ver` permission) a general interaction panel with: actions-per-day chart, communication status aggregated by teacher (Pending/Sending/Sent/Failed/Cancelled), interactions by teacher×subject, and a configurable last-N actions log (default 200) (F9.1).

#### Scenario: View general monitor
- **WHEN** an ADMIN accesses `/monitores/general`
- **THEN** the system shows:
  - A chart of actions per day (last 30 days)
  - A table of communication status grouped by teacher
  - A table of interactions by teacher × subject with action type breakdown
  - A log of the last 200 actions (configurable)

#### Scenario: Filter last actions
- **WHEN** an ADMIN changes the max log entries filter from 200 to 50
- **THEN** the system shows only the last 50 actions

### Requirement: Coordination monitor
The system SHALL provide a coordination-specific monitor with date range filters (F2.9) showing per-teacher, per-subject interaction data.

#### Scenario: View coordination monitor
- **WHEN** a COORDINADOR accesses `/monitores/coordinacion`
- **THEN** the system shows interaction data filterable by date range, subject, and user

#### Scenario: Filter by date range
- **WHEN** a COORDINADOR sets date range "2026-08-01" to "2026-08-31"
- **THEN** the system shows only interactions within that range

### Requirement: Role-based data scoping
The system SHALL restrict monitor data based on the user's role: COORDINADOR sees only `(propio)` scope data, ADMIN sees all tenant data.

#### Scenario: COORDINADOR scope filtering
- **WHEN** a COORDINADOR (not ADMIN) accesses the general monitor
- **THEN** the system shows only data related to the COORDINADOR's assigned subjects
