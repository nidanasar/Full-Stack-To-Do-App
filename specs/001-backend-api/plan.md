# Implementation Plan: Backend API

**Branch**: `001-backend-api` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-api/spec.md`

---

## Summary

Implement a FastAPI-based REST API for the Phase II Todo application with JWT authentication, SQLModel ORM, and Neon PostgreSQL. The backend provides secure, user-scoped CRUD operations for tasks with strict multi-user isolation.

**Primary Requirements**:
- JWT validation on all protected endpoints (user_id from `sub` claim only)
- Full CRUD for tasks: create, read, update (PUT/PATCH), delete
- User registration and login with bcrypt password hashing
- Async database sessions with connection pooling
- Consistent error response format

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, SQLModel, asyncpg, python-jose, passlib[bcrypt], pydantic
**Storage**: Neon Serverless PostgreSQL (asyncpg driver)
**Testing**: pytest with async support
**Target Platform**: Linux server (Vercel/Docker)
**Project Type**: Web application (backend component of monorepo)
**Performance Goals**: <100ms API response time (p95), <500ms task creation
**Constraints**: User isolation enforced, JWT-only auth, no manual code
**Scale/Scope**: 50 concurrent users, 100 tasks per user

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | PASS | All implementation derived from @specs/*, Claude Code execution |
| II. Reusable Intelligence | PASS | Using api-backend agent, auth-boundary agent |
| III. Multi-User Security | PASS | JWT validation, user_id from sub claim, 404 for wrong user |
| IV. Cloud-Native Foundation | PASS | Monorepo structure, Neon PostgreSQL, docker-compose ready |
| V. Clean Architecture | PASS | RESTful /api/v1/{resource}, Pydantic validation, async sessions |

**All gates passed. No violations requiring justification.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-api/
├── plan.md              # This file
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output (complete)
├── quickstart.md        # Phase 1 output (complete)
├── contracts/
│   └── openapi.yaml     # Phase 1 output (complete)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app entry, CORS, router registration
├── config.py            # Settings from environment variables
├── database.py          # Async engine, session factory, get_db dependency
├── models.py            # SQLModel User and Task table definitions
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT creation/verification, password hashing
├── dependencies.py      # get_current_user dependency
├── exceptions.py        # Custom exception handlers, error response format
├── routes/
│   ├── __init__.py
│   ├── auth.py          # POST /auth/register, POST /auth/login
│   └── tasks.py         # GET/POST /tasks, GET/PUT/PATCH/DELETE /tasks/{id}
├── tests/
│   ├── conftest.py      # Test fixtures, test database
│   ├── test_auth.py     # Auth endpoint tests
│   └── test_tasks.py    # Task CRUD tests
├── pyproject.toml       # UV/pip dependencies
├── .env.example         # Environment variable template
└── .env                 # Local environment (gitignored)
```

**Structure Decision**: Web application layout selected per constitution IV (monorepo). Backend is a standalone service within the monorepo, communicating with frontend via REST API.

---

## Implementation Phases

### Phase 1: Database Foundation

**Objective**: Establish database connection and ORM models

| Task | File | Description |
|------|------|-------------|
| 1.1 | config.py | Settings class with DATABASE_URL, BETTER_AUTH_SECRET |
| 1.2 | database.py | Async engine, session factory, connection pool settings |
| 1.3 | models.py | User and Task SQLModel classes per data-model.md |

**Dependencies**: None
**Validation**: Database connection test, model table creation

---

### Phase 2: Authentication Core

**Objective**: Implement JWT validation and password hashing

| Task | File | Description |
|------|------|-------------|
| 2.1 | auth.py | Password hashing with bcrypt |
| 2.2 | auth.py | JWT creation (sub, exp, iat claims) |
| 2.3 | auth.py | JWT verification with BETTER_AUTH_SECRET |
| 2.4 | dependencies.py | get_current_user dependency |
| 2.5 | exceptions.py | Error response format, 401/404/409/422 handlers |

**Dependencies**: Phase 1
**Validation**: JWT encode/decode roundtrip test

---

### Phase 3: Auth Endpoints

**Objective**: Implement registration and login

| Task | File | Description |
|------|------|-------------|
| 3.1 | routes/auth.py | POST /auth/register - create user, return JWT |
| 3.2 | routes/auth.py | POST /auth/login - validate credentials, return JWT |
| 3.3 | schemas.py | UserCreate, UserResponse, AuthResponse schemas |

**Dependencies**: Phase 2
**Validation**: Register/login flow test, duplicate email rejection

---

### Phase 4: Task CRUD Endpoints

**Objective**: Implement all task operations with user scoping

