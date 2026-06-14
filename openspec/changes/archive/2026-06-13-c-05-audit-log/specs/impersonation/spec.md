## ADDED Requirements

### Requirement: Permission-gated impersonation start
The system SHALL allow a user holding the `impersonacion:usar` permission to start an impersonation session over a target user via `POST /api/v1/auth/impersonate/{user_id}`. The endpoint MUST be fail-closed: a user without the permission receives 403.

#### Scenario: Authorized user starts impersonation
- **WHEN** a user with `impersonacion:usar` calls impersonate on a valid same-tenant target
- **THEN** a new access token is issued whose `sub` is the target user and whose `actor_id` is the real user

#### Scenario: Unauthorized user is rejected
- **WHEN** a user lacking `impersonacion:usar` calls the impersonate endpoint
- **THEN** the system responds 403 and no token is issued and no session is started

### Requirement: Tenant-scoped target
Impersonation SHALL only target a user in the same tenant as the impersonator. The target user MUST be resolved within the authenticated user's tenant; a cross-tenant target MUST be rejected.

#### Scenario: Cross-tenant target is rejected
- **WHEN** an authorized user attempts to impersonate a user belonging to a different tenant
- **THEN** the request is rejected and no impersonation token is issued

### Requirement: Distinguishable impersonation session
An impersonation session SHALL be distinguishable from a normal session by carrying an `actor_id` claim that identifies the real logged-in user. When `actor_id` is absent, the session is normal and the actor equals `sub`.

#### Scenario: Normal session has no actor_id
- **WHEN** a user authenticates normally
- **THEN** the access token carries no `actor_id` claim and the session actor equals the token subject

#### Scenario: Impersonation session carries actor_id
- **WHEN** an impersonation session is active
- **THEN** the resolved session exposes both the impersonated user (`sub`) and the real actor (`actor_id`)

### Requirement: Ending impersonation
The system SHALL provide `POST /api/v1/auth/impersonate/end`, valid only for a token bearing an `actor_id`, which issues a new normal token for the real actor.

#### Scenario: End restores the real actor session
- **WHEN** the end endpoint is called with a valid impersonation token
- **THEN** a new normal token is issued for the real actor with no `actor_id` claim

#### Scenario: End on a normal token is rejected
- **WHEN** the end endpoint is called with a token that has no `actor_id`
- **THEN** the request is rejected

### Requirement: Impersonation is audited
The start and end of every impersonation session SHALL be recorded in the audit log, attributed to the real actor, identifying the impersonated user.

#### Scenario: Start is audited
- **WHEN** an impersonation session is started
- **THEN** an audit record with action `IMPERSONACION_INICIAR` is written, with `actor_id` = real user and `impersonado_id` = target user

#### Scenario: End is audited
- **WHEN** an impersonation session is ended
- **THEN** an audit record with action `IMPERSONACION_FINALIZAR` is written, attributed to the real actor

### Requirement: Identity never from request data
Impersonation SHALL never be activated by a request parameter, body field, or header on a normal request. The only way to act as another user is to obtain a re-issued JWT from the impersonate endpoint; subsequent requests derive identity solely from that verified token.

#### Scenario: No act-as header is honored
- **WHEN** a normal authenticated request includes an arbitrary "act-as" parameter or header
- **THEN** the system ignores it and resolves identity exclusively from the verified JWT
