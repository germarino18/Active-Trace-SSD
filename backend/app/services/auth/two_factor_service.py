import base64
import os

import pyotp

from app.core.security import decrypt_value, encrypt_value, get_encryption_key


class TwoFactorService:
    def __init__(self, issuer: str = "activia-trace"):
        self._issuer = issuer

    def generate_secret(self, email: str) -> dict:
        secret = pyotp.random_base32()
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=self._issuer)
        return {
            "secret": secret,
            "qr_uri": uri,
        }

    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    @staticmethod
    def encrypt_secret(secret: str) -> str:
        key = get_encryption_key()
        return encrypt_value(secret, key)

    @staticmethod
    def decrypt_secret(encrypted: str) -> str:
        key = get_encryption_key()
        return decrypt_value(encrypted, key)
