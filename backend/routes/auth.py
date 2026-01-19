"""Authentication routes for user registration and login."""

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from auth import create_access_token, password_hash, password_verify
from dependencies import DbSession
from exceptions import ConflictException, UnauthorizedException
from models import User
from schemas import AuthResponse, LoginRequest, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
async def register(data: UserCreate, db: DbSession) -> AuthResponse:
    """Register a new user account.

    Creates a new user with hashed password and returns JWT token.

    Args:
        data: User registration data (email, password).
        db: Database session.

    Returns:
        AuthResponse with user data and JWT token.

    Raises:
        ConflictException: If email is already registered.
    """
    # Hash password before storage
    hashed = password_hash(data.password)

    # Create user
    user = User(
        email=data.email,
        hashed_password=hashed,
    )

    db.add(user)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ConflictException("Email already registered")

    # Generate JWT token
    token = create_access_token(user.id)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
    },
)
async def login(data: LoginRequest, db: DbSession) -> AuthResponse:
    """Authenticate user and return JWT token.

    Verifies email and password, returns JWT on success.

    Args:
        data: Login credentials (email, password).
        db: Database session.

    Returns:
        AuthResponse with user data and JWT token.

    Raises:
        UnauthorizedException: If credentials are invalid.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Generic error message to prevent user enumeration
    if user is None:
        raise UnauthorizedException("Invalid credentials")

    # Verify password
    if not password_verify(data.password, user.hashed_password):
        raise UnauthorizedException("Invalid credentials")

    # Generate JWT token
    token = create_access_token(user.id)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )
