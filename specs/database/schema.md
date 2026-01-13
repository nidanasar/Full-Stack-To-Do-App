# Database Specification — Phase II

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Status**: Ratified

## Purpose

Define the persistent data model for Phase II, ensuring reliable storage, strict user isolation, and compatibility with FastAPI + SQLModel.

This specification governs database schema, access patterns, and data integrity constraints.

---

## Database Engine

### Provider Configuration

| Property | Value |
|----------|-------|
| Provider | Neon |
| Type | Serverless PostgreSQL |
| Version | PostgreSQL 15+ |
| Connection | `DATABASE_URL` environment variable |
| Driver | asyncpg (async) |
| ORM | SQLModel |

### Connection String Format

```
postgresql+asyncpg://<user>:<password>@<host>/<database>?sslmode=require
```

### Connection Pool Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Pool Size | 5 | Serverless cold start optimization |
| Max Overflow | 10 | Handle burst traffic |
| Pool Timeout | 30s | Prevent hanging connections |
| Pool Recycle | 1800s | Neon connection limits |

---

## Design Principles

| Principle | Description | Enforcement |
|-----------|-------------|-------------|
| User Isolation | All data scoped by `user_id` | Application + FK constraints |
| No Shared Records | No global or shared task records | Schema design |
| Referential Integrity | Foreign keys enforced | Database constraints |
| CRUD Optimization | Schema optimized for CRUD, not analytics | Index strategy |
| Type Safety | All models type-safe via SQLModel | ORM layer |

---

## Schema Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Neon PostgreSQL                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐   │
│  │       users         │         │       tasks         │   │
│  ├─────────────────────┤         ├─────────────────────┤   │
│  │ id          UUID PK │◀────────│ user_id     UUID FK │   │
│  │ email       TEXT UQ │   1:N   │ id          UUID PK │   │
│  │ hashed_     TEXT    │         │ title       TEXT    │   │
│  │   password          │         │ description TEXT?   │   │
│  │ created_at  TIMESTAMPTZ       │ completed   BOOLEAN │   │
│  └─────────────────────┘         │ created_at  TIMESTAMPTZ │
│                                  │ updated_at  TIMESTAMPTZ │
│                                  └─────────────────────┘   │
│                                                              │
│  Constraints:                                                │
│  • users.email UNIQUE                                        │
│  • tasks.user_id REFERENCES users(id) ON DELETE CASCADE     │
│  • tasks.title NOT NULL                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tables

### Users Table

**Table Name**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| `email` | TEXT | UNIQUE, NOT NULL | User's email address |
| `hashed_password` | TEXT | NOT NULL | bcrypt-hashed password |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation timestamp |

**Notes**:
- Managed in coordination with Better Auth
- Passwords NEVER stored in plain text
- No `updated_at` on users (immutable except password changes)
- Email used as login identifier

**SQL DDL**:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

---

### Tasks Table

**Table Name**: `tasks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| `user_id` | UUID | FOREIGN KEY → users(id), NOT NULL | Owner reference |
| `title` | TEXT | NOT NULL | Task title (required) |
| `description` | TEXT | NULLABLE | Optional task details |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last modification timestamp |

**Notes**:
- `user_id` is immutable after creation (tasks cannot be transferred)
- `updated_at` auto-updates on any modification
- `title` cannot be empty string (application validation)

**SQL DDL**:

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Primary access pattern: user's tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Filtered queries: user's completed/pending tasks
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Sorting: user's tasks by creation date
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

**Trigger for updated_at**:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Indexes

### Index Strategy

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| `idx_users_email` | `email` | UNIQUE B-tree | Login lookups |
| `idx_tasks_user_id` | `user_id` | B-tree | List user's tasks |
| `idx_tasks_user_completed` | `(user_id, completed)` | B-tree | Filter by status |
| `idx_tasks_user_created` | `(user_id, created_at DESC)` | B-tree | Sort by date |

### Query Patterns Supported

| Query Pattern | Index Used | Expected Performance |
|---------------|------------|----------------------|
| `SELECT * FROM users WHERE email = ?` | idx_users_email | O(log n) |
| `SELECT * FROM tasks WHERE user_id = ?` | idx_tasks_user_id | O(log n + k) |
| `SELECT * FROM tasks WHERE user_id = ? AND completed = ?` | idx_tasks_user_completed | O(log n + k) |
| `SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC` | idx_tasks_user_created | O(log n + k) |

---

## Relationships

### Entity Relationship Diagram

```
┌─────────────┐                    ┌─────────────┐
│    User     │                    │    Task     │
├─────────────┤                    ├─────────────┤
│ id (PK)     │───────────────────▶│ user_id (FK)│
│ email       │        1:N         │ id (PK)     │
│ hashed_     │   "owns many"      │ title       │
│   password  │                    │ description │
│ created_at  │                    │ completed   │
└─────────────┘                    │ created_at  │
                                   │ updated_at  │
                                   └─────────────┘
