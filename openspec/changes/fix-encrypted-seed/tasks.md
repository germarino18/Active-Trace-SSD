## 1. Fix seed to encrypt email before INSERT

- [x] 1.1 Read `backend/seed_dev.py` and locate the `entrada_padron` raw SQL INSERT block
- [x] 1.2 Import `encrypt_value` from `app.core.security` at the top of seed_dev.py
- [x] 1.3 Encrypt the `email` variable before it is interpolated into the raw SQL INSERT
- [x] 1.4 Add `# WARNING: EncryptedString column` comment above the INSERT to warn future developers

## 2. Create remediation script for existing plaintext emails

- [x] 2.1 Create `backend/scripts/remediate_encrypted_entrada_padron.py` with:
  - Raw SQL read of `entrada_padron.email` (bypass TypeDecorator)
  - For each non-null value: check if valid base64 + decrypts successfully → skip; otherwise → encrypt with `encrypt_value()` and UPDATE
  - Transactional: rollback on any error
  - `--dry-run` flag for preview without writes
  - Exit codes: 0 (success), 1 (error)

## 3. Verify fix by reading entrada_padron through the ORM

- [ ] 3.1 Run the remediation script against a seeded database
- [ ] 3.2 Start the application and verify `EntradaPadron.email` loads without `binascii.Error`
- [ ] 3.3 Confirm `EntradaPadron.email` returns the original plaintext (decrypted) value

## 4. Smoke test affected endpoints

- [ ] 4.1 `GET /api/v1/profesor/dictados/{id}/padron` — returns 200, includes email field
- [ ] 4.2 `POST /api/v1/profesor/dictados/{id}/comunicado-atrasados` — returns 200
- [ ] 4.3 `POST /api/v1/profesor/dictados/{id}/comunicado-atrasado-null` — returns 200

## 5. Add safeguard documentation

- [x] 5.1 Add code comment near `EncryptedString` column definitions in `app/models/entrada_padron.py`: `# WARNING: raw SQL INSERT bypasses this TypeDecorator — always encrypt manually`
- [x] 5.2 Audit `seed_dev.py` for other `EncryptedString` columns (`usuario.dni/cuil/cbu/alias_cbu`, `comunicacion.destinatario`) and add warning comments
