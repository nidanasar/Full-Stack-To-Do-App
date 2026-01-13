---
description: Configure async database sessions with SQLModel and FastAPI dependency injection.
---

# Skill: Async Database Session

## Purpose
Manage database connections with async SQLModel sessions, connection pooling, and proper transaction handling for FastAPI.

## Stack Context
- **Backend**: FastAPI + SQLModel
- **Database**: Neon PostgreSQL (serverless)
- **Driver**: asyncpg (async PostgreSQL driver)

## Dependencies

```toml
# pyproject.toml
[project.dependencies]
sqlmodel = "^0.0.22"
asyncpg = "^0.29.0"
sqlalchemy = { extras = ["asyncio"], version = "^2.0" }
```

## Implementation

### Database Configuration
```python
# db/config.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Neon PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# Convert to async URL if needed
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in development
    pool_size=5,  # Neon serverless: keep pool small
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
```

### Session Dependency
```python
# db/session.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .config import async_session

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Database Initialization
```python
# db/init.py
from sqlmodel import SQLModel
from .config import engine

async def init_db():
    """Create all tables. Call once at startup."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db():
    """Close all connections. Call at shutdown."""
    await engine.dispose()
```

### FastAPI Lifespan Integration
```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.init import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(lifespan=lifespan)
```

### Using in Routes
```python
# routes/tasks.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db.session import get_session
from models.task import Task

router = APIRouter()

@router.get("/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)  # Injected session
):
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()

@router.post("/tasks", status_code=201)
async def create_task(
    task: TaskCreate,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    db_task = Task(**task.dict(), user_id=user_id)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)  # Get generated fields (id, timestamps)
    return db_task
```

## Transaction Patterns

### Automatic Commit/Rollback
```python
# get_session() handles this automatically:
# - Commits on success
# - Rolls back on exception
```

### Manual Transaction Control
```python
@router.post("/batch")
async def batch_operation(
    items: list[TaskCreate],
    session: AsyncSession = Depends(get_session)
):
    try:
        for item in items:
            task = Task(**item.dict())
            session.add(task)
        await session.commit()  # Commit all at once
    except Exception:
        await session.rollback()  # Rollback entire batch
        raise
```

### Nested Operations
```python
async def create_user_with_tasks(
    session: AsyncSession,
    user_data: UserCreate,
    initial_tasks: list[TaskCreate]
):
    """Create user and initial tasks in single transaction."""
    user = User(**user_data.dict())
    session.add(user)
    await session.flush()  # Get user.id without committing

    for task_data in initial_tasks:
        task = Task(**task_data.dict(), user_id=user.id)
        session.add(task)

    # Caller's session will commit everything together
    return user
```

## Neon PostgreSQL Specifics

```python
# For Neon serverless, use connection pooling settings:
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,  # Keep small for serverless
    max_overflow=10,
    pool_pre_ping=True,  # Handle cold starts
    pool_recycle=300,  # Recycle stale connections
    connect_args={
        "server_settings": {
            "application_name": "hackathon-todo"
        }
    }
)
```

## Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

## Project Structure

```
backend/
├── db/
│   ├── __init__.py
│   ├── config.py      # Engine and session factory
│   ├── session.py     # get_session dependency
│   └── init.py        # init_db, close_db
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── task.py
├── routes/
│   └── tasks.py
└── main.py            # FastAPI app with lifespan
```

## Checklist
- [ ] DATABASE_URL uses `postgresql+asyncpg://` prefix
- [ ] Connection pooling configured for Neon serverless
- [ ] `get_session` dependency handles commit/rollback
- [ ] Lifespan initializes DB on startup, disposes on shutdown
- [ ] All routes use `Depends(get_session)`
- [ ] `await session.refresh()` after inserts to get generated fields
