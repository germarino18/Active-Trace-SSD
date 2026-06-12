import pytest

from app.core.security import decrypt_value, encrypt_value, get_encryption_key


@pytest.fixture
def valid_key() -> bytes:
    return get_encryption_key("a" * 64)


def test_encrypt_produces_non_empty_string(valid_key: bytes):
    result = encrypt_value("sensitive data", valid_key)
    assert isinstance(result, str)
    assert len(result) > 0


def test_same_plaintext_different_ciphertexts(valid_key: bytes):
    c1 = encrypt_value("same data", valid_key)
    c2 = encrypt_value("same data", valid_key)
    assert c1 != c2


def test_round_trip(valid_key: bytes):
    original = "hello world 123"
    encrypted = encrypt_value(original, valid_key)
    decrypted = decrypt_value(encrypted, valid_key)
    assert decrypted == original


def test_decrypt_with_wrong_key_raises_exception(valid_key: bytes):
    wrong_key = get_encryption_key("b" * 64)
    encrypted = encrypt_value("secret", valid_key)
    with pytest.raises(Exception):
        decrypt_value(encrypted, wrong_key)


def test_tampered_ciphertext_raises_exception(valid_key: bytes):
    encrypted = encrypt_value("secret", valid_key)
    tampered = encrypted[:-1] + ("0" if encrypted[-1] != "0" else "1")
    with pytest.raises(Exception):
        decrypt_value(tampered, valid_key)


def test_invalid_key_length_raises_value_error():
    with pytest.raises(ValueError):
        get_encryption_key("too-short")


def test_non_hex_key_raises_value_error():
    with pytest.raises(ValueError):
        get_encryption_key("z" * 64)
