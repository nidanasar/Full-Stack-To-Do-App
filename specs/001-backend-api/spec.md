# Feature Specification: Backend API Implementation

**Feature Branch**: `001-backend-api`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "Backend Specification — Phase II (Full-Stack Todo) - FastAPI REST API with JWT auth, SQLModel ORM, Neon PostgreSQL, async sessions, user-scoped task CRUD"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Task Creation (Priority: P1)

As an authenticated user, I can create a new task through the API so that it is securely stored and associated with my account.

**Why this priority**: Task creation is the foundational operation. Without it, no other CRUD operations have meaning. This story validates authentication, database connectivity, and the core data model.

**Independent Test**: Can be fully tested by sending a POST request with valid JWT to `/api/v1/tasks` with title/description and verifying the task is created with the correct user_id from the JWT.

**Acceptance Scenarios**:

1. **Given** I am authenticated with a valid JWT, **When** I POST to `/api/v1/tasks` with `{"title": "Buy groceries", "description": "Milk, eggs, bread"}`, **Then** I receive 201 Created with the task data including my user_id, auto-generated id, and timestamps
2. **Given** I send a request without an Authorization header, **When** I POST to `/api/v1/tasks`, **Then** I receive 401 Unauthorized with error code "UNAUTHORIZED"
3. **Given** I send an expired JWT, **When** I POST to `/api/v1/tasks`, **Then** I receive 401 Unauthorized

---

### User Story 2 - Task Listing with Filtering (Priority: P1)

As an authenticated user, I can retrieve all my tasks so that I can view my task list, optionally filtered by completion status.

**Why this priority**: Viewing tasks is equally critical as creating them. This validates user isolation (only seeing own tasks) and basic query filtering.

**Independent Test**: Can be tested by creating multiple tasks and calling GET `/api/v1/tasks` with and without `completed` filter, verifying only the authenticated user's tasks are returned.

**Acceptance Scenarios**:

1. **Given** I have 5 tasks (3 pending, 2 completed), **When** I GET `/api/v1/tasks`, **Then** I receive all 5 tasks belonging to me
2. **Given** I have 5 tasks, **When** I GET `/api/v1/tasks?completed=true`, **Then** I receive only my 2 completed tasks
3. **Given** another user has 10 tasks, **When** I GET `/api/v1/tasks` with my JWT, **Then** I see only my tasks (user isolation enforced)

---

### User Story 3 - Task Update (Priority: P2)

As an authenticated user, I can update my task's title, description, or completion status so that I can modify task details as needed.

**Why this priority**: Modification follows creation and viewing. This validates ownership checks and partial updates.

**Independent Test**: Can be tested by creating a task, then calling PUT/PATCH with modified data and verifying the changes persist.

**Acceptance Scenarios**:

1. **Given** I have a task with id "abc-123", **When** I PUT to `/api/v1/tasks/abc-123` with updated data, **Then** the task is fully updated and returned with new `updated_at` timestamp
2. **Given** I have a pending task, **When** I PATCH with `{"completed": true}`, **Then** only the completed field changes while other fields remain unchanged
3. **Given** another user owns task "xyz-789", **When** I PUT to `/api/v1/tasks/xyz-789`, **Then** I receive 404 Not Found (not 403, to prevent enumeration)

---

### User Story 4 - Task Deletion (Priority: P2)

As an authenticated user, I can delete my task so that I can remove completed or unwanted tasks.

**Why this priority**: Deletion completes the CRUD operations. Validates ownership before delete.

**Independent Test**: Can be tested by creating a task, deleting it via DELETE endpoint, and verifying it no longer appears in task list.

**Acceptance Scenarios**:

1. **Given** I have a task with id "abc-123", **When** I DELETE `/api/v1/tasks/abc-123`, **Then** I receive 204 No Content and the task no longer exists
2. **Given** I try to delete a non-existent task, **When** I DELETE `/api/v1/tasks/fake-id`, **Then** I receive 404 Not Found
3. **Given** another user owns task "xyz-789", **When** I DELETE `/api/v1/tasks/xyz-789`, **Then** I receive 404 Not Found

---

### User Story 5 - User Registration & Login (Priority: P1)

As a visitor, I can register and login so that I receive a JWT to access protected endpoints.

**Why this priority**: Authentication is required before any task operations can be performed. Core prerequisite.

**Independent Test**: Can be tested by registering a new user, then logging in with those credentials and verifying a valid JWT is returned.

**Acceptance Scenarios**:

1. **Given** I am a new visitor, **When** I POST to `/api/v1/auth/register` with valid email/password, **Then** I receive 201 Created with user data and JWT
2. **Given** I have an account, **When** I POST to `/api/v1/auth/login` with correct credentials, **Then** I receive 200 OK with user data and JWT
3. **Given** I submit duplicate email on registration, **When** I POST to `/api/v1/auth/register`, **Then** I receive 409 Conflict with "Email already registered"
4. **Given** I submit wrong password, **When** I POST to `/api/v1/auth/login`, **Then** I receive 401 Unauthorized with generic "Invalid credentials" message

