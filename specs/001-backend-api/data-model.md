# Data Model: Backend API

**Feature**: 001-backend-api
**Date**: 2026-01-13
**Source**: @specs/database/schema.md

---

## Entity Overview

```
┌─────────────────────┐         ┌─────────────────────┐
│        User         │         │        Task         │
├─────────────────────┤         ├─────────────────────┤
│ id: UUID (PK)       │────────▶│ id: UUID (PK)       │
│ email: str (UNIQUE) │   1:N   │ user_id: UUID (FK)  │
│ hashed_password: str│         │ title: str          │
│ created_at: datetime│         │ description: str?   │
└─────────────────────┘         │ completed: bool     │
                                │ created_at: datetime│
                                │ updated_at: datetime│
                                └─────────────────────┘
```

---

## User Entity

### SQLModel Definition

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(Text, unique=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Field Specifications

| Field | Type | Constraints | Validation |
|-------|------|-------------|------------|
| id | UUID | PK, auto-generated | Valid UUID v4 |
| email | string | UNIQUE, NOT NULL | Valid email format |
| hashed_password | string | NOT NULL | bcrypt hash |
| created_at | datetime | NOT NULL, auto | UTC timestamp |

### Business Rules

- Email must be unique across all users
- Password stored as bcrypt hash only
- No update of email after creation
- Cascade delete removes all user's tasks

---

## Task Entity

### SQLModel Definition

```python
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, ForeignKey

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    title: str = Field(sa_column=Column(Text, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Field Specifications

| Field | Type | Constraints | Validation |
|-------|------|-------------|------------|
| id | UUID | PK, auto-generated | Valid UUID v4 |
| user_id | UUID | FK → users.id, NOT NULL | Must exist in users |
| title | string | NOT NULL | 1-500 characters |
| description | string | NULLABLE | 0-5000 characters |
| completed | boolean | NOT NULL, default FALSE | true/false |
| created_at | datetime | NOT NULL, auto | UTC timestamp |
| updated_at | datetime | NOT NULL, auto-update | UTC timestamp |

### Business Rules

- user_id is immutable after creation
- title cannot be empty string
- updated_at auto-updates on any modification
- Tasks deleted when user deleted (CASCADE)

---

## State Transitions

### Task Completion States

```
         ┌──────────────────┐
         │                  │
         ▼                  │
    ┌─────────┐       ┌─────────┐
    │ Pending │◀─────▶│Complete │
    │completed│       │completed│
    │ = false │       │ = true  │
    └─────────┘       └─────────┘
```

- Tasks start as pending (completed = false)
- Toggle via PATCH with `{"completed": true/false}`
- No intermediate states

---

## Relationships

### User → Tasks (One-to-Many)

- One user has many tasks
- Each task belongs to exactly one user
- Foreign key: tasks.user_id → users.id
- Cascade delete: deleting user deletes all tasks

### Cardinality

| Relationship | Type | Enforcement |
|--------------|------|-------------|
| User → Tasks | 1:N | FK constraint |
| Task → User | N:1 | FK constraint |

---

## Indexes

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| idx_users_email | users | email | Login lookups |
| idx_tasks_user_id | tasks | user_id | List user's tasks |
| idx_tasks_user_completed | tasks | (user_id, completed) | Filter by status |
| idx_tasks_user_created | tasks | (user_id, created_at DESC) | Sort by date |

---

## Pydantic Schemas

### Request Schemas

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)

class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool

class TaskPatch(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: Optional[bool] = None
```

### Response Schemas

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: UserResponse
    token: str

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]

class ErrorResponse(BaseModel):
    error: dict  # {"code": str, "message": str}
```

---

## References

- @specs/database/schema.md - Source schema specification
- @specs/api/rest-endpoints.md - API contract for schemas
