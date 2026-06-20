## ADDED Requirements

### Requirement: Remediation script detects and re-encrypts plaintext emails
The system SHALL provide a one-shot script that reads `entrada_padron.email` via raw SQL, identifies plaintext values (not yet encrypted), encrypts them using `encrypt_value()` from `app.core.security`, and updates the rows in-place.

#### Scenario: All emails are plaintext
- **WHEN** the script runs against a database where all `entrada_padron.email` values are plaintext
- **THEN** every non-null value SHALL be encrypted with AES-256-GCM
- **THEN** the script SHALL log `"Remediated X rows"` and exit with code 0

#### Scenario: Some emails are already encrypted (e.g. partial fix)
- **WHEN** the script runs against a database where some `entrada_padron.email` values are already encrypted
- **THEN** the script SHALL skip values that are valid base64 AND successfully decrypt
- **THEN** the script SHALL encrypt and update the remaining plaintext values
- **THEN** the script SHALL log `"Remediated X rows, skipped Y rows"` and exit with code 0

#### Scenario: Read-only mode
- **WHEN** the script runs with `--dry-run` flag
- **THEN** it SHALL print which rows WOULD be updated without actually modifying the database
- **THEN** it SHALL exit with code 0

#### Scenario: All values are already encrypted (no-op)
- **WHEN** the script runs and every `entrada_padron.email` value is already encrypted
- **THEN** the script SHALL log `"No rows to remediate"` and exit with code 0

#### Scenario: Connection failure or encryption error
- **WHEN** the script encounters any error during read or update
- **THEN** it SHALL roll back the current transaction
- **THEN** it SHALL log the error and row ID (if applicable)
- **THEN** it SHALL exit with code 1