---

### Edge Cases

- What happens when a user submits an empty title? → 422 Unprocessable Entity with validation error
- What happens when title exceeds 500 characters? → 422 Unprocessable Entity with validation error
- What happens when task_id is not a valid UUID? → 422 Unprocessable Entity
- How does system handle malformed JSON in request body? → 400 Bad Request
- What happens when database connection fails? → 500 Internal Server Error with logged details
- What happens when JWT secret is misconfigured? → Application fails to start (startup validation)
- How does system handle concurrent updates to the same task? → Last write wins (standard PostgreSQL behavior)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate JWT on all endpoints except `/auth/register` and `/auth/login`
- **FR-002**: System MUST extract user_id from JWT `sub` claim, never from request body or URL
- **FR-003**: System MUST filter all task queries by the authenticated user's ID
- **FR-004**: System MUST provide POST `/api/v1/tasks` for task creation
- **FR-005**: System MUST provide GET `/api/v1/tasks` for listing tasks with optional `completed` filter
- **FR-006**: System MUST provide GET `/api/v1/tasks/{task_id}` for retrieving single task
- **FR-007**: System MUST provide PUT `/api/v1/tasks/{task_id}` for full task update
- **FR-008**: System MUST provide PATCH `/api/v1/tasks/{task_id}` for partial task update
- **FR-009**: System MUST provide DELETE `/api/v1/tasks/{task_id}` for task deletion
- **FR-010**: System MUST return 404 (not 403) when accessing another user's task
- **FR-011**: System MUST hash passwords using bcrypt before storage
- **FR-012**: System MUST validate email format and password minimum length (8 chars) on registration
- **FR-013**: System MUST return consistent error response format: `{"error": {"code": "...", "message": "..."}}`
- **FR-014**: System MUST use async database sessions for all queries
- **FR-015**: System MUST auto-update `updated_at` timestamp on task modifications
- **FR-016**: System MUST validate task title is non-empty and <= 500 characters
- **FR-017**: System MUST validate description is <= 5000 characters if provided
- **FR-018**: System MUST return appropriate HTTP status codes (200, 201, 204, 400, 401, 404, 409, 422, 500)

### Key Entities

- **User**: Account holder with unique email, hashed password, and creation timestamp. Primary identifier for task ownership.
- **Task**: Work item belonging to a user, with title (required), optional description, completion status, and timestamps.
- **JWT Token**: Stateless authentication credential containing user ID (`sub`), expiration (`exp`), and issued-at (`iat`) claims.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authenticated users can complete task creation in under 500ms (p95)
- **SC-002**: Task list retrieval returns results in under 200ms for up to 100 tasks
- **SC-003**: 100% of task operations enforce user isolation (zero cross-user data access)
- **SC-004**: All protected endpoints reject unauthenticated requests with 401
- **SC-005**: Duplicate email registration is rejected with 409 (no duplicate accounts)
- **SC-006**: Password stored using bcrypt hash (never plaintext)
- **SC-007**: All API responses follow consistent JSON structure
- **SC-008**: System handles 50 concurrent authenticated users without degradation
- **SC-009**: Invalid JWT tokens are rejected before any database operation occurs
- **SC-010**: Task CRUD operations maintain data integrity (no orphan tasks, no missing timestamps)

## Assumptions

The following reasonable defaults were assumed based on the existing specs and industry standards:

1. **Authentication Method**: JWT with HS256 signing, 7-day expiration (per @specs/features/authentication.md)
2. **Database Provider**: Neon PostgreSQL with async driver (per @specs/database/schema.md)
3. **API Versioning**: `/api/v1` prefix for all endpoints (per @specs/api/rest-endpoints.md)
4. **Error Response Format**: Consistent `{"error": {"code": "", "message": ""}}` structure
5. **Connection Pooling**: 5 connections with max 10 overflow (serverless optimization)
6. **User Enumeration Protection**: 404 returned for both "not found" and "wrong user" scenarios
7. **Content-Type**: JSON only for all requests and responses

## Dependencies

- @specs/api/rest-endpoints.md - API contract this backend must implement
- @specs/database/schema.md - Database schema and models to use
- @specs/features/authentication.md - Authentication flows and JWT handling
- @specs/architecture.md - Overall system architecture

## Out of Scope (Phase II)

- Bulk operations (batch create/update/delete)
- Rate limiting
- Pagination (small data sets expected)
- Search/filter by title
- Refresh tokens
- OAuth providers
- Admin endpoints
- Audit logging
- Soft deletes

## References

- @specs/api/rest-endpoints.md - Complete API specification
- @specs/database/schema.md - Database tables and ORM models
- @specs/features/authentication.md - Auth flows and security requirements
- @.specify/memory/constitution.md - Project constitution and coding standards
