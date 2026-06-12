import pyotp

from app.services.auth.two_factor_service import TwoFactorService


def test_generate_secret_returns_base32():
    svc = TwoFactorService()
    result = svc.generate_secret("user@example.com")
    assert "secret" in result
    assert "qr_uri" in result
    secret = result["secret"]
    import base64
    import string
    valid_chars = set(string.ascii_uppercase + string.digits + "=")
    assert all(c in valid_chars for c in secret)


def test_qr_uri_format():
    svc = TwoFactorService(issuer="activia-trace")
    result = svc.generate_secret("user@example.com")
    assert result["qr_uri"].startswith("otpauth://totp/")
    assert "activia-trace" in result["qr_uri"]
    assert "user%40example.com" in result["qr_uri"] or "user@example.com" in result["qr_uri"]


def test_verify_correct_code():
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    code = totp.now()
    assert TwoFactorService.verify_code(secret, code) is True


def test_verify_incorrect_code():
    secret = pyotp.random_base32()
    assert TwoFactorService.verify_code(secret, "000000") is False


def test_verify_code_from_adjacent_window():
    import time
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    code_now = totp.now()
    time.sleep(35)
    assert TwoFactorService.verify_code(secret, code_now) is True
