---
description: Apply input validation patterns using Pydantic and SQLModel for FastAPI endpoints.
---

# Skill: Input Validation

## Purpose
Define validation patterns for request inputs. Ensures data integrity before reaching business logic or database.

## Stack Context
- **Backend**: FastAPI + Pydantic + SQLModel
- **Validation**: Pydantic v2 validators
- **Database**: SQLModel with Neon Postgres

## Validation Layers

```
Request → Pydantic Schema → Business Logic → SQLModel → Database
          (validation)      (rules)          (constraints)
```

## Request Schemas

### Task Schemas
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else v
```

### User Schemas
```python
from pydantic import BaseModel, Field, EmailStr, field_validator
import re

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)
```

## Common Validators

### UUID Validation
```python
from uuid import UUID
from pydantic import field_validator

class TaskIdParam(BaseModel):
    task_id: UUID

    @field_validator("task_id", mode="before")
    @classmethod
    def validate_uuid(cls, v):
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return v
```

### Enum Validation
```python
from enum import Enum

class TaskStatus(str, Enum):
    all = "all"
    active = "active"
    completed = "completed"

class TaskFilter(BaseModel):
    status: TaskStatus = TaskStatus.all
```

## FastAPI Integration

### Request Body Validation
```python
@router.post("/tasks", status_code=201)
async def create_task(
    task: TaskCreate,  # Pydantic validates automatically
    user_id: UUID = Depends(get_current_user_id)
):
    # task.title is guaranteed non-empty, max 255 chars
    return await insert_task(task, user_id)
```

### Query Parameter Validation
```python
@router.get("/tasks")
async def list_tasks(
    status: TaskStatus = TaskStatus.all,
    limit: int = Field(default=50, ge=1, le=100),
    offset: int = Field(default=0, ge=0)
):
    return await fetch_tasks(status, limit, offset)
```

### Path Parameter Validation
```python
from fastapi import Path

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: UUID = Path(..., description="Task UUID")
):
    return await fetch_task(task_id)
```

## Error Responses

FastAPI automatically returns 422 for validation errors:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### Custom Error Handler
```python
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=400,
        content={
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input",
                "details": errors
            }
        }
    )
```

## Validation Rules Summary

| Field | Constraints |
|-------|-------------|
| `email` | Valid email format (EmailStr) |
| `password` | Min 8 chars, 1 letter, 1 number |
| `title` | 1-255 chars, not whitespace-only |
| `description` | Max 1000 chars, optional |
| `completed` | Boolean |
| `task_id` | Valid UUID v4 |

## Checklist
- [ ] All request bodies have Pydantic schemas
- [ ] Required fields use `Field(...)` or no default
- [ ] Optional fields use `Optional[T]` with default
- [ ] String fields have length constraints
- [ ] Custom validators handle edge cases
- [ ] 422 errors transformed to consistent format
