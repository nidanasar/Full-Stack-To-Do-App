---
description: Apply user-scoped CRUD pattern ensuring all operations filter by authenticated user_id from JWT.
---

# Skill: User-Scoped CRUD

## Purpose
Provide a reusable pattern for performing CRUD operations while enforcing strict user ownership. All database queries MUST filter by user_id extracted from JWT.

## Guarantees
- `user_id` ALWAYS comes from JWT (never from request body)
- All queries ALWAYS filter by `user_id`
- No cross-user data access is possible
- Ownership verified before any mutation

## Stack Context
- **Backend**: FastAPI + SQLModel + Neon Postgres
- **Auth**: Better Auth (frontend) + JWT validation (backend)
- **ORM**: SQLModel with async support

## Pattern Implementation

### 1. Model Definition (SQLModel)
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)  # ALWAYS required
    title: str
    description: str | None = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Dependency for User Context
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Extract and validate user_id from JWT. NEVER trust client input."""
    token = credentials.credentials
    payload = verify_jwt(token)  # Raises 401 if invalid
    return UUID(payload["sub"])
```

### 3. CRUD Operations (Always User-Scoped)

#### Create
```python
@router.post("/tasks", status_code=201)
async def create_task(
    task: TaskCreate,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    db_task = Task(**task.dict(), user_id=user_id)  # user_id from JWT
    session.add(db_task)
    await session.commit()
    return db_task
```

#### List (User's Tasks Only)
```python
@router.get("/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    statement = select(Task).where(Task.user_id == user_id)
    results = await session.execute(statement)
    return results.scalars().all()
```

#### Get Single (With Ownership Check)
```python
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # CRITICAL: ownership filter
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

#### Update (With Ownership Check)
```python
@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow()
    await session.commit()
    return task
```

#### Delete (With Ownership Check)
```python
@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()
```

## Applies To
- Task creation, listing, update, deletion
- Any user-owned resource in Phase II+
- Future: Chatbot actions, event handlers

## Failure Modes
| Scenario | Response |
|----------|----------|
| Resource not owned by user | 404 Not Found |
| Invalid/missing JWT | 401 Unauthorized |
| Malformed user_id in JWT | 403 Forbidden |

## Security Rules
1. NEVER accept `user_id` from request body or query params
2. ALWAYS use `Depends(get_current_user_id)` for user context
3. ALWAYS include `user_id` filter in WHERE clauses
4. Return 404 (not 403) for unowned resources to prevent enumeration

## Checklist Before Implementation
- [ ] Model has `user_id` foreign key with index
- [ ] Endpoint uses `Depends(get_current_user_id)`
- [ ] Query includes `where(Model.user_id == user_id)`
- [ ] Tests verify cross-user access is blocked
