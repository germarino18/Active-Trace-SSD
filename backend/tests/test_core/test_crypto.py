"""Tests for app.core.crypto.EncryptedString (C-07 task group 1).

EncryptedString is a SQLAlchemy TypeDecorator that wraps the existing
AES-256-GCM primitives in app.core.security (encrypt_value/decrypt_value/
get_encryption_key). It encrypts on bind (write) and decrypts on result
(read), storing base64(nonce+ciphertext) as the underlying String/Text.
"""

import os

import pytest

from app.core.crypto import EncryptedString
from app.core.security import decrypt_value, get_encryption_key

_TEST_KEY_HEX = "a" * 64


@pytest.fixture(autouse=True)
def _encryption_key_env():
    old = os.environ.get("ENCRYPTION_KEY")
    os.environ["ENCRYPTION_KEY"] = _TEST_KEY_HEX
    yield
    if old is None:
        os.environ.pop("ENCRYPTION_KEY", None)
    else:
        os.environ["ENCRYPTION_KEY"] = old


def test_bind_then_result_round_trips_plaintext():
    """1.1 — bind→result round-trips a plaintext value."""
    coltype = EncryptedString()
    plaintext = "12345678"

    bound = coltype.process_bind_param(plaintext, dialect=None)
    result = coltype.process_result_value(bound, dialect=None)

    assert result == plaintext


def test_bound_value_is_not_plaintext():
    """1.2 — the bound param (DB-layer value) is ciphertext, not plaintext."""
    coltype = EncryptedString()
    plaintext = "20-12345678-9"

    bound = coltype.process_bind_param(plaintext, dialect=None)

    assert bound != plaintext
    assert plaintext not in bound

    # And it really is the AES-256-GCM ciphertext format used by security.py:
    # decrypting it directly with the configured key returns the plaintext.
    key = get_encryption_key()
    assert decrypt_value(bound, key) == plaintext


def test_none_value_round_trips_as_none():
    """1.4 — None is handled without attempting to encrypt/decrypt."""
    coltype = EncryptedString()

    assert coltype.process_bind_param(None, dialect=None) is None
    assert coltype.process_result_value(None, dialect=None) is None


def test_empty_string_round_trips():
    """1.4 — empty string handled (treated distinctly from None)."""
    coltype = EncryptedString()

    bound = coltype.process_bind_param("", dialect=None)
    result = coltype.process_result_value(bound, dialect=None)

    assert result == ""


def test_same_plaintext_encrypted_twice_yields_different_ciphertexts_both_decryptable():
    """1.4 — random nonce per value: two encryptions differ but both decrypt correctly."""
    coltype = EncryptedString()
    plaintext = "ARS-000123456789"

    bound_1 = coltype.process_bind_param(plaintext, dialect=None)
    bound_2 = coltype.process_bind_param(plaintext, dialect=None)

    assert bound_1 != bound_2
    assert coltype.process_result_value(bound_1, dialect=None) == plaintext
    assert coltype.process_result_value(bound_2, dialect=None) == plaintext
