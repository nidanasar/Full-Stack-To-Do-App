# Data Model: Frontend Web Application

**Feature**: 002-frontend-web
**Date**: 2026-01-15

---

## TypeScript Interfaces

### User Entity

```typescript
// User data from API
interface User {
  id: string           // UUID from backend
  email: string        // User's email address
  created_at: string   // ISO date string
}
```

### Task Entity

```typescript
// Task data from API
interface Task {
  id: string           // UUID from backend
  user_id: string      // Owner's UUID
  title: string        // 1-500 characters
  description: string | null  // Optional, max 5000 chars
  completed: boolean   // Completion status
  created_at: string   // ISO date string
  updated_at: string   // ISO date string
}

// For creating new tasks
interface TaskCreate {
  title: string        // Required, 1-500 chars
  description?: string // Optional
}

// For updating tasks (full)
interface TaskUpdate {
  title: string
  description: string | null
  completed: boolean
}

// For patching tasks (partial)
interface TaskPatch {
  title?: string
  description?: string | null
  completed?: boolean
}
```

### API Response Types

```typescript
// Standard API response wrapper
interface ApiResponse<T> {
  data: T
  error?: never
}

// Error response
interface ApiError {
  data?: never
  error: {
    message: string
    code: string
  }
}

// Union type for API calls
type ApiResult<T> = ApiResponse<T> | ApiError

// Auth response from login/register
interface AuthResponse {
  user: User
  token: string  // JWT (stored in httpOnly cookie by Better Auth)
}

// Task list response
interface TaskListResponse {
  tasks: Task[]
}
```

### Session Types

```typescript
// Better Auth session
interface Session {
  user: User
  expires: string  // ISO date string
}
```

### Filter State

```typescript
// Task filter options
type TaskFilter = 'all' | 'active' | 'completed'
```

---

## State Management

### Client-Side State

| State | Type | Location | Purpose |
|-------|------|----------|---------|
| tasks | Task[] | TaskList component | Current task list |
| filter | TaskFilter | TaskList component | Active filter |
| isLoading | boolean | Components | Loading indicators |
| error | string \| null | Components | Error messages |

### Server-Side Data

| Data | Fetched In | Cached |
|------|------------|--------|
| User session | middleware, layout | Yes (Better Auth) |
| Task list | /tasks page | No (always fresh) |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Server         │    │  Client         │                │
│  │  Components     │    │  Components     │                │
│  │                 │    │                 │                │
│  │  - TasksPage    │───▶│  - TaskList     │                │
│  │  - Layout       │    │  - TaskItem     │                │
│  │                 │    │  - TaskForm     │                │
│  └────────┬────────┘    └────────┬────────┘                │
│           │                      │                          │
│           ▼                      ▼                          │
│  ┌─────────────────────────────────────────┐               │
│  │           API Client (lib/api.ts)        │               │
│  │         credentials: 'include'           │               │
│  └────────────────────┬────────────────────┘               │
│                       │                                     │
└───────────────────────┼─────────────────────────────────────┘
                        │ httpOnly cookie (JWT)
                        ▼
              ┌─────────────────────┐
              │  FastAPI Backend    │
              │  localhost:8000     │
              └─────────────────────┘
```

---

## Validation Rules (Client-Side)

### Registration Form

| Field | Rule | Error Message |
|-------|------|---------------|
| email | Valid email format | "Please enter a valid email" |
| password | Min 8 characters | "Password must be at least 8 characters" |
| confirmPassword | Must match password | "Passwords do not match" |

### Login Form

| Field | Rule | Error Message |
|-------|------|---------------|
| email | Required, valid format | "Please enter a valid email" |
| password | Required | "Password is required" |

### Task Form

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required, 1-500 chars | "Title is required" / "Title too long" |
| description | Optional, max 5000 chars | "Description too long" |

---

## References

- @specs/api/rest-endpoints.md - Backend API contract
- @specs/001-backend-api/data-model.md - Backend data model
- @specs/002-frontend-web/research.md - Technical decisions
