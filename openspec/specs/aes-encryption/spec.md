## ADDED Requirements

### Requirement: Encrypt plaintext to base64 string
The system SHALL provide `encrypt_value(plaintext: str, key: bytes) -> str` that encrypts a plaintext string using AES-256-GCM and returns a base64-encoded string containing nonce + tag + ciphertext.

#### Scenario: Encrypt produces non-empty base64 string
- **WHEN** calling `encrypt_value("sensitive data", key)` with a valid 32-byte key
- **THEN** the result is a non-empty base64-encoded string

#### Scenario: Same plaintext produces different ciphertexts
- **WHEN** calling `encrypt_value("same data", key)` twice with the same key
- **THEN** the two resulting ciphertexts are different due to random nonce

### Requirement: Decrypt base64 string to original plaintext
The system SHALL provide `decrypt_value(ciphertext_b64: str, key: bytes) -> str` that decrypts a base64-encoded ciphertext (produced by `encrypt_value`) and returns the original plaintext.

#### Scenario: Round-trip encryption and decryption
- **WHEN** encrypting a plaintext string and immediately decrypting the result with the same key
- **THEN** the decrypted output equals the original plaintext

#### Scenario: Decrypt with wrong key raises exception
- **WHEN** calling `decrypt_value(ciphertext, wrong_key)` where `wrong_key` is different from the encryption key
- **THEN** an `AuthenticationError` (or equivalent) is raised due to GCM tag verification failure

#### Scenario: Decrypt with tampered ciphertext raises exception
- **WHEN** calling `decrypt_value(tampered_ciphertext, key)` where the ciphertext has been modified
- **THEN** an exception is raised due to GCM authentication tag mismatch

### Requirement: Key derivation from ENCRYPTION_KEY environment variable
The system SHALL derive the AES-256 key from the `ENCRYPTION_KEY` environment variable, which MUST be a 64-character hex string (32 bytes).

#### Scenario: Valid ENCRYPTION_KEY produces 32-byte key
- **WHEN** reading a 64-character hex string from `ENCRYPTION_KEY`
- **THEN** the derived key is exactly 32 bytes

#### Scenario: Invalid ENCRYPTION_KEY length raises ValueError
- **WHEN** `ENCRYPTION_KEY` is not a 64-character hex string
- **THEN** a ValueError is raised during key derivation
