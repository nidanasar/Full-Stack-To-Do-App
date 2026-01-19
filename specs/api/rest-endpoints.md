# API Specification — Phase II

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Status**: Ratified

## Purpose

Define all REST API endpoints for Phase II, ensuring consistent, secure, and strictly user-scoped task management.

This specification governs API contracts, request/response formats, authentication requirements, and error handling.

---

## API Style

| Aspect | Value |
|--------|-------|
| Architecture | RESTful |
| State | Stateless |
| Format | JSON (application/json) |
| Versioning | `/api/v1` prefix |
| Authentication | JWT Bearer token |

### Base URL

```
Production: https://api.<domain>/api/v1
Development: http://localhost:8000/api/v1
```

### Content Type

All requests and responses use JSON:

```
Content-Type: application/json
Accept: application/json
```

---

## Authentication & Authorization

### JWT Requirement

All endpoints except `/auth/register` and `/auth/login` require a valid JWT.

**Header Format**:
```
Authorization: Bearer <jwt>
```

### Backend Validation

On every protected request, the backend enforces:

| Check | Description | On Failure |
|-------|-------------|------------|
| Token Present | `Authorization` header exists | 401 Unauthorized |
| Valid Signature | Signed with `BETTER_AUTH_SECRET` | 401 Unauthorized |
| Not Expired | `exp` claim > current time | 401 Unauthorized |
| User Exists | `sub` claim matches user in DB | 401 Unauthorized |

### User Isolation

**Critical Design Decision**: User ID is extracted from the JWT `sub` claim, NOT from URL path parameters.

Per constitution Section III: "user_id MUST NEVER come from request body; ALWAYS from JWT"

```
# User ID source
✅ CORRECT: user_id = jwt.sub (from token)
❌ WRONG: user_id = request.path_param (from URL)
❌ WRONG: user_id = request.body.user_id (from body)
```

### Authorization Response Codes

| Condition | Status Code | Response |
|-----------|-------------|----------|
| No token provided | 401 Unauthorized | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| Invalid token | 401 Unauthorized | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}}` |
| Expired token | 401 Unauthorized | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}}` |
| Resource not found | 404 Not Found | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |
| Wrong user's resource | 404 Not Found | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |

**Note**: Wrong user access returns 404 (not 403) to prevent resource enumeration.

---

## Endpoint Overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Create user account |
| POST | `/api/v1/auth/login` | Public | Authenticate user |
| GET | `/api/v1/tasks` | Protected | List user's tasks |
| POST | `/api/v1/tasks` | Protected | Create new task |
| GET | `/api/v1/tasks/{task_id}` | Protected | Get single task |
| PUT | `/api/v1/tasks/{task_id}` | Protected | Update task (full) |
| PATCH | `/api/v1/tasks/{task_id}` | Protected | Update task (partial) |
| DELETE | `/api/v1/tasks/{task_id}` | Protected | Delete task |

---

## Authentication Endpoints

### POST /api/v1/auth/register

Create a new user account.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Minimum 8 characters |

**Success Response**: `201 Created`
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-13T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 409 Conflict | Email already exists | `{"error": {"code": "CONFLICT", "message": "Email already registered"}}` |
| 422 Unprocessable | Invalid email format | `{"error": {"code": "VALIDATION_ERROR", "message": "Invalid email format"}}` |
| 422 Unprocessable | Password too short | `{"error": {"code": "VALIDATION_ERROR", "message": "Password must be at least 8 characters"}}` |

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123"}'
```

---

### POST /api/v1/auth/login

Authenticate an existing user.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Non-empty |

**Success Response**: `200 OK`
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-13T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | Invalid credentials | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid credentials"}}` |
| 422 Unprocessable | Missing fields | `{"error": {"code": "VALIDATION_ERROR", "message": "Email and password required"}}` |

**Security Note**: The same error message is returned for both "wrong password" and "email not found" to prevent user enumeration.

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123"}'
```

---

## Task Endpoints

### POST /api/v1/tasks

Create a new task for the authenticated user.

**Authentication**: Required (JWT)

**Request Headers**:
```
Authorization: Bearer <jwt>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-500 characters |
| description | string | No | 0-5000 characters |

