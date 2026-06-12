import time

from app.services.auth.rate_limiter import RateLimiter


def test_under_limit_passes():
    limiter = RateLimiter(max_attempts=5, window_seconds=60)
    for _ in range(4):
        assert limiter.check("1.2.3.4", "a@x.com") is True


def test_over_limit_blocks():
    limiter = RateLimiter(max_attempts=5, window_seconds=60)
    for _ in range(5):
        limiter.check("1.2.3.4", "a@x.com")
    assert limiter.check("1.2.3.4", "a@x.com") is False


def test_different_email_same_ip_independent():
    limiter = RateLimiter(max_attempts=5, window_seconds=60)
    for _ in range(5):
        limiter.check("1.2.3.4", "a@x.com")
    assert limiter.check("1.2.3.4", "b@x.com") is True


def test_window_resets():
    limiter = RateLimiter(max_attempts=5, window_seconds=1)
    for _ in range(5):
        limiter.check("1.2.3.4", "a@x.com")
    assert limiter.check("1.2.3.4", "a@x.com") is False
    time.sleep(1.1)
    assert limiter.check("1.2.3.4", "a@x.com") is True


def test_retry_after():
    limiter = RateLimiter(max_attempts=2, window_seconds=60)
    limiter.check("1.2.3.4", "a@x.com")
    limiter.check("1.2.3.4", "a@x.com")
    retry = limiter.get_retry_after("1.2.3.4", "a@x.com")
    assert retry > 0


def test_reset_clears():
    limiter = RateLimiter(max_attempts=5, window_seconds=60)
    for _ in range(5):
        limiter.check("1.2.3.4", "a@x.com")
    limiter.reset("1.2.3.4", "a@x.com")
    assert limiter.check("1.2.3.4", "a@x.com") is True
