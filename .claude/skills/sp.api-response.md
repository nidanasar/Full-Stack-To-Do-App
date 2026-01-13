---
description: Apply consistent API response structure for all FastAPI endpoints.
---

# Skill: API Response Contract

## Purpose
Define a consistent response structure for all API endpoints. Ensures frontend can reliably parse responses and handle errors.

## Stack Context
- **Backend**: FastAPI + Pydantic
- **Frontend**: Next.js + TypeScript

## Response Structure

### Success Response
```json
{
  "data": { /* entity or array */ },
  "error": null
}
```

### Error Response
```json
{
  "data": null,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Task not found"
  }
}
```

## Pydantic Models

```python
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

# Usage examples
class TaskResponse(ApiResponse[Task]):
    pass

class TaskListResponse(ApiResponse[list[Task]]):
    pass
```

## Response Helpers

```python
from fastapi import Response
from typing import TypeVar, Any

T = TypeVar("T")

def success(data: T) -> dict:
    """Wrap successful response."""
    return {"data": data, "error": None}

def error(code: str, message: str, status_code: int = 400) -> dict:
    """Wrap error response."""
    return {
        "data": None,
        "error": {"code": code, "message": message}
    }
```

## Endpoint Examples

### Single Resource
```python
@router.get("/tasks/{task_id}", response_model=ApiResponse[Task])
async def get_task(task_id: UUID, user_id: UUID = Depends(get_current_user_id)):
    task = await fetch_task(task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return success(task)
```

### Collection
```python
@router.get("/tasks", response_model=ApiResponse[list[Task]])
async def list_tasks(user_id: UUID = Depends(get_current_user_id)):
    tasks = await fetch_tasks_for_user(user_id)
    return success(tasks)
```

### Create
```python
@router.post("/tasks", status_code=201, response_model=ApiResponse[Task])
async def create_task(task: TaskCreate, user_id: UUID = Depends(get_current_user_id)):
    new_task = await insert_task(task, user_id)
    return success(new_task)
```

### Delete
```python
@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: UUID, user_id: UUID = Depends(get_current_user_id)):
    deleted = await remove_task(task_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
```

## Frontend TypeScript Types

```typescript
// types/api.ts
interface ErrorDetail {
  code: string;
  message: string;
}

interface ApiResponse<T> {
  data: T | null;
  error: ErrorDetail | null;
}

// Usage
type TaskResponse = ApiResponse<Task>;
type TaskListResponse = ApiResponse<Task[]>;
```

## Frontend API Client

```typescript
// lib/api.ts
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_URL}${endpoint}`, options);
  const json = await response.json();

  if (json.error) {
    throw new ApiError(json.error.code, json.error.message);
  }

  return json;
}

// Usage
const { data: tasks } = await apiClient<Task[]>("/tasks");
```

## HTTP Status Codes

| Operation | Success | Error Cases |
|-----------|---------|-------------|
| GET (single) | 200 | 404, 401 |
| GET (list) | 200 | 401 |
| POST | 201 | 400, 401, 409 |
| PATCH | 200 | 400, 401, 404 |
| DELETE | 204 | 401, 404 |

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input |
| `UNAUTHORIZED` | 401 | Missing/invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Entity doesn't exist |
| `CONFLICT` | 409 | Duplicate resource |
| `INTERNAL_ERROR` | 500 | Server error |

## Checklist
- [ ] All endpoints return `{data, error}` structure
- [ ] Error responses include `code` and `message`
- [ ] Status codes match operation semantics
- [ ] Frontend types match backend response models
