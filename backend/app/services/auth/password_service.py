from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher(
    memory_cost=19456,
    time_cost=2,
    parallelism=1,
)


class PasswordService:
    @staticmethod
    def hash_password(plain: str) -> str:
        return _ph.hash(plain)

    @staticmethod
    def verify_password(plain: str, password_hash: str) -> bool:
        try:
            return _ph.verify(password_hash, plain)
        except VerifyMismatchError:
            return False