```

### Relationship Rules

| Rule | Constraint | Behavior |
|------|------------|----------|
| One user → many tasks | Foreign key | Enforced by DB |
| Task must have user | NOT NULL FK | Insert rejected without user_id |
| Cascade delete | ON DELETE CASCADE | Deleting user deletes all tasks |
| No orphan tasks | FK constraint | Tasks cannot exist without user |

### Cascade Behavior

```sql
-- When a user is deleted:
DELETE FROM users WHERE id = 'user-uuid';
-- Automatically executes:
-- DELETE FROM tasks WHERE user_id = 'user-uuid';
```

---

## ORM Mapping (SQLModel)

### User Model

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text

class User(SQLModel, table=True):
    """User account model."""
    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique user identifier"
    )
    email: str = Field(
        sa_column=Column(Text, unique=True, nullable=False),
        description="User's email address"
    )
    hashed_password: str = Field(
        sa_column=Column(Text, nullable=False),
        description="bcrypt-hashed password"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp"
    )

    # Relationship (for ORM navigation, not DB)
    # tasks: list["Task"] = Relationship(back_populates="user")
```

### Task Model

```python
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, ForeignKey

class Task(SQLModel, table=True):
    """Task item model."""
    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier"
    )
    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False
        ),
        description="Owner user ID"
    )
    title: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Optional task details"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp"
    )

    # Relationship (for ORM navigation, not DB)
    # user: User = Relationship(back_populates="tasks")
```

### Pydantic Schemas (Request/Response)

```python
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# --- User Schemas ---

class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    """User data in responses."""
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Task Schemas ---

class TaskCreate(BaseModel):
    """Task creation request."""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)

class TaskUpdate(BaseModel):
    """Task update request (partial)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    """Task data in responses."""
    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """List of tasks response."""
    tasks: list[TaskResponse]
```

---

## Data Access Rules

### Query Patterns (MUST Follow)

| Rule | Implementation | Enforcement |
|------|----------------|-------------|
| All queries include user_id | WHERE user_id = ? | Code review |
| No cross-user joins | Application restriction | Code review |
| No raw SQL | Use SQLModel/SQLAlchemy | Linting |
| No SELECT * in production | Explicit column selection | Performance |

### Repository Pattern Example

```python
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class TaskRepository:
    """Data access layer for tasks."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: UUID, user_id: UUID) -> Task | None:
        """Get task by ID, scoped to user."""
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id  # ALWAYS include user_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        completed: bool | None = None
    ) -> list[Task]:
        """List all tasks for a user."""
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        statement = statement.order_by(Task.created_at.desc())

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, user_id: UUID, data: TaskCreate) -> Task:
        """Create a new task for user."""
        task = Task(
            user_id=user_id,  # ALWAYS set from JWT, never from request
            title=data.title,
            description=data.description
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(
        self,
        task_id: UUID,
        user_id: UUID,
        data: TaskUpdate
    ) -> Task | None:
        """Update task, scoped to user."""
        task = await self.get_by_id(task_id, user_id)
        if task is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete task, scoped to user."""
        task = await self.get_by_id(task_id, user_id)
        if task is None:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True
```

### Anti-Patterns (NEVER Do)

```python
# ❌ WRONG: No user_id filter
async def get_task_wrong(task_id: UUID) -> Task:
    return await session.get(Task, task_id)

# ❌ WRONG: user_id from request body
async def create_task_wrong(data: dict) -> Task:
    task = Task(user_id=data["user_id"], ...)  # NEVER from request

# ❌ WRONG: Cross-user join
statement = select(Task).join(User).where(User.email == "other@example.com")

# ❌ WRONG: Raw SQL
await session.execute(text("SELECT * FROM tasks WHERE ..."))
```

