"""FastAPI dependencies for database sessions and authentication."""

from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from auth import verify_token
from database import async_session
from exceptions import UnauthorizedException


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session.

    Yields:
        AsyncSession for database operations.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> UUID:
    """Extract and validate user ID from JWT in Authorization header.

    Args:
        authorization: Authorization header value (Bearer <token>).

    Returns:
        UUID of the authenticated user.

    Raises:
        UnauthorizedException: If token is missing, invalid, or expired.
    """
    if not authorization:
        raise UnauthorizedException("Missing authorization header")

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid authorization header format")

    token = parts[1]
    user_id = verify_token(token)

    if user_id is None:
        raise UnauthorizedException("Invalid or expired token")

    return user_id


# Type aliases for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[UUID, Depends(get_current_user)]
