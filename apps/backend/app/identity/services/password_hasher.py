"""Password hashing service implementation using passlib bcrypt.

Supports hash calculations, verification comparisons, and rounds config updates.
"""

from passlib.context import CryptContext
import bcrypt

# Monkeypatch bcrypt.hashpw to truncate passwords longer than 72 bytes
# bcrypt naturally ignores bytes past 72, but newer python-bcrypt packages raise ValueError.
_original_hashpw = bcrypt.hashpw
def patched_hashpw(password: bytes, salt: bytes) -> bytes:
    if len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)
bcrypt.hashpw = patched_hashpw

from app.identity.services.interfaces import IPasswordHasher


class PasswordHasher(IPasswordHasher):
    """Bcrypt password hashing service implementing IPasswordHasher."""

    def __init__(self, work_factor: int = 12) -> None:
        """Initializes the PasswordHasher.

        Args:
            work_factor: Configured bcrypt rounds (work factor).
        """
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=work_factor,
        )

    def hash(self, password: str) -> str:
        """Computes a secure bcrypt hash of the plain-text password.

        Args:
            password: The plain-text password.

        Returns:
            The secure hashed string.
        """
        return self.pwd_context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        """Verifies plain-text password against bcrypt representation.

        Args:
            password: Plain-text password.
            hashed_password: Hashed password.

        Returns:
            True if matched; False otherwise.
        """
        return self.pwd_context.verify(password, hashed_password)

    def needs_rehash(self, hashed_password: str) -> bool:
        """Determines if the hash rounds configuration needs migration update.

        Args:
            hashed_password: Hashed password string.

        Returns:
            True if work factor rounds differ; False otherwise.
        """
        return self.pwd_context.needs_update(hashed_password)