| Task | File | Description |
|------|------|-------------|
| 4.1 | schemas.py | TaskCreate, TaskUpdate, TaskPatch, TaskResponse schemas |
| 4.2 | routes/tasks.py | POST /tasks - create task for current user |
| 4.3 | routes/tasks.py | GET /tasks - list user's tasks with filters |
| 4.4 | routes/tasks.py | GET /tasks/{id} - get single task |
| 4.5 | routes/tasks.py | PUT /tasks/{id} - full update |
| 4.6 | routes/tasks.py | PATCH /tasks/{id} - partial update |
| 4.7 | routes/tasks.py | DELETE /tasks/{id} - delete task |

**Dependencies**: Phase 3
**Validation**: CRUD operations test, user isolation test

---

### Phase 5: App Assembly

**Objective**: Wire up FastAPI app with all components

| Task | File | Description |
|------|------|-------------|
| 5.1 | main.py | FastAPI app instance with metadata |
| 5.2 | main.py | CORS middleware configuration |
| 5.3 | main.py | Router registration (/api/v1 prefix) |
| 5.4 | main.py | Exception handler registration |
| 5.5 | main.py | Startup validation (DB connection, JWT secret) |

**Dependencies**: Phase 4
**Validation**: Full API integration test

---

### Phase 6: Testing & Verification

**Objective**: Comprehensive test suite

| Task | File | Description |
|------|------|-------------|
| 6.1 | tests/conftest.py | Test fixtures, async test database |
| 6.2 | tests/test_auth.py | Registration, login, JWT validation tests |
| 6.3 | tests/test_tasks.py | CRUD tests, user isolation tests |
| 6.4 | tests/test_tasks.py | Edge cases: empty title, invalid UUID, etc. |

**Dependencies**: Phase 5
**Validation**: 100% test pass rate

---

## Critical Paths

### User Isolation Flow

```
Request → JWT Extraction → User ID from sub → Query Filter → Response
                ↓
        Missing/Invalid → 401 Unauthorized
                ↓
        Wrong User's Resource → 404 Not Found (not 403)
```

### Authentication Flow

```
Register: email/password → hash password → create user → generate JWT → return
Login: email/password → find user → verify hash → generate JWT → return
Protected: JWT header → decode → validate → extract user_id → proceed
```

---

## Key Implementation Patterns

### 1. User ID Extraction (CRITICAL)

```python
# CORRECT: Always from JWT
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
    user_id = payload.get("sub")
    # Use user_id for all queries

# WRONG: Never from request
def wrong_approach(user_id: UUID = Path(...)):  # NEVER DO THIS
    pass
```

### 2. Query Scoping

```python
# All task queries MUST include user_id filter
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == current_user.id  # ALWAYS
)
```

### 3. Error Responses

```python
# Wrong user returns 404 (not 403)
if task is None or task.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Resource not found")
```

---

## Success Criteria Mapping

| Success Criteria | Implementation | Validation |
|-----------------|----------------|------------|
| SC-001: <500ms creation | Async DB, connection pool | Load test |
| SC-002: <200ms list | Indexed queries | Load test |
| SC-003: User isolation | Query filter on user_id | Multi-user test |
| SC-004: 401 for unauth | JWT dependency | Auth test |
| SC-005: 409 for duplicate | Unique constraint | Registration test |
| SC-006: bcrypt passwords | passlib[bcrypt] | Hash verification |
| SC-007: Consistent JSON | Exception handlers | Response format test |
| SC-008: 50 concurrent | Connection pool | Stress test |
| SC-009: JWT before DB | Dependency order | Auth test |
| SC-010: Data integrity | FK constraints | Cascade delete test |

---

## Risk Mitigations

| Risk | Mitigation | Fallback |
|------|------------|----------|
| JWT secret mismatch | Startup validation | Clear error message |
| DB connection failure | Connection pool retry | 500 with logging |
| Concurrent updates | Last write wins | N/A (acceptable) |
| User enumeration | 404 for all "not found" | N/A (by design) |

---

## Dependencies on Other Specs

| Spec | Dependency Type | Critical Items |
|------|-----------------|----------------|
| @specs/api/rest-endpoints.md | Contract | Endpoint paths, status codes, schemas |
| @specs/database/schema.md | Schema | Table definitions, indexes, constraints |
| @specs/features/authentication.md | Flow | JWT claims, validation order |
| @.specify/memory/constitution.md | Principles | All 5 principles compliance |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks via api-backend agent
3. Run test suite for validation
4. Verify against success criteria

---

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | specs/001-backend-api/research.md | Complete |
| Data Model | specs/001-backend-api/data-model.md | Complete |
| OpenAPI Contract | specs/001-backend-api/contracts/openapi.yaml | Complete |
| Quickstart | specs/001-backend-api/quickstart.md | Complete |
| Implementation Plan | specs/001-backend-api/plan.md | Complete |

---

## References

- @specs/001-backend-api/spec.md - Feature specification
- @specs/api/rest-endpoints.md - API contract
- @specs/database/schema.md - Database schema
- @specs/features/authentication.md - Auth flows
- @.specify/memory/constitution.md - Project principles