**Success Response**: `201 Created`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T10:30:00Z"
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | No/invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| 422 Unprocessable | Empty title | `{"error": {"code": "VALIDATION_ERROR", "message": "Title is required"}}` |
| 422 Unprocessable | Title too long | `{"error": {"code": "VALIDATION_ERROR", "message": "Title must be 500 characters or less"}}` |

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

---

### GET /api/v1/tasks

List all tasks for the authenticated user.

**Authentication**: Required (JWT)

**Request Headers**:
```
Authorization: Bearer <jwt>
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| completed | boolean | No | (all) | Filter by completion status |
| sort | string | No | `created_at` | Sort field |
| order | string | No | `desc` | Sort order: `asc` or `desc` |

**Success Response**: `200 OK`
```json
{
  "tasks": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-13T10:30:00Z",
      "updated_at": "2026-01-13T10:30:00Z"
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "title": "Call dentist",
      "description": null,
      "completed": true,
      "created_at": "2026-01-12T09:00:00Z",
      "updated_at": "2026-01-13T08:00:00Z"
    }
  ]
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | No/invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |

**Example Requests**:
```bash
# Get all tasks
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <jwt>"

# Get only completed tasks
curl -X GET "http://localhost:8000/api/v1/tasks?completed=true" \
  -H "Authorization: Bearer <jwt>"

# Get pending tasks sorted by creation date ascending
curl -X GET "http://localhost:8000/api/v1/tasks?completed=false&sort=created_at&order=asc" \
  -H "Authorization: Bearer <jwt>"
```

---

### GET /api/v1/tasks/{task_id}

Get a single task by ID.

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | UUID | Task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt>
```

**Success Response**: `200 OK`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T10:30:00Z"
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | No/invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| 404 Not Found | Task not found | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |
| 404 Not Found | Task belongs to different user | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |

**Example Request**:
```bash
curl -X GET http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <jwt>"
```

---

### PUT /api/v1/tasks/{task_id}

Update a task (full replacement).

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | UUID | Task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, butter",
  "completed": true
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-500 characters |
| description | string | No | 0-5000 characters (null clears) |
| completed | boolean | Yes | true or false |

**Success Response**: `200 OK`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, butter",
  "completed": true,
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T11:45:00Z"
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | No/invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| 404 Not Found | Task not found / wrong user | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |
| 422 Unprocessable | Validation failed | `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}` |

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries (updated)", "description": "Milk, eggs, bread, butter", "completed": true}'
```

---

### PATCH /api/v1/tasks/{task_id}

Partially update a task.

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | UUID | Task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "completed": true
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | No | 1-500 characters |
| description | string | No | 0-5000 characters |
| completed | boolean | No | true or false |

**Success Response**: `200 OK`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T11:45:00Z"
}
```

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | No/invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| 404 Not Found | Task not found / wrong user | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |
| 422 Unprocessable | Validation failed | `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}` |

**Use Cases**:
- Toggle completion: `{"completed": true}`
- Update title only: `{"title": "New title"}`
- Clear description: `{"description": null}`

**Example Request**:
```bash
# Toggle completion status
curl -X PATCH http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

---

### DELETE /api/v1/tasks/{task_id}

Delete a task.

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | UUID | Task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt>
```

**Success Response**: `204 No Content`

(Empty response body)

**Error Responses**:

| Status | Condition | Response |
|--------|-----------|----------|
| 401 Unauthorized | No/invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| 404 Not Found | Task not found / wrong user | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer <jwt>"
```

---

## Request/Response Schemas

### User Schemas

**UserCreate** (Request):
```json
{
  "email": "string (email format)",
  "password": "string (min 8 chars)"
}
```

**UserResponse** (Response):
```json
{
  "id": "uuid",
  "email": "string",
  "created_at": "ISO 8601 timestamp"
}
```

**AuthResponse** (Response):
```json
{
  "user": UserResponse,
  "token": "JWT string"
}
```

### Task Schemas

