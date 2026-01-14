"""Pytest fixtures for async testing."""

import asyncio
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from auth import create_access_token, password_hash
from dependencies import get_db
from main import app
from models import Task, User

# Test database URL (SQLite in-memory for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# Test session factory
test_async_session = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with test_async_session() as session:
        yield session

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client with test database."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=password_hash("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user: User) -> str:
    """Create JWT token for test user."""
    return create_access_token(test_user.id)


@pytest_asyncio.fixture
async def auth_headers(test_user_token: str) -> dict:
    """Create authorization headers for test user."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> User:
    """Create another test user for isolation tests."""
    user = User(
        email="other@example.com",
        hashed_password=password_hash("password456"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user_token(other_user: User) -> str:
    """Create JWT token for other user."""
    return create_access_token(other_user.id)


@pytest_asyncio.fixture
async def other_auth_headers(other_user_token: str) -> dict:
    """Create authorization headers for other user."""
    return {"Authorization": f"Bearer {other_user_token}"}


@pytest_asyncio.fixture
async def test_task(db_session: AsyncSession, test_user: User) -> Task:
    """Create a test task for the test user."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test description",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
