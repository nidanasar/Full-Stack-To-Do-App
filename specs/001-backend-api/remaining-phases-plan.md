# Implementation Plan: Remaining Phases (7-9)

**Feature**: 001-backend-api
**Date**: 2026-01-14
**Status**: Phases 1-6 Complete, 3 Phases Remaining

---

## Summary

| Phase | Description | Tasks | Estimated Effort |
|-------|-------------|-------|------------------|
| 7 | Task Deletion (US4) | 3 | Small |
| 8 | App Assembly | 7 | Medium |
| 9 | Polish & Verification | 8 | Medium |
| **Total** | | **18** | |

---

## Phase 7: Task Deletion (US4)

**Goal**: Authenticated users can delete their tasks

### Tasks

| ID | Description | File |
|----|-------------|------|
| T042 | Implement DELETE /api/v1/tasks/{task_id} with ownership check | `routes/tasks.py` |
| T043 | Return 204 No Content on successful deletion | `routes/tasks.py` |
| T044 | Return 404 for non-existent OR other user's task | `routes/tasks.py` |

### Implementation Details

```python
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "Missing or invalid JWT"},
        404: {"description": "Task not found or not owned by user"},
    },
)
async def delete_task(
    task_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a task with ownership verification."""
    task = await get_task_with_ownership(db, task_id, current_user)
    await db.delete(task)
```

### Checkpoint
- Users can delete their tasks
- Returns 204 on success
- Returns 404 for unauthorized access (prevents enumeration)

---

## Phase 8: App Assembly

**Goal**: Wire up FastAPI app with all components into runnable application

### Tasks

| ID | Description | File |
|----|-------------|------|
| T045 | Create FastAPI app instance with title, description, version | `main.py` |
| T046 | Add CORS middleware allowing frontend origin | `main.py` |
| T047 | Register auth router at `/api/v1/auth` prefix | `main.py` |
| T048 | Register tasks router at `/api/v1/tasks` prefix | `main.py` |
| T049 | Register exception handlers from exceptions.py | `main.py` |
| T050 | Add startup validation for DATABASE_URL and BETTER_AUTH_SECRET | `main.py` |
| T051 | Verify routes/__init__.py exports both routers | `routes/__init__.py` |

### Implementation Details

```python
# main.py structure
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, close_db
from exceptions import register_exception_handlers
from routes import auth_router, tasks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not configured")
    if not settings.better_auth_secret:
        raise RuntimeError("BETTER_AUTH_SECRET not configured")

    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="Hackathon Todo API",
    description="Phase II Todo Application Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.better_auth_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
```

### Checkpoint
- Server starts with `uvicorn main:app --reload --port 8000`
- Swagger docs available at `/docs`
- All routes accessible under `/api/v1/`

---

## Phase 9: Polish & Verification

**Goal**: Add tests and verify all acceptance scenarios

### Tasks

| ID | Description | File |
|----|-------------|------|
| T052 | Create async test fixtures and test database setup | `tests/conftest.py` |
| T053 | Create auth tests (register, login, JWT validation) | `tests/test_auth.py` |
| T054 | Create task CRUD tests with user isolation | `tests/test_tasks.py` |
| T055 | Verify all acceptance scenarios from spec.md | Manual |
| T056 | Verify multi-user isolation | Manual |
| T057 | Verify 401/404 behavior (no 403 exposure) | Manual |
| T058 | Run quickstart.md curl commands | Manual |
| T059 | Update backend/CLAUDE.md if needed | `CLAUDE.md` |

### Test Structure

```
backend/tests/
├── conftest.py      # Fixtures: async client, test DB, test user
├── test_auth.py     # Registration, login, JWT tests
└── test_tasks.py    # CRUD + user isolation tests
```

### Key Test Cases

**Auth Tests (test_auth.py)**:
- Register new user → 201 + JWT
- Register duplicate email → 409
- Login valid credentials → 200 + JWT
- Login wrong password → 401
- Login non-existent user → 401

**Task Tests (test_tasks.py)**:
- Create task with JWT → 201
- Create task without JWT → 401
- List user's tasks only (isolation)
- Get task by ID → 200
- Get other user's task → 404 (not 403)
- Update task → 200 + updated_at changed
- Patch task partial → only changed fields update
- Delete task → 204
- Delete other user's task → 404

### Verification Commands

```bash
# Start server
cd backend
uv run uvicorn main:app --reload --port 8000

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Create task (use token from login)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"title": "Test task"}'

# List tasks
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <TOKEN>"

# Delete task
curl -X DELETE http://localhost:8000/api/v1/tasks/<TASK_ID> \
  -H "Authorization: Bearer <TOKEN>"

# Run tests
uv run pytest -v
```

### Checkpoint
- All tests pass
- API responds correctly to curl commands
- Multi-user isolation verified
- Documentation updated

---

## Execution Order

```
Phase 7 (Delete endpoint)
    ↓
Phase 8 (main.py assembly)
    ↓
Phase 9 (Tests & verification)
```

**Note**: Phase 8 must complete before Phase 9 verification, as we need a running server to test.

---

## Files to Create/Modify

### Phase 7
- `backend/routes/tasks.py` - Add DELETE endpoint

### Phase 8
- `backend/main.py` - **CREATE** (new file)
- `backend/routes/__init__.py` - Verify exports

### Phase 9
- `backend/tests/conftest.py` - **CREATE**
- `backend/tests/test_auth.py` - **CREATE**
- `backend/tests/test_tasks.py` - **CREATE**
- `backend/CLAUDE.md` - Update if needed

---

## Success Criteria

- [ ] DELETE /api/v1/tasks/{id} returns 204
- [ ] Server starts without errors
- [ ] All routes registered under /api/v1
- [ ] CORS allows frontend origin
- [ ] Exception handlers return consistent error format
- [ ] All pytest tests pass
- [ ] Quickstart curl commands work
- [ ] Multi-user isolation verified
