---
description: Apply owner validation pattern to ensure users can only access their own resources.
---

# Skill: Owner Validation

## Purpose
Ensure users can only access, modify, or delete resources they own. Prevents cross-user data access attacks.

## Stack Context
- **Backend**: FastAPI + SQLModel
- **Auth**: JWT with user_id in `sub` claim
- **Pattern**: Query-level filtering + explicit ownership checks

## Core Principle

**NEVER trust client input for ownership. ALWAYS derive user_id from JWT.**

```
❌ BAD:  request.body.user_id  → Client can spoof
❌ BAD:  request.query.user_id → Client can spoof
✅ GOOD: jwt.sub (user_id)     → Server-verified
```

## Implementation Patterns

### Pattern 1: Query-Level Filtering (Preferred)
Include `user_id` in the WHERE clause. Resource not found = 404.

```python
async def get_task(task_id: UUID, user_id: UUID) -> Task | None:
    """Fetch task only if owned by user."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Ownership filter
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

@router.get("/tasks/{task_id}")
async def get_task_endpoint(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    task = await get_task(task_id, user_id)
    if not task:
        raise HTTPException(404, "Task not found")  # Don't reveal if exists
    return task
```

### Pattern 2: Fetch-Then-Verify (When Needed)
Use when you need to check ownership separately (e.g., for different error messages in internal tools).

```python
async def get_task_with_ownership_check(
    task_id: UUID,
    user_id: UUID
) -> Task:
    """Fetch task and verify ownership."""
    task = await session.get(Task, task_id)

    if not task:
        raise NotFoundError("Task")

    if task.user_id != user_id:
        # Return 404 to prevent enumeration
        raise NotFoundError("Task")

    return task
```

## Route Examples

### Update with Owner Validation
```python
@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: UUID,
    update: TaskUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    # Query includes ownership filter
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    # Apply updates
    for key, value in update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    await session.commit()
    return task
```

### Delete with Owner Validation
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
        raise HTTPException(404, "Task not found")

    await session.delete(task)
    await session.commit()
    return Response(status_code=204)
```

### List (Always Scoped)
```python
@router.get("/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    status: TaskStatus = TaskStatus.all
):
    statement = select(Task).where(Task.user_id == user_id)

    if status == TaskStatus.active:
        statement = statement.where(Task.completed == False)
    elif status == TaskStatus.completed:
        statement = statement.where(Task.completed == True)

    result = await session.execute(statement)
    return result.scalars().all()
```

## Reusable Dependency

```python
from fastapi import Depends, HTTPException
from uuid import UUID

async def get_owned_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> Task:
    """Dependency that fetches task with ownership validation."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    return task

# Usage - cleaner routes
@router.patch("/tasks/{task_id}")
async def update_task(
    update: TaskUpdate,
    task: Task = Depends(get_owned_task)  # Ownership already validated
):
    for key, value in update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    await session.commit()
    return task
```

## Security Rules

| Rule | Reason |
|------|--------|
| Always use `Depends(get_current_user_id)` | JWT is server-verified |
| Include `user_id` in WHERE clause | Prevents cross-user access |
| Return 404 for unowned resources | Prevents resource enumeration |
| Never accept user_id from request body | Client can spoof |
| Log access attempts | Audit trail for security |

## Common Mistakes

```python
# ❌ WRONG: user_id from request body
@router.patch("/tasks/{task_id}")
async def update_task(task_id: UUID, body: TaskUpdateWithUser):
    task = await get_task(task_id)
    if task.user_id != body.user_id:  # Attacker controls body.user_id!
        raise HTTPException(403)

# ✅ CORRECT: user_id from JWT
@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: UUID,
    body: TaskUpdate,
    user_id: UUID = Depends(get_current_user_id)  # From JWT
):
    task = await get_task(task_id, user_id)  # Filtered by owner
```

## Testing Owner Validation

```python
# tests/test_owner_validation.py
import pytest

async def test_cannot_access_other_users_task(client, user_a_token, user_b_task):
    """User A cannot access User B's task."""
    response = await client.get(
        f"/tasks/{user_b_task.id}",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert response.status_code == 404  # Not 403!

async def test_cannot_update_other_users_task(client, user_a_token, user_b_task):
    """User A cannot update User B's task."""
    response = await client.patch(
        f"/tasks/{user_b_task.id}",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"title": "Hacked!"}
    )
    assert response.status_code == 404

async def test_cannot_delete_other_users_task(client, user_a_token, user_b_task):
    """User A cannot delete User B's task."""
    response = await client.delete(
        f"/tasks/{user_b_task.id}",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert response.status_code == 404
```

## Checklist
- [ ] All resource endpoints use `Depends(get_current_user_id)`
- [ ] All queries include `where(Model.user_id == user_id)`
- [ ] Unowned resources return 404 (not 403)
- [ ] No endpoint accepts user_id from request body/query
- [ ] Tests verify cross-user access is blocked
- [ ] Audit logging for sensitive operations
