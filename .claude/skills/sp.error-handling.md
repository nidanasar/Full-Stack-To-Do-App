---
description: Apply consistent error handling patterns across FastAPI backend.
---

# Skill: Error Handling

## Purpose
Define error handling patterns that provide consistent, secure, and user-friendly error responses across all API endpoints.

## Stack Context
- **Backend**: FastAPI + Python
- **Frontend**: Next.js + TypeScript
- **Pattern**: Centralized exception handlers

## Error Taxonomy

| Code | HTTP | When to Use |
|------|------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input format or constraints |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Valid auth but insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Entity doesn't exist OR not owned by user |
| `CONFLICT` | 409 | Duplicate resource (e.g., email exists) |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Custom Exception Classes

```python
# exceptions.py
from fastapi import HTTPException

class AppException(HTTPException):
    """Base exception for application errors."""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        super().__init__(status_code=status_code, detail={"code": code, "message": message})

class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} not found",
            status_code=404
        )

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401
        )

class ForbiddenError(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403
        )

class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409
        )

class ValidationError(AppException):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=400
        )
```

## Global Exception Handlers

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "data": None,
            "error": {"code": exc.code, "message": exc.detail["message"]}
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()]
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

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log full error for debugging, return generic message to client
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

## Usage in Routes

```python
from .exceptions import NotFoundError, ConflictError

@router.get("/tasks/{task_id}")
async def get_task(task_id: UUID, user_id: UUID = Depends(get_current_user_id)):
    task = await fetch_task(task_id, user_id)
    if not task:
        raise NotFoundError("Task")  # Returns 404 with consistent format
    return success(task)

@router.post("/auth/register")
async def register(user: UserCreate):
    existing = await get_user_by_email(user.email)
    if existing:
        raise ConflictError("Email already registered")
    # ... create user
```

## Security Considerations

### 1. Don't Leak Information
```python
# BAD - reveals whether email exists
raise HTTPException(404, "User with this email not found")

# GOOD - generic message prevents enumeration
raise UnauthorizedError("Invalid credentials")
```

### 2. Return 404 for Unowned Resources
```python
# BAD - reveals resource exists but user doesn't own it
raise ForbiddenError("You don't own this task")

# GOOD - prevents resource enumeration
raise NotFoundError("Task")
```

### 3. Don't Expose Stack Traces
```python
# BAD
@app.exception_handler(Exception)
async def handler(request, exc):
    return {"error": str(exc), "trace": traceback.format_exc()}

# GOOD
@app.exception_handler(Exception)
async def handler(request, exc):
    logger.exception(exc)  # Log for debugging
    return {"error": {"code": "INTERNAL_ERROR", "message": "An error occurred"}}
```

## Frontend Error Handling

```typescript
// lib/api.ts
class ApiError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, options);
  const json = await response.json();

  if (json.error) {
    throw new ApiError(json.error.code, json.error.message);
  }

  return json.data;
}

// Usage in component
try {
  const tasks = await apiClient<Task[]>("/tasks");
} catch (error) {
  if (error instanceof ApiError) {
    switch (error.code) {
      case "UNAUTHORIZED":
        router.push("/login");
        break;
      case "RESOURCE_NOT_FOUND":
        toast.error("Task not found");
        break;
      default:
        toast.error(error.message);
    }
  }
}
```

## Checklist
- [ ] All custom exceptions extend `AppException`
- [ ] Global handlers registered in main.py
- [ ] 500 errors logged but not exposed to client
- [ ] 404 used for unowned resources (not 403)
- [ ] Login errors use generic messages
- [ ] Frontend handles all error codes gracefully