**TaskCreate** (Request):
```json
{
  "title": "string (1-500 chars, required)",
  "description": "string (0-5000 chars, optional)"
}
```

**TaskUpdate** (Request - PUT):
```json
{
  "title": "string (1-500 chars, required)",
  "description": "string | null",
  "completed": "boolean (required)"
}
```

**TaskPatch** (Request - PATCH):
```json
{
  "title": "string (optional)",
  "description": "string | null (optional)",
  "completed": "boolean (optional)"
}
```

**TaskResponse** (Response):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**TaskListResponse** (Response):
```json
{
  "tasks": [TaskResponse]
}
```

### Error Schema

**ErrorResponse**:
```json
{
  "error": {
    "code": "string (error code)",
    "message": "string (human-readable message)"
  }
}
```

---

## Validation Rules

### Field Validation

| Field | Rules |
|-------|-------|
| email | Valid email format, unique in system |
| password | Minimum 8 characters |
| title | Required, 1-500 characters, non-empty |
| description | Optional, 0-5000 characters |
| completed | Boolean (true/false) |
| task_id | Valid UUID v4 format |

### Request Validation

| Rule | Enforcement |
|------|-------------|
| Content-Type must be application/json | 415 Unsupported Media Type |
| Request body must be valid JSON | 400 Bad Request |
| Required fields must be present | 422 Unprocessable Entity |
| Field types must match schema | 422 Unprocessable Entity |
| UUIDs must be valid format | 422 Unprocessable Entity |

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description"
  }
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `NOT_FOUND` | 404 | Resource not found (or access denied) |
| `CONFLICT` | 409 | Resource conflict (e.g., duplicate email) |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Status Code Reference

| Status | Meaning | When Used |
|--------|---------|-----------|
| 200 OK | Success | GET, PUT, PATCH success |
| 201 Created | Resource created | POST success |
| 204 No Content | Success, no body | DELETE success |
| 400 Bad Request | Malformed request | Invalid JSON |
| 401 Unauthorized | Auth required/failed | Missing/invalid token |
| 404 Not Found | Resource not found | Task not found or wrong user |
| 409 Conflict | Resource conflict | Duplicate email |
| 415 Unsupported Media | Wrong content type | Non-JSON request |
| 422 Unprocessable | Validation error | Invalid field values |
| 500 Internal Error | Server error | Unexpected failures |

---

## Security Constraints

### Token Security

| Constraint | Enforcement |
|------------|-------------|
| JWT in Authorization header only | Backend validation |
| No JWT in URL or query params | Code review, rejected if found |
| No JWT in request body | Code review |
| Tokens validated on every request | Middleware |

### Data Security

| Constraint | Enforcement |
|------------|-------------|
| User ID from JWT only | Backend extracts from `sub` claim |
| All queries filtered by user_id | Repository layer |
| No cross-user data access | Application logic + 404 response |
| Passwords never returned in responses | Schema design |

### Transport Security

| Constraint | Environment |
|------------|-------------|
| HTTPS required | Production |
| HTTP allowed | Development only |

### Rate Limiting (Future)

