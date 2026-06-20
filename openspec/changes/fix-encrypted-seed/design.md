## Context

`entrada_padron.email` is declared as `Column(EncryptedString, nullable=True)` where `EncryptedString` is a SQLAlchemy `TypeDecorator` in `app/core/crypto.py`. It transparently encrypts/decrypts with AES-256-GCM on `process_bind_param` / `process_result_value`. However, `seed_dev.py` uses raw SQL (`text("INSERT INTO ...")`) which bypasses the TypeDecorator entirely, storing plaintext values. Any ORM read of `.email` triggers `base64.b64decode()` on the plaintext, raising `binascii.Error`.

The `frontend-profesor` change introduced endpoints that access `EntradaPadron.email` via the ORM, making this latent bug surface as 500 errors.

**Also at risk:** `usuario.dni`, `usuario.cuil`, `usuario.cbu`, `usuario.alias_cbu`, `comunicacion.destinatario` — all `EncryptedString` seeded via raw SQL. These are not yet exposed through ORM reads in production code, so they remain latent.

## Goals / Non-Goals

**Goals:**
- Fix `seed_dev.py` so new seeds produce correctly encrypted `email` values
- Provide a one-shot remediation script for existing plaintext `email` rows
- Add safeguard comments to discourage future raw SQL inserts on encrypted columns

**Non-Goals:**
- Fixing other `EncryptedString` columns that are not yet causing errors (latent, not urgent)
- Refactoring the raw SQL pattern in `seed_dev.py` to use ORM (too invasive, risk of breaking other seeds)
- Changing the encryption implementation itself

## Decisions

1. **Use `encrypt_value()` in seed rather than ORM insert**
   - **Why:** `seed_dev.py` has ~50 raw SQL inserts across many tables; rewriting to ORM for one column is high risk and low reward. `encrypt_value()` is already exported from `app.core.security` and produces the same ciphertext the TypeDecorator would. This is a minimal, targeted change.
   - **Alternative considered:** Rewrite the `entrada_padron` INSERT to use the SQLAlchemy ORM model. Rejected because it introduces inconsistency in the seed file — some inserts through ORM, others raw — and risks subtle ordering/relationship bugs.

2. **Remediation script as standalone Python script**
   - **Why:** A one-shot script lives outside the app lifecycle, runs only once per environment (dev/staging/prod), and has no reason to exist after execution. Placing it in `backend/scripts/` keeps it discoverable but clearly separate from application code.
   - **Design:** Script reads `entrada_padron.email` via raw SQL (bypassing the TypeDecorator to get the plaintext), calls `encrypt_value()` on each non-null value, and updates the row. Logs count of affected rows on completion.

3. **No Alembic migration**
   - **Why:** The column schema is unchanged — still `Text` with `EncryptedString`. Only the data content changes. A migration would be a no-op at the DDL level and introduce unnecessary version churn.

## Risks / Trade-offs

- **[Risk] Script runs on already-encrypted data** → Double encryption would corrupt data irreparably. **Mitigation:** Script checks if the value is valid base64 before attempting encryption. If it parses as valid base64 AND decryption succeeds, skip it (already encrypted). Only process values that fail `decrypt_value()`.
- **[Risk] Script misses some rows due to connection error** → **Mitigation:** Script wraps the update in a transaction. If any step fails, the entire batch is rolled back and the script exits with error message including the offending row ID.
- **[Risk] Other encrypted columns seeded via raw SQL cause the same bug later** → **Mitigation:** Add a `# WARNING: EncryptedString column — do NOT use raw plaintext` comment above each seed INSERT that targets an `EncryptedString` column. Document the risk in the codebase.

## Migration Plan

1. **Run remediation script** on any database that has already been seeded (dev, staging, prod if applicable)
2. **Apply seed_dev.py fix** so future seeds are clean
3. **Verify** by hitting the affected endpoints and confirming they return data instead of 500

**Rollback:** If remediation corrupts data, restore from backup and patch the seed only (data will be plaintext again but endpoints will still fail — same as current state).
