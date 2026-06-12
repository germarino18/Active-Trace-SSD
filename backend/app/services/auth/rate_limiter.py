import time
from threading import Lock


class RateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = {}
        self._lock = Lock()

    def _key(self, ip: str, email: str) -> str:
        return f"{ip}:{email}"

    def check(self, ip: str, email: str) -> bool:
        key = self._key(ip, email)
        now = time.time()
        with self._lock:
            timestamps = self._attempts.get(key, [])
            cutoff = now - self._window_seconds
            timestamps = [t for t in timestamps if t > cutoff]
            if len(timestamps) >= self._max_attempts:
                return False
            timestamps.append(now)
            self._attempts[key] = timestamps
        return True

    def get_retry_after(self, ip: str, email: str) -> int:
        key = self._key(ip, email)
        now = time.time()
        with self._lock:
            timestamps = self._attempts.get(key, [])
            if not timestamps:
                return 0
            cutoff = now - self._window_seconds
            timestamps = [t for t in timestamps if t > cutoff]
            if not timestamps:
                return 0
            oldest = timestamps[0]
            retry_after = int(self._window_seconds - (now - oldest))
            return max(1, retry_after)

    def reset(self, ip: str, email: str) -> None:
        key = self._key(ip, email)
        with self._lock:
            self._attempts.pop(key, None)
