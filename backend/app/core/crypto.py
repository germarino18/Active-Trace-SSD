"""SQLAlchemy type that transparently encrypts/decrypts column values.

`EncryptedString` wraps the AES-256-GCM primitives already implemented in
`app.core.security` (`encrypt_value`/`decrypt_value`/`get_encryption_key`).
It does NOT implement any cryptography itself — it only adapts those
primitives to SQLAlchemy's `TypeDecorator` hooks so PII columns (dni, cuil,
cbu, alias_cbu) are ciphertext at rest and plaintext via the ORM (Regla
Dura #12).

The underlying column type is `String`/`Text`, storing base64(nonce +
ciphertext) as produced by `encrypt_value`.
"""

from sqlalchemy.types import String, TypeDecorator

from app.core.security import decrypt_value, encrypt_value, get_encryption_key


class EncryptedString(TypeDecorator):
    """Transparent AES-256-GCM encryption for string columns.

    - `process_bind_param` (write): encrypts the plaintext before it is
      sent to the database.
    - `process_result_value` (read): decrypts the stored ciphertext back
      into plaintext for the ORM attribute.

    `None` is passed through unchanged (nullable columns stay NULL).
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        key = get_encryption_key()
        return encrypt_value(value, key)

    def process_result_value(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        key = get_encryption_key()
        return decrypt_value(value, key)
