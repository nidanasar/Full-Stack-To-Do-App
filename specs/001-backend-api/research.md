# Research: Backend API Implementation

**Feature**: 001-backend-api
**Date**: 2026-01-13
**Status**: Complete

## Overview

Research phase for Backend API implementation. All technical decisions are well-defined in existing specs - no critical unknowns requiring clarification.

---

## Decisions

### 1. FastAPI Project Structure

**Decision**: Use flat module structure with route-based organization

**Rationale**:
- FastAPI best practices favor functional organization
- Aligns with constitution principle V (Clean Architecture)
- Simpler than layered architecture for MVP scope

**Alternatives Considered**:
- Domain-driven design (DDD) layers: Rejected - overkill for Phase II CRUD
- Single file: Rejected - poor maintainability

**Structure**:
```
backend/
├── main.py           # FastAPI app entry, router registration
├── config.py         # Settings and environment variables
├── database.py       # Async engine, session factory
├── models.py         # SQLModel User and Task models
├── schemas.py        # Pydantic request/response schemas
├── auth.py           # JWT verification, password hashing
├── routes/
│   ├── __init__.py
│   ├── auth.py       # /auth/register, /auth/login
│   └── tasks.py      # /tasks CRUD endpoints
├── dependencies.py   # FastAPI dependencies (get_db, get_current_user)
└── exceptions.py     # Custom exception handlers
```

---

### 2. JWT Verification Strategy

**Decision**: Middleware-free approach using FastAPI dependencies

**Rationale**:
- FastAPI Depends() is more Pythonic than middleware
- Cleaner exception handling per-route
- Better testability with dependency injection
- Aligns with existing @specs/features/authentication.md

**Alternatives Considered**:
- Global middleware: Rejected - harder to exclude public routes
- OAuth2PasswordBearer built-in: Used as base, extended for JWT validation

**Implementation Pattern**:
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Decode JWT, validate, return user
```

---

### 3. Async Database Session Management

**Decision**: Context manager pattern with SQLAlchemy AsyncSession

**Rationale**:
- Native async support for Neon PostgreSQL
- Connection pooling built-in
- Clean session lifecycle management
- Per @specs/database/schema.md specifications

**Alternatives Considered**:
- Sync sessions: Rejected - blocks event loop
- Raw asyncpg: Rejected - lose SQLModel type safety

**Pool Configuration** (from database spec):
- Pool Size: 5
- Max Overflow: 10
- Pool Timeout: 30s
- Pool Recycle: 1800s

---

### 4. Password Hashing

**Decision**: bcrypt via passlib library

**Rationale**:
- Industry standard for password hashing
- Built-in salt generation
- Configurable work factor
- Per constitution Section III security requirements

**Alternatives Considered**:
- argon2: Good but less universal library support
- scrypt: Good but bcrypt is more common in Python ecosystem

---

### 5. Error Response Format

**Decision**: Consistent JSON error structure per API spec

**Rationale**:
- Single format for all errors simplifies frontend handling
- Error codes enable programmatic handling
- Messages are user-friendly
- Per @specs/api/rest-endpoints.md

**Format**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

**Error Codes**:
- UNAUTHORIZED (401)
- NOT_FOUND (404)
- CONFLICT (409)
- VALIDATION_ERROR (422)
- INTERNAL_ERROR (500)

---

### 6. User Isolation Implementation

**Decision**: Query-level filtering with user_id from JWT

**Rationale**:
- All task queries include WHERE user_id = ?
- User ID extracted from JWT sub claim only
- 404 returned for both "not found" and "wrong user"
- Per constitution Section III

**Anti-Pattern Prevention**:
- Never accept user_id from request body
- Never accept user_id from URL path
- Always validate task ownership before any operation

---

## Dependencies

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ^0.109.0 | Web framework |
| uvicorn | ^0.27.0 | ASGI server |
| sqlmodel | ^0.0.14 | ORM with type safety |
| asyncpg | ^0.29.0 | Async PostgreSQL driver |
| python-jose[cryptography] | ^3.3.0 | JWT encoding/decoding |
| passlib[bcrypt] | ^1.7.4 | Password hashing |
| pydantic[email-validator] | ^2.5.0 | Request validation |
| python-multipart | ^0.0.6 | Form data parsing |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | Neon PostgreSQL connection string |
| BETTER_AUTH_SECRET | Yes | JWT signing secret (shared with frontend) |
| ENVIRONMENT | No | "development" or "production" |

---

## Integration Points

### Frontend Integration

- Better Auth (frontend) issues JWTs
- Backend validates JWTs using shared BETTER_AUTH_SECRET
- CORS must allow frontend origin
- Cookie-based JWT transport supported

### Database Integration

- Neon Serverless PostgreSQL
- SSL required (sslmode=require)
- Async connections via asyncpg
- Connection string format: `postgresql+asyncpg://...`

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| JWT secret mismatch | Startup validation, clear error message |
| Database connection failures | Graceful 500 response, logged details |
| Concurrent updates | Last write wins (standard PostgreSQL) |
| User enumeration | 404 for all "not found" cases |

---

## References

- @specs/api/rest-endpoints.md - API contract
- @specs/database/schema.md - Database schema
- @specs/features/authentication.md - Auth flows
- @.specify/memory/constitution.md - Project principles