| Endpoint | Limit | Status |
|----------|-------|--------|
| /auth/login | 5 req/min | Phase III |
| /auth/register | 3 req/min | Phase III |
| /tasks/* | 100 req/min | Phase III |

---

## Phase II Constraints

### Not Implemented

| Feature | Status | Rationale |
|---------|--------|-----------|
| Pagination | Excluded | Small data sets expected |
| Bulk operations | Excluded | Single task operations sufficient |
| Search/filter by title | Excluded | Out of scope |
| Task sorting by multiple fields | Excluded | Single sort field sufficient |
| Rate limiting | Excluded | Phase III |
| API versioning beyond v1 | Excluded | Single version for MVP |

### Data Limits

| Limit | Value | Enforcement |
|-------|-------|-------------|
| Tasks per user | 1000 | Application (soft) |
| Title length | 500 chars | Pydantic validation |
| Description length | 5000 chars | Pydantic validation |
| Request body size | 1MB | Server config |

---

## FastAPI Implementation Reference

### Router Structure

```python
# app/api/v1/router.py
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Auth routes (public)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Task routes (protected)
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
```

### Auth Router

```python
# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, AuthResponse
from app.services.auth import AuthService

router = APIRouter()

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, auth_service: AuthService = Depends()):
    """Create a new user account."""
    return await auth_service.register(data)

@router.post("/login", response_model=AuthResponse)
async def login(data: UserCreate, auth_service: AuthService = Depends()):
    """Authenticate user and return JWT."""
    return await auth_service.login(data)
```

### Tasks Router

```python
# app/api/v1/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional
from app.schemas.task import TaskCreate, TaskUpdate, TaskPatch, TaskResponse, TaskListResponse
from app.models.user import User
from app.core.deps import get_current_user
from app.services.task import TaskService

router = APIRouter()

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Create a new task for the authenticated user."""
    return await task_service.create(current_user.id, data)

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    completed: Optional[bool] = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """List all tasks for the authenticated user."""
    tasks = await task_service.list_by_user(
        current_user.id,
        completed=completed,
        sort=sort,
        order=order
    )
    return TaskListResponse(tasks=tasks)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Get a single task by ID."""
    task = await task_service.get_by_id(task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Update a task (full replacement)."""
    task = await task_service.update(task_id, current_user.id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: UUID,
    data: TaskPatch,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Partially update a task."""
    task = await task_service.patch(task_id, current_user.id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Delete a task."""
    deleted = await task_service.delete(task_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resource not found")
```

---

## Functional Requirements

### Authentication Requirements

- **FR-API-001**: System MUST provide POST /auth/register endpoint
- **FR-API-002**: System MUST provide POST /auth/login endpoint
- **FR-API-003**: System MUST return JWT on successful auth
- **FR-API-004**: System MUST validate email format on registration
- **FR-API-005**: System MUST enforce password minimum length

### Task Requirements

- **FR-API-006**: System MUST provide full CRUD for tasks
- **FR-API-007**: System MUST filter tasks by authenticated user
- **FR-API-008**: System MUST support filtering by completion status
- **FR-API-009**: System MUST support sorting by creation date
- **FR-API-010**: System MUST validate task title is non-empty

### Security Requirements

- **FR-API-011**: System MUST require JWT for all task endpoints
- **FR-API-012**: System MUST return 401 for missing/invalid tokens
- **FR-API-013**: System MUST return 404 for wrong user's tasks
- **FR-API-014**: System MUST NOT expose user_id in error messages

---

## API Acceptance Criteria

### Authentication

- [ ] **AC-API-001**: POST /auth/register creates user and returns JWT
- [ ] **AC-API-002**: POST /auth/login validates credentials and returns JWT
- [ ] **AC-API-003**: Duplicate email registration returns 409
- [ ] **AC-API-004**: Invalid credentials return 401 with generic message

### Task CRUD

- [ ] **AC-API-005**: POST /tasks creates task for authenticated user
- [ ] **AC-API-006**: GET /tasks returns only authenticated user's tasks
- [ ] **AC-API-007**: GET /tasks/{id} returns task if owned by user
- [ ] **AC-API-008**: PUT /tasks/{id} updates all fields
- [ ] **AC-API-009**: PATCH /tasks/{id} updates specified fields only
- [ ] **AC-API-010**: DELETE /tasks/{id} removes task and returns 204

### Authorization

- [ ] **AC-API-011**: Requests without token receive 401
- [ ] **AC-API-012**: Requests with invalid token receive 401
- [ ] **AC-API-013**: Accessing other user's task returns 404
- [ ] **AC-API-014**: User ID is extracted from JWT, not request

### Validation

- [ ] **AC-API-015**: Empty title rejected with 422
- [ ] **AC-API-016**: Invalid UUID rejected with 422
- [ ] **AC-API-017**: Invalid JSON rejected with 400
- [ ] **AC-API-018**: Missing required fields rejected with 422

---

## References

- @specs/architecture.md - System architecture (API Architecture section)
- @specs/features/authentication.md - Authentication specification
- @specs/database/schema.md - Database schema and models
- @.specify/memory/constitution.md - Project constitution (Section V: Clean Architecture)
