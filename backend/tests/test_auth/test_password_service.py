from app.services.auth.password_service import PasswordService


def test_hash_password_returns_argon2id_string():
    result = PasswordService.hash_password("SecureP@ss1")
    assert result.startswith("$argon2id$")
    assert isinstance(result, str)


def test_verify_correct_password():
    hashed = PasswordService.hash_password("SecureP@ss1")
    assert PasswordService.verify_password("SecureP@ss1", hashed) is True


def test_verify_incorrect_password():
    hashed = PasswordService.hash_password("SecureP@ss1")
    assert PasswordService.verify_password("WrongP@ss1", hashed) is False
