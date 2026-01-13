---
description: Implement JWT authentication flow between Better Auth (frontend) and FastAPI (backend).
---

# Skill: JWT Authentication

## Purpose
Define the authentication boundary between Next.js frontend (Better Auth) and FastAPI backend (JWT validation). Ensures secure token flow across the stack.

## Stack Context
- **Frontend**: Next.js + Better Auth (handles login/register UI and token storage)
- **Backend**: FastAPI + python-jose (validates JWT, extracts user context)
- **Database**: Neon Postgres (shared user table)

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│   Next.js Frontend  │         │   FastAPI Backend   │
│   (Better Auth)     │         │   (JWT Validation)  │
├─────────────────────┤         ├─────────────────────┤
│ 1. User logs in     │         │                     │
│ 2. Better Auth      │────────>│ 3. Validate JWT     │
│    sends JWT in     │  Bearer │ 4. Extract user_id  │
│    Authorization    │  Token  │ 5. Process request  │
│    header           │         │                     │
└─────────────────────┘         └─────────────────────┘
```

## JWT Contract

### Token Structure
```json
{
  "sub": "user-uuid-here",
  "email": "user@example.com",
  "iat": 1699999999,
  "exp": 1700604799
}
```

### Required Claims
| Claim | Type | Description |
|-------|------|-------------|
| `sub` | UUID string | User ID (primary identifier) |
| `email` | string | User email (optional, for display) |
| `iat` | int | Issued at timestamp |
| `exp` | int | Expiration timestamp (7 days default) |

## Backend Implementation (FastAPI)

### Dependencies
```python
# requirements.txt / pyproject.toml
python-jose[cryptography]
```

### JWT Validation
```python
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from uuid import UUID
import os

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: UUID
    email: str | None = None
    exp: int

def verify_jwt(token: str) -> TokenPayload:
    """Verify JWT and return payload. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"]
        )
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Dependency to extract user_id from JWT."""
    payload = verify_jwt(credentials.credentials)
    return payload.sub

async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency to extract email from JWT."""
    payload = verify_jwt(credentials.credentials)
    return payload.email
```

### Protected Route Example
```python
from fastapi import APIRouter, Depends
from uuid import UUID

router = APIRouter()

@router.get("/me")
async def get_current_user(
    user_id: UUID = Depends(get_current_user_id)
):
    return {"user_id": str(user_id)}

@router.get("/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id)
):
    # user_id guaranteed to be valid from JWT
    return await get_tasks_for_user(user_id)
```

## Frontend Implementation (Next.js + Better Auth)

### API Client Setup
```typescript
// lib/api.ts
import { auth } from "@/lib/auth";

export async function apiClient(
  endpoint: string,
  options: RequestInit = {}
) {
  const session = await auth();

  const headers = new Headers(options.headers);
  if (session?.accessToken) {
    headers.set("Authorization", `Bearer ${session.accessToken}`);
  }
  headers.set("Content-Type", "application/json");

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
    { ...options, headers }
  );

  if (response.status === 401) {
    // Token expired - trigger re-auth
    throw new Error("Unauthorized");
  }

  return response.json();
}
```

### Using in Components
```typescript
// app/tasks/page.tsx
import { apiClient } from "@/lib/api";

export default async function TasksPage() {
  const tasks = await apiClient("/tasks");
  return <TaskList tasks={tasks} />;
}
```

## Environment Variables

### Backend (.env)
```
JWT_SECRET=your-secure-256-bit-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-better-auth-secret
```

## Failure Modes

| Scenario | HTTP Code | Response |
|----------|-----------|----------|
| Missing Authorization header | 401 | `{"detail": "Not authenticated"}` |
| Invalid token format | 401 | `{"detail": "Invalid or expired token"}` |
| Expired token | 401 | `{"detail": "Invalid or expired token"}` |
| Wrong signature | 401 | `{"detail": "Invalid or expired token"}` |

## Security Rules
1. NEVER log full JWT tokens
2. NEVER store JWT in localStorage (use httpOnly cookies via Better Auth)
3. ALWAYS validate token on every request
4. ALWAYS use HTTPS in production
5. Rotate JWT_SECRET periodically

## Checklist
- [ ] JWT_SECRET is 256+ bits and stored securely
- [ ] Token expiration is set (default: 7 days)
- [ ] Backend validates signature and expiration
- [ ] Frontend handles 401 with re-authentication
- [ ] CORS configured for frontend origin