---

## Database Session Management

### Async Session Factory

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = "postgresql+asyncpg://..."

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for debugging
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """Dependency for FastAPI endpoints."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Transaction Pattern

```python
async def create_user_with_task(
    session: AsyncSession,
    user_data: UserCreate,
    task_data: TaskCreate
) -> tuple[User, Task]:
    """Atomic creation of user and initial task."""
    async with session.begin():
        user = User(email=user_data.email, hashed_password="...")
        session.add(user)
        await session.flush()  # Get user.id

        task = Task(user_id=user.id, title=task_data.title)
        session.add(task)

    # Commit happens automatically at end of `begin()` block
    return user, task
```

---

## Migration Strategy

### Approach

| Aspect | Strategy |
|--------|----------|
| Tool | SQLModel metadata + Alembic |
| Direction | Forward-only in Phase II |
| Destructive | Not allowed in Phase II |
| Schema changes | Require spec update first |

### Initial Migration

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', 'created_at'])

def downgrade() -> None:
    op.drop_table('tasks')
    op.drop_table('users')
```

---

## Phase II Constraints

### Not Implemented

| Feature | Status | Rationale |
|---------|--------|-----------|
| Soft deletes | Excluded | Complexity; hard delete sufficient |
| Audit logs | Excluded | Out of scope for MVP |
| Task history | Excluded | No version tracking needed |
| Full-text search | Excluded | Simple LIKE sufficient |
| Pagination | Optional | Small data sets expected |

### Data Limits

| Entity | Limit | Enforcement |
|--------|-------|-------------|
| Users | Unlimited | None |
| Tasks per user | 1000 | Application (soft limit) |
| Title length | 500 chars | Pydantic validation |
| Description length | 5000 chars | Pydantic validation |

---

## Functional Requirements

### Data Integrity Requirements

- **FR-DB-001**: System MUST store user passwords as bcrypt hashes only
- **FR-DB-002**: System MUST enforce unique email constraint at database level
- **FR-DB-003**: System MUST enforce foreign key constraint on tasks.user_id
- **FR-DB-004**: System MUST cascade delete tasks when user is deleted
- **FR-DB-005**: System MUST auto-generate UUIDs for all primary keys

### Data Access Requirements

- **FR-DB-006**: System MUST include user_id filter on all task queries
- **FR-DB-007**: System MUST NOT allow cross-user data access
- **FR-DB-008**: System MUST use async database sessions
- **FR-DB-009**: System MUST auto-update `updated_at` on task modifications

### Performance Requirements

- **FR-DB-010**: System MUST index user_id column on tasks table
- **FR-DB-011**: System MUST index email column on users table
- **FR-DB-012**: Database queries MUST complete in < 50ms (p95)

---

## Database Acceptance Criteria

### Data Persistence

- [ ] **AC-DB-001**: Data persists across application restarts
- [ ] **AC-DB-002**: Data persists across database connection recycling
- [ ] **AC-DB-003**: Transactions are ACID-compliant

### User Isolation

- [ ] **AC-DB-004**: Tasks are always scoped to user_id
- [ ] **AC-DB-005**: User A cannot query User B's tasks
- [ ] **AC-DB-006**: Deleting user cascades to delete all user's tasks

### Schema Integrity

- [ ] **AC-DB-007**: Schema matches SQLModel model definitions
- [ ] **AC-DB-008**: Duplicate emails rejected at database level
- [ ] **AC-DB-009**: Tasks without user_id rejected at database level
- [ ] **AC-DB-010**: Tasks with invalid user_id rejected (FK violation)

### Performance

- [ ] **AC-DB-011**: User's task list query uses index (no full scan)
- [ ] **AC-DB-012**: Login query uses index (no full scan)
- [ ] **AC-DB-013**: Connection pooling prevents connection exhaustion

### Type Safety

- [ ] **AC-DB-014**: All models are type-safe via SQLModel
- [ ] **AC-DB-015**: All UUIDs are valid v4 format
- [ ] **AC-DB-016**: All timestamps use timezone-aware format (TIMESTAMPTZ)

---

## References

- @specs/architecture.md - System architecture (Database Architecture section)
- @specs/features/authentication.md - Authentication specification
- @specs/api/rest-endpoints.md - API contract
- @.specify/memory/constitution.md - Project constitution (Section IV: Cloud-Native Foundation)
