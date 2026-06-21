## Why

`seed_dev.py` inserts `entrada_padron.email` as plaintext via raw SQL, but the column uses `EncryptedString` (AES-256-GCM TypeDecorator). The TypeDecorator only activates through the ORM, so raw SQL bypasses encryption. Any endpoint reading `email` through the ORM fails with `binascii.Error: Invalid base64-encoded string`.

This didn't surface until the `frontend-profesor` change added endpoints that access `EntradaPadron.email`:
- `GET /api/v1/profesor/dictados/{id}/padron`
- `POST /api/v1/profesor/dictados/{id}/comunicado-atrasados`
- `POST /api/v1/profesor/dictados/{id}/comunicado-atrasado-null`

Same risk exists for `usuario.dni`, `usuario.cuil`, `usuario.cbu`, `usuario.alias_cbu` and `comunicacion.destinatario` — all `EncryptedString` seeded via raw SQL.

## What Changes

- Fix `backend/seed_dev.py` to encrypt `email` values before raw SQL INSERT using `encrypt_value()` from `app.core.security`
- Create a one-shot remediation script that re-encrypts existing plaintext emails in `entrada_padron`
- Add safeguard comment to discourage raw SQL inserts on encrypted columns
- (Future-proofing) Flag other `EncryptedString` columns seeded via raw SQL for the same treatment when they become reachable

## Capabilities

### New Capabilities
- `remediate-encrypted-data`: one-shot script to detect and re-encrypt plaintext values in `EncryptedString` columns, with logging of affected rows

### Modified Capabilities
(none — bugfix only, no spec-level behavior changes)

## Impact

**Affected code:**
- `backend/seed_dev.py` — raw SQL INSERTs on `entrada_padron` table
- `backend/app/core/security.py` — `encrypt_value()` already exists, no changes needed
- New file: `backend/scripts/remediate_encrypted_entrada_padron.py`

**Affected data:**
- All `entrada_padron.email` values currently in plaintext in the database must be re-encrypted

**Non-breaking:**
- Fix is transparent: reads go through the ORM and work identically on encrypted values
- Existing encrypted values (if any) are unaffected
