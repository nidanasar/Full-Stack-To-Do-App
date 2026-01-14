# Tasks: Backend API Implementation

**Input**: Design documents from `/specs/001-backend-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not explicitly requested in spec - test tasks included in final polish phase for verification.

**Organization**: Tasks grouped by user story priority. Auth (US5) is foundational since all task operations require JWT.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1-US5 maps to user stories from spec.md
- All paths relative to `backend/` directory

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize FastAPI project structure and dependencies

- [ ] T001 Create backend project structure per plan.md in backend/
- [ ] T002 Create pyproject.toml with dependencies: fastapi, uvicorn, sqlmodel, asyncpg, python-jose, passlib[bcrypt], pydantic[email-validator], python-multipart in backend/pyproject.toml
- [ ] T003 [P] Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, ENVIRONMENT in backend/.env.example
- [ ] T004 [P] Create .gitignore for Python/backend in backend/.gitignore

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create config.py with Settings class using pydantic-settings for DATABASE_URL, BETTER_AUTH_SECRET in backend/config.py
- [ ] T006 Create database.py with async engine, AsyncSession factory, connection pool settings (5 pool, 10 overflow, 30s timeout) in backend/database.py
- [ ] T007 [P] Create User SQLModel in backend/models.py per data-model.md (id, email, hashed_password, created_at)
- [ ] T008 [P] Create Task SQLModel in backend/models.py per data-model.md (id, user_id FK, title, description, completed, timestamps)
- [ ] T009 Create exceptions.py with ErrorResponse format and custom exception handlers (401, 404, 409, 422) in backend/exceptions.py
- [ ] T010 [P] Create auth.py with password_hash() and password_verify() using bcrypt in backend/auth.py
- [ ] T011 Create auth.py with create_access_token() generating JWT with sub, exp, iat claims in backend/auth.py
- [ ] T012 Create auth.py with verify_token() validating JWT signature and expiration in backend/auth.py
- [ ] T013 Create dependencies.py with get_db() async session dependency in backend/dependencies.py
- [ ] T014 Create dependencies.py with get_current_user() extracting user_id from JWT sub claim in backend/dependencies.py

**Checkpoint**: Foundation ready - auth and task story implementation can begin

---

## Phase 3: User Story 5 - User Registration & Login (Priority: P1) MVP

**Goal**: Enable visitors to register and login to receive JWT for protected endpoints

**Independent Test**: Register new user, login with credentials, verify valid JWT returned

### Schemas for US5

- [ ] T015 [P] [US5] Create UserCreate schema (email: EmailStr, password: min 8 chars) in backend/schemas.py
- [ ] T016 [P] [US5] Create UserResponse schema (id, email, created_at) in backend/schemas.py
- [ ] T017 [P] [US5] Create AuthResponse schema (user: UserResponse, token: str) in backend/schemas.py
- [ ] T018 [P] [US5] Create LoginRequest schema (email, password) in backend/schemas.py

### Implementation for US5

- [ ] T019 [US5] Create routes/__init__.py with router imports in backend/routes/__init__.py
- [ ] T020 [US5] Implement POST /auth/register - validate email/password, hash password, create user, return JWT in backend/routes/auth.py
- [ ] T021 [US5] Implement POST /auth/login - find user by email, verify password hash, return JWT in backend/routes/auth.py
- [ ] T022 [US5] Add 409 Conflict error for duplicate email registration in backend/routes/auth.py
- [ ] T023 [US5] Add 401 Unauthorized with generic "Invalid credentials" for wrong password in backend/routes/auth.py

**Checkpoint**: Users can register and login - JWT available for task operations

---

## Phase 4: User Story 1 - Secure Task Creation (Priority: P1)

**Goal**: Authenticated users can create tasks associated with their account

**Independent Test**: POST /api/v1/tasks with valid JWT, verify 201 with task data and correct user_id

### Schemas for US1

- [ ] T024 [P] [US1] Create TaskCreate schema (title: 1-500 chars, description: optional max 5000) in backend/schemas.py
- [ ] T025 [P] [US1] Create TaskResponse schema (id, user_id, title, description, completed, timestamps) in backend/schemas.py

### Implementation for US1

- [ ] T026 [US1] Implement POST /api/v1/tasks - create task with user_id from JWT sub claim in backend/routes/tasks.py
- [ ] T027 [US1] Add JWT authentication dependency to POST /tasks endpoint in backend/routes/tasks.py
- [ ] T028 [US1] Add 422 validation for empty/invalid title in backend/routes/tasks.py
- [ ] T029 [US1] Add 401 Unauthorized for missing/invalid JWT in backend/routes/tasks.py

**Checkpoint**: Authenticated users can create tasks - US1 independently testable

---

## Phase 5: User Story 2 - Task Listing with Filtering (Priority: P1)

**Goal**: Authenticated users can list their tasks with optional filtering

**Independent Test**: Create tasks, GET /api/v1/tasks, verify only user's tasks returned with user isolation

### Schemas for US2

- [ ] T030 [P] [US2] Create TaskListResponse schema (tasks: list[TaskResponse]) in backend/schemas.py

### Implementation for US2

- [ ] T031 [US2] Implement GET /api/v1/tasks - list tasks filtered by user_id from JWT in backend/routes/tasks.py
- [ ] T032 [US2] Add optional completed query parameter filter in backend/routes/tasks.py
- [ ] T033 [US2] Add optional sort and order query parameters in backend/routes/tasks.py
- [ ] T034 [US2] Enforce user isolation - WHERE user_id = current_user.id on all queries in backend/routes/tasks.py

**Checkpoint**: Users can view their task list - US2 independently testable

---

## Phase 6: User Story 3 - Task Update (Priority: P2)

**Goal**: Authenticated users can update their task's title, description, or completion status

**Independent Test**: Create task, PUT/PATCH with modified data, verify changes persist with updated_at

### Schemas for US3

- [ ] T035 [P] [US3] Create TaskUpdate schema (title, description, completed - all required) in backend/schemas.py
- [ ] T036 [P] [US3] Create TaskPatch schema (title, description, completed - all optional) in backend/schemas.py

### Implementation for US3

- [ ] T037 [US3] Implement GET /api/v1/tasks/{task_id} - get single task with ownership check in backend/routes/tasks.py
- [ ] T038 [US3] Implement PUT /api/v1/tasks/{task_id} - full update with ownership check in backend/routes/tasks.py
- [ ] T039 [US3] Implement PATCH /api/v1/tasks/{task_id} - partial update with ownership check in backend/routes/tasks.py
- [ ] T040 [US3] Return 404 Not Found when task doesn't exist OR belongs to different user in backend/routes/tasks.py
- [ ] T041 [US3] Auto-update updated_at timestamp on modifications in backend/routes/tasks.py

**Checkpoint**: Users can update their tasks - US3 independently testable

---

## Phase 7: User Story 4 - Task Deletion (Priority: P2)

**Goal**: Authenticated users can delete their tasks

**Independent Test**: Create task, DELETE /api/v1/tasks/{task_id}, verify 204 and task removed

### Implementation for US4

- [ ] T042 [US4] Implement DELETE /api/v1/tasks/{task_id} - delete with ownership check in backend/routes/tasks.py
- [ ] T043 [US4] Return 204 No Content on successful deletion in backend/routes/tasks.py
- [ ] T044 [US4] Return 404 Not Found when task doesn't exist OR belongs to different user in backend/routes/tasks.py

**Checkpoint**: Users can delete their tasks - US4 independently testable

---

## Phase 8: App Assembly

**Purpose**: Wire up FastAPI app with all components

- [ ] T045 Create main.py with FastAPI app instance, title, description, version in backend/main.py
- [ ] T046 Add CORS middleware configuration allowing frontend origin in backend/main.py
- [ ] T047 Register auth router at /api/v1/auth prefix in backend/main.py
- [ ] T048 Register tasks router at /api/v1/tasks prefix in backend/main.py
- [ ] T049 Register exception handlers from exceptions.py in backend/main.py
- [ ] T050 Add startup validation for DATABASE_URL and BETTER_AUTH_SECRET in backend/main.py
- [ ] T051 [P] Create routes/__init__.py exporting auth_router and tasks_router in backend/routes/__init__.py

**Checkpoint**: Full API assembled and runnable with `uvicorn main:app --reload`

---

## Phase 9: Polish & Verification

**Purpose**: Final verification and cross-cutting concerns

- [ ] T052 [P] Create tests/conftest.py with async test fixtures and test database setup in backend/tests/conftest.py
- [ ] T053 [P] Create tests/test_auth.py with registration, login, JWT validation tests in backend/tests/test_auth.py
- [ ] T054 [P] Create tests/test_tasks.py with CRUD tests and user isolation verification in backend/tests/test_tasks.py
- [ ] T055 Verify all acceptance scenarios from spec.md pass
- [ ] T056 Verify multi-user isolation - User A cannot see User B's tasks
- [ ] T057 Verify 401/404 behavior matches spec (no 403 exposure)
- [ ] T058 Run quickstart.md validation with curl commands
- [ ] T059 Update backend/CLAUDE.md with implementation notes if needed

**Checkpoint**: All tasks complete, API verified against specification

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3-7 (User Stories) → Phase 8 (Assembly) → Phase 9 (Polish)
                                               ↓
                           US5 must complete before US1-4 (auth required)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US5 (Auth) | Phase 2 only | None - must be first |
| US1 (Create) | US5 | US2 |
| US2 (List) | US5 | US1 |
| US3 (Update) | US5, US1 | US4 |
| US4 (Delete) | US5, US1 | US3 |

### Within Each Phase

- Tasks marked [P] can run in parallel
- Schema tasks ([P]) can run in parallel
- Implementation tasks are sequential within their story

---

## Parallel Opportunities

### Phase 1 Parallel
```
T003: .env.example  }
T004: .gitignore    } → Run together
```

### Phase 2 Parallel
```
T007: User model     }
T008: Task model     }
T010: Password hash  } → Run together (different functions/sections)
```

### Phase 3 (US5) Parallel
```
T015: UserCreate    }
T016: UserResponse  }
T017: AuthResponse  } → Run together (all schemas)
T018: LoginRequest  }
```

### Phase 4-7 Cross-Story
```
After US5 completes:
US1 and US2 can proceed in parallel
After US1 completes:
US3 and US4 can proceed in parallel
```

---

## Implementation Strategy

### MVP First (US5 + US1 + US2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US5 (Auth) - **Users can register/login**
4. Complete Phase 4: US1 (Create) - **Users can create tasks**
5. Complete Phase 5: US2 (List) - **Users can view tasks**
6. **STOP and VALIDATE**: Test core functionality
7. Deploy MVP if needed

### Full Implementation

Continue with:
8. Complete Phase 6: US3 (Update)
9. Complete Phase 7: US4 (Delete)
10. Complete Phase 8: App Assembly
11. Complete Phase 9: Polish & Verification

### Single Developer Sequence

```
T001-T004 (Setup) → T005-T014 (Foundation) → T015-T023 (US5) → T024-T029 (US1) → T030-T034 (US2) → T035-T041 (US3) → T042-T044 (US4) → T045-T051 (Assembly) → T052-T059 (Polish)
```

---

## Task Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Phase 1: Setup | 4 | 2 |
| Phase 2: Foundational | 10 | 4 |
| Phase 3: US5 Auth | 9 | 4 |
| Phase 4: US1 Create | 6 | 2 |
| Phase 5: US2 List | 5 | 1 |
| Phase 6: US3 Update | 7 | 2 |
| Phase 7: US4 Delete | 3 | 0 |
| Phase 8: Assembly | 7 | 1 |
| Phase 9: Polish | 8 | 3 |
| **Total** | **59** | **19** |

---

## Notes

- All task endpoints require JWT validation (get_current_user dependency)
- User ID MUST come from JWT sub claim, NEVER from request
- Return 404 (not 403) for "wrong user" scenarios to prevent enumeration
- Use async/await for all database operations
- Commit after each task or logical group
- Test each user story independently before proceeding
