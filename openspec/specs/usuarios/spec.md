## ADDED Requirements

### Requirement: Usuario profile model with 1:1 link to auth identity
The system SHALL provide a `usuario` table that holds the business profile of a person, linked 1:1 to the auth identity `users` via `user_id` (FK → `users.id`, UNIQUE, `ondelete=CASCADE`). The `usuario` table SHALL use BaseMixin, TenantMixin, SoftDeleteMixin and AuditMixin. The auth table `users` SHALL NOT receive any PII columns; the email SHALL remain only on `users.email` and SHALL NOT be duplicated on `usuario`.

#### Scenario: Profile linked to one auth identity
- **WHEN** a `usuario` row is created with a `user_id` pointing to an existing `users` row in the same tenant
- **THEN** the row is persisted and a second `usuario` row for the same `user_id` is rejected by the unique constraint

#### Scenario: Profile is tenant-scoped
- **WHEN** a repository lists `usuario` rows
- **THEN** only rows of the caller's tenant are returned (tenant filter by default)

#### Scenario: Deleting the auth identity cascades to the profile
- **WHEN** a `users` row is hard-removed
- **THEN** its linked `usuario` row is removed by the CASCADE

### Requirement: PII fields are encrypted at rest with AES-256
The system SHALL store `dni`, `cuil`, `cbu` and `alias_cbu` encrypted with AES-256 via an `EncryptedString` SQLAlchemy type that wraps the existing `encrypt_value`/`decrypt_value` primitives and the configured `ENCRYPTION_KEY`. These fields SHALL be ciphertext at rest and SHALL never appear in plaintext in logs or in API responses unless explicitly decrypted by an authorized path.

#### Scenario: PII is ciphertext in the database
- **WHEN** a `usuario` is persisted with a known `dni`/`cuil`/`cbu`/`alias_cbu`
- **THEN** the raw column values read directly from the database are NOT the plaintext values

#### Scenario: PII round-trips through the ORM
- **WHEN** the `usuario` is loaded via the ORM
- **THEN** the `dni`/`cuil`/`cbu`/`alias_cbu` attributes return the original plaintext values

#### Scenario: PII is not exposed in default responses
- **WHEN** the `usuario` is serialized by a list or default read endpoint
- **THEN** the response does NOT include the encrypted PII fields

### Requirement: Legajo is a business attribute, never a credential
The system SHALL treat `legajo` and `legajo_profesional` as optional business attributes of `usuario`, never as a primary key, credential, or session selector. Identity SHALL remain the internal UUID.

#### Scenario: Legajo is optional
- **WHEN** a `usuario` is created without a `legajo`
- **THEN** the row is persisted successfully

#### Scenario: Legajo cannot select a session
- **WHEN** a request supplies a `legajo` as a would-be identity selector
- **THEN** the identity used is the UUID from the verified JWT, not the legajo

### Requirement: Admin ABM for usuarios gated by usuarios:gestionar
The system SHALL expose `/api/admin/usuarios` for create, read, update and soft-delete of `usuario` profiles, gated by `require_permission("usuarios:gestionar")`, fail-closed. Deletion SHALL be soft (never hard delete).

#### Scenario: Authorized admin manages usuarios
- **WHEN** a caller with `usuarios:gestionar` creates a `usuario`
- **THEN** the profile is persisted in the caller's tenant

#### Scenario: Caller without permission is rejected
- **WHEN** a caller lacking `usuarios:gestionar` calls any `/api/admin/usuarios` endpoint
- **THEN** the response is 403 Forbidden and no change is made

#### Scenario: Delete is soft
- **WHEN** a `usuario` is deleted via the ABM
- **THEN** the row is marked `deleted_at` and remains in the database
