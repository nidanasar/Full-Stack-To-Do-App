"""Database configuration with async SQLAlchemy engine and session factory."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from config import settings

# Convert postgres:// to postgresql+asyncpg:// for async driver
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remove sslmode and channel_binding from URL (asyncpg handles SSL differently)
parsed = urlparse(database_url)
query_params = parse_qs(parsed.query)
query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)
clean_query = urlencode(query_params, doseq=True)
database_url = urlunparse(parsed._replace(query=clean_query))

# Create async engine with connection pool settings optimized for serverless
engine = create_async_engine(
    database_url,
    echo=settings.environment == "development",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
