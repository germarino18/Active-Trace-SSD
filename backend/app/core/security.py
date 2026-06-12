import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_encryption_key(encryption_key_raw: str | None = None) -> bytes:
    if encryption_key_raw is None:
        encryption_key_raw = os.environ.get("ENCRYPTION_KEY", "")
    try:
        key = bytes.fromhex(encryption_key_raw)
    except ValueError as exc:
        raise ValueError("ENCRYPTION_KEY must be a valid 64-character hex string") from exc
    if len(key) != 32:
        raise ValueError(
            f"ENCRYPTION_KEY decoded to {len(key)} bytes, expected 32 bytes (64 hex chars)"
        )
    return key


def encrypt_value(plaintext: str, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_value(ciphertext_b64: str, key: bytes) -> str:
    raw = base64.b64decode(ciphertext_b64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
