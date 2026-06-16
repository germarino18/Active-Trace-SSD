## ADDED Requirements

### Requirement: User can see visible avisos for their role and scope
The system SHALL return avisos visible to the requesting user based on:
- aviso.activo = true
- aviso.inicio_en <= now <= aviso.fin_en (RN-18)
- aviso.alcance matches the user's context:
  - GLOBAL: all users see it
  - POR_MATERIA: user must be enrolled/assigned to that materia
  - POR_COHORTE: user must belong to that cohorte
  - POR_ROL: user must have the matching role
- If aviso.rol_destino is set, only users with that role see the aviso (in addition to alcance filtering)

#### Scenario: User sees global avisos
- **WHEN** an ALUMNO sends GET /api/v1/avisos/visible
- **THEN** the response includes all active avisos with alcance=GLOBAL within their visibility window

#### Scenario: User sees avisos by role matching
- **WHEN** a PROFESOR sends GET /api/v1/avisos/visible
- **THEN** the response includes active avisos with alcance=POR_ROL and rol_destino=PROFESOR (or PROFESOR or higher) that are within their visibility window

#### Scenario: User sees avisos by materia enrollment
- **WHEN** an ALUMNO enrolled in materia X sends GET /api/v1/avisos/visible
- **THEN** the response includes active avisos with alcance=POR_MATERIA and materia_id=X within their visibility window

#### Scenario: User sees avisos by cohorte membership
- **WHEN** an ALUMNO belonging to cohorte Y sends GET /api/v1/avisos/visible
- **THEN** the response includes active avisos with alcance=POR_COHORTE and cohorte_id=Y within their visibility window

### Requirement: Visible avisos are filtered by active flag and date window
The system SHALL only return avisos where activo=true AND now is between inicio_en and fin_en (RN-18).

#### Scenario: Expired aviso is not visible
- **WHEN** a user requests visible avisos and an aviso has fin_en < now
- **THEN** that aviso is excluded from the response

#### Scenario: Future aviso is not visible
- **WHEN** a user requests visible avisos and an aviso has inicio_en > now
- **THEN** that aviso is excluded from the response

### Requirement: Visible avisos are ordered by orden then created_at
The system SHALL return visible avisos sorted by orden ascending (lower = higher priority), then by created_at descending (newer first).

#### Scenario: Avisos ordered correctly
- **WHEN** a user requests visible avisos
- **THEN** the avisos are ordered by orden ascending, then created_at descending

### Requirement: Visible avisos include acknowledgment status
The system SHALL indicate for each visible aviso whether the current user has already confirmed it (acknowledged: boolean), derived from AcknowledgmentAviso table.

#### Scenario: Acknowledged aviso shows confirmed
- **WHEN** a user who already confirmed aviso X requests visible avisos
- **THEN** aviso X shows acknowledged=true in the response

#### Scenario: Unacknowledged aviso shows pending
- **WHEN** a user who has NOT confirmed aviso X requests visible avisos
- **THEN** aviso X shows acknowledged=false in the response
