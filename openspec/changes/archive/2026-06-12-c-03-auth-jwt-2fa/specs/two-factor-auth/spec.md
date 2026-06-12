## ADDED Requirements

### Requirement: POST /api/auth/2fa/enroll — generate TOTP secret
The system SHALL provide an endpoint (authenticated) that generates a new TOTP secret for the current user. It returns:
- `secret`: the Base32-encoded secret (plaintext, one-time display)
- `qr_uri`: `otpauth://totp/{issuer}:{email}?secret={secret}&issuer={issuer}` URI for QR code generation on the client

The secret is encrypted with AES-256-GCM and stored in the user's `totp_secret` column. However, 2FA is NOT yet enabled — the user must verify first via `/api/auth/2fa/verify`.

Calling enroll when 2FA is already enabled SHOULD return an error (disable first).

#### Scenario: Enroll generates secret and QR URI
- **WHEN** calling POST /api/auth/2fa/enroll with a valid access token for a user WITHOUT 2FA
- **THEN** the response is 200 with `secret` (Base32), `qr_uri` (otpauth:// URI), and the encrypted totp_secret is stored in the database

#### Scenario: Enroll when 2FA already enabled
- **WHEN** calling POST /api/auth/2fa/enroll for a user who already has 2FA enabled
- **THEN** the response is 409 Conflict with error "2FA is already enabled. Disable first to re-enroll."

#### Scenario: Enroll requires authentication
- **WHEN** calling POST /api/auth/2fa/enroll without a valid access token
- **THEN** the response is 401 Unauthorized

### Requirement: POST /api/auth/2fa/verify — confirm TOTP setup
The system SHALL provide an endpoint (authenticated) that accepts `totp_code`. If the code is valid for the stored TOTP secret, it sets `totp_enabled_at` to the current timestamp, officially enabling 2FA for the user.

#### Scenario: Verify with valid TOTP code
- **WHEN** calling POST /api/auth/2fa/verify with a valid totp_code matching the stored secret
- **THEN** the response is 200 OK, and the user's totp_enabled_at is set to the current timestamp

#### Scenario: Verify with invalid TOTP code
- **WHEN** calling POST /api/auth/2fa/verify with an invalid totp_code
- **THEN** the response is 401 Unauthorized, and totp_enabled_at remains NULL

#### Scenario: Verify without prior enrollment
- **WHEN** calling POST /api/auth/2fa/verify for a user who has no totp_secret stored
- **THEN** the response is 400 Bad Request with error "No pending enrollment. Call /2fa/enroll first."

### Requirement: POST /api/auth/2fa/disable — remove 2FA
The system SHALL provide an endpoint (authenticated) that accepts `password` and `totp_code`. It validates both, then clears `totp_secret` and `totp_enabled_at`, disabling 2FA.

This requires TWO factors to disable: current password (something you know) and current TOTP (something you have). This prevents a stolen access token from disabling 2FA.

#### Scenario: Disable 2FA with correct password and TOTP
- **WHEN** calling POST /api/auth/2fa/disable with the correct password and a valid totp_code
- **THEN** the response is 200 OK, totp_secret is set to NULL, totp_enabled_at is set to NULL

#### Scenario: Disable 2FA with wrong password
- **WHEN** calling POST /api/auth/2fa/disable with an incorrect password
- **THEN** the response is 401 Unauthorized, and 2FA remains enabled

#### Scenario: Disable 2FA with invalid TOTP
- **WHEN** calling POST /api/auth/2fa/disable with the correct password but invalid totp_code
- **THEN** the response is 401 Unauthorized, and 2FA remains enabled

### Requirement: TOTP verification uses pyotp
The system SHALL use the `pyotp` library for TOTP generation and verification with the following parameters:
- Algorithm: SHA1 (TOTP standard)
- Digits: 6
- Interval: 30 seconds
- Window: 1 (allows ±1 interval for clock skew)

#### Scenario: TOTP code is 6 digits
- **WHEN** generating a TOTP code from a valid secret
- **THEN** the code is exactly 6 numeric digits

#### Scenario: Verify current window code
- **WHEN** verifying a TOTP code generated in the current 30-second window
- **THEN** verification returns True

#### Scenario: Verify code from adjacent window
- **WHEN** verifying a TOTP code generated 25 seconds ago (previous window)
- **THEN** verification returns True (window=1 allows skew)

#### Scenario: Verify code from distant window
- **WHEN** verifying a TOTP code generated 90 seconds ago (3 windows ago)
- **THEN** verification returns False
