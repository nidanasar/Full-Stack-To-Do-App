"""Authentication utilities for password hashing and JWT handling."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Bcrypt hashed password string.
    """
    return pwd_context.hash(password)


def password_verify(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Bcrypt hashed password to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID) -> str:
    """Create a JWT access token for a user.

    Args:
        user_id: UUID of the user to create token for.

    Returns:
        Encoded JWT string with sub, exp, and iat claims.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_expiration_days)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(token: str) -> UUID | None:
    """Verify a JWT token and extract the user ID.

    Args:
        token: JWT token string to verify.

    Returns:
        User UUID if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        return UUID(user_id_str)
    except (JWTError, ValueError):
        return None
