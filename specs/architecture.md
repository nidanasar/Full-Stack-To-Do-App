# System Architecture — Phase II

**Version**: 1.1.0
**Last Updated**: 2026-01-13
**Status**: Ratified

## Overview

Phase II is a cloud-ready, monorepo-based full-stack web application supporting secure, multi-user Todo management via a REST API.

The system follows a **frontend–backend–database** separation with JWT-based authentication and strict user isolation.

---

## High-Level Architecture

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Client      │       │     Backend     │       │    Database     │
│    (Browser)    │──────▶│    (FastAPI)    │──────▶│ (Neon Postgres) │
│                 │◀──────│   JWT Auth      │◀──────│                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
        │                         │
        │    HTTPS / JSON         │
        ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│   Next.js App   │       │   Better Auth   │
│   (App Router)  │       │  (JWT Shared)   │
└─────────────────┘       └─────────────────┘
```

All communication occurs over HTTPS using JSON.

---

## Monorepo Structure

```
fullstack-app/
├── hackathon-todo/
│   ├── frontend/                 # Next.js 16+ App Router
│   │   ├── app/                  # App Router pages and layouts
│   │   │   ├── (auth)/           # Auth route group (login, signup)
│   │   │   ├── (dashboard)/      # Protected dashboard routes
│   │   │   ├── api/              # API routes (Better Auth)
│   │   │   └── layout.tsx        # Root layout
│   │   ├── components/           # Reusable UI components
│   │   ├── lib/                  # Utilities, auth client, API client
│   │   ├── styles/               # Global styles, Tailwind config
│   │   └── CLAUDE.md             # Frontend agent instructions
│   │
│   ├── backend/                  # FastAPI Python backend
│   │   ├── app/
│   │   │   ├── api/              # API routes
│   │   │   │   └── v1/           # Versioned endpoints
│   │   │   │       ├── auth.py   # Auth endpoints
│   │   │   │       └── tasks.py  # Task CRUD endpoints
│   │   │   ├── core/             # Config, security, dependencies
│   │   │   ├── models/           # SQLModel database models
│   │   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   └── services/         # Business logic layer
│   │   ├── main.py               # FastAPI app entry point
│   │   └── CLAUDE.md             # Backend agent instructions
│   │
│   ├── specs/                    # Specification documents
│   │   ├── overview.md
│   │   ├── architecture.md       # This file
│   │   ├── features/             # Feature specifications
│   │   ├── api/                  # API contracts
│   │   ├── database/             # Database schema
│   │   └── ui/                   # UI specifications
│   │
│   ├── .claude/                  # Claude Code configuration
│   │   ├── agents/               # Subagent definitions
│   │   ├── commands/             # Spec-Kit commands
│   │   └── skills/               # Reusable skill patterns
│   │
│   ├── .specify/                 # Spec-Kit Plus templates
│   │   ├── templates/            # Document templates
│   │   ├── scripts/              # Automation scripts
│   │   └── memory/               # Constitution and memory
│   │
│   ├── history/                  # Prompt History Records
│   │   └── prompts/              # PHR storage
│   │
│   ├── docker-compose.yml        # Container orchestration
│   └── CLAUDE.md                 # Monorepo agent instructions
```

---

## Technology Stack

### Frontend Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 16+ (App Router) | Server-side rendering, routing |
| Language | TypeScript (strict mode) | Type safety |
| Styling | Tailwind CSS | Utility-first responsive design |
| Auth Client | Better Auth | JWT session management |
| State | React useState/useContext | Local state management |
| HTTP Client | fetch API | API communication |

### Backend Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | Async REST API |
| Language | Python 3.11+ | Backend logic |
| ORM | SQLModel | Type-safe database operations |
| Validation | Pydantic | Request/response validation |
| Auth | python-jose + Better Auth | JWT verification |
| Password | passlib[bcrypt] | Secure password hashing |

### Database Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | Neon Serverless Postgres | Cloud-native persistence |
| Driver | asyncpg | Async database connections |
| Migrations | Alembic | Schema migrations |

### DevOps & Tooling

| Component | Technology | Purpose |
|-----------|------------|---------|
| Package Manager | UV (Python), npm (Node) | Dependency management |
| Containers | Docker, docker-compose | Local orchestration |
| Linting | ESLint, Prettier (TS), Ruff (Python) | Code quality |
| Testing | pytest (backend), vitest (frontend) | Test automation |

---

## Frontend Architecture

### Component Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js App Router                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │ Server Components│    │ Client Components│                │
│  │  (Data Fetching) │    │ (Interactivity)  │                │
│  └────────┬────────┘    └────────┬─────────┘                │
│           │                      │                           │
│           ▼                      ▼                           │
│  ┌─────────────────────────────────────────┐                │
│  │           Better Auth Client            │                │
│  │         (Session & JWT Storage)         │                │
│  └─────────────────────────────────────────┘                │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────┐                │
│  │     API Client (Authorization: Bearer)   │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Rendering Strategy

| Component Type | Use Case | Data Access |
|----------------|----------|-------------|
| Server Components | Static layouts, initial data fetch | Direct server-side |
| Client Components | Forms, buttons, interactive UI | Via API client |

### Responsibilities

| Responsibility | Owned | NOT Owned |
|----------------|-------|-----------|
| UI rendering | ✅ | |
| Auth flow (signup/login/logout) | ✅ | |
| Client-side input validation | ✅ | |
| JWT storage & transmission | ✅ | |
| Business logic | | ❌ |
| Data validation (authoritative) | | ❌ |
| Authorization decisions | | ❌ |

### Key Patterns

- **Server Components**: Used for layouts, page shells, and initial data hydration
- **Client Components**: Used for forms, modals, and any user interaction
- **API Calls**: All calls include `Authorization: Bearer <jwt>` header
- **Session**: Managed by Better Auth client library
- **No Direct DB Access**: Frontend NEVER connects to database directly

---

## Backend Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   API Layer (Routers)                │    │
│  │     /api/v1/auth/*        /api/v1/tasks/*           │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Middleware Layer                        │    │
│  │   JWT Validation │ CORS │ Error Handling            │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Service Layer (Business Logic)          │    │
│  │   AuthService │ TaskService │ UserService           │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Data Layer (SQLModel + Pydantic)        │    │
│  │   Models │ Schemas │ Database Sessions              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Responsibilities

| Responsibility | Owned | NOT Owned |
|----------------|-------|-----------|
| JWT validation & verification | ✅ | |
| Business logic | ✅ | |
| Task CRUD operations | ✅ | |
| Data validation (Pydantic) | ✅ | |
| Authorization enforcement | ✅ | |
| User-scoped data filtering | ✅ | |
| UI rendering | | ❌ |
| Session storage | | ❌ |

### User-Scoped Routing

All task endpoints are scoped by the authenticated user:

```python
# Dependency injection pattern
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract and validate user from JWT token."""
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    # All subsequent queries filtered by user_id
    return user_id

# Every task query includes user filter
async def get_tasks(user_id: UUID = Depends(get_current_user)):
    return await db.query(Task).filter(Task.user_id == user_id).all()
```

### Validation Layers

| Layer | Validation Type | Example |
|-------|-----------------|---------|
| Pydantic Schemas | Request shape, types | `title: str`, `completed: bool` |
| Business Rules | Domain logic | "Title cannot be empty" |
| Authorization | User ownership | `task.user_id == current_user.id` |

---

## Database Architecture

### Schema Design

```
┌─────────────────────────────────────────────────────────────┐
│                  Neon Serverless PostgreSQL                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐   │
│  │       users         │         │       tasks         │   │
│  ├─────────────────────┤         ├─────────────────────┤   │
│  │ id          UUID PK │◀────────│ user_id     UUID FK │   │
│  │ email    VARCHAR UK │   1:N   │ id          UUID PK │   │
│  │ password    VARCHAR │         │ title       VARCHAR │   │
│  │ created_at TIMESTAMP│         │ description    TEXT │   │
│  │ updated_at TIMESTAMP│         │ completed   BOOLEAN │   │
│  └─────────────────────┘         │ created_at TIMESTAMP│   │
│                                  │ updated_at TIMESTAMP│   │
│                                  └─────────────────────┘   │
│                                                              │
│  Constraints:                                                │
│  • users.email UNIQUE                                        │
│  • tasks.user_id REFERENCES users(id) ON DELETE CASCADE     │
│  • NO cross-user joins permitted in application code        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Isolation Rules

| Rule | Enforcement | Level |
|------|-------------|-------|
| Tasks belong to one user | Foreign key constraint | Database |
| Users can only access own tasks | WHERE user_id = ? | Application |
| No cross-user queries | Code review + testing | Application |
| Cascade delete on user removal | ON DELETE CASCADE | Database |

### Indexes

| Index | Column(s) | Purpose |
|-------|-----------|---------|
| Primary | users.id | User lookup |
| Unique | users.email | Login lookup, uniqueness |
| Foreign | tasks.user_id | User's task queries |
| Primary | tasks.id | Task lookup |

---

## Authentication Flow

### Detailed Sequence

```
┌────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐
│ User   │     │ Frontend │     │ Backend  │     │  Neon  │
│Browser │     │ Next.js  │     │ FastAPI  │     │Postgres│
└───┬────┘     └────┬─────┘     └────┬─────┘     └───┬────┘
    │               │                │               │
    │ 1. Login form │                │               │
    │──────────────▶│                │               │
    │               │                │               │
    │               │ 2. POST /auth/login            │
    │               │───────────────▶│               │
    │               │                │               │
    │               │                │ 3. Query user │
    │               │                │──────────────▶│
    │               │                │               │
    │               │                │ 4. User record│
    │               │                │◀──────────────│
    │               │                │               │
    │               │                │ 5. Verify     │
    │               │                │    password   │
    │               │                │    (bcrypt)   │
    │               │                │               │
    │               │ 6. JWT token   │               │
    │               │◀───────────────│               │
    │               │                │               │
    │ 7. Store JWT  │                │               │
    │    (cookie)   │                │               │
    │◀──────────────│                │               │
    │               │                │               │
    │ 8. API request│                │               │
    │   + Bearer JWT│                │               │
    │──────────────▶│───────────────▶│               │
    │               │                │               │
    │               │                │ 9. Validate:  │
    │               │                │  • Signature  │
    │               │                │  • Expiry     │
    │               │                │  • sub claim  │
    │               │                │               │
    │               │                │ 10. Query     │
    │               │                │    (scoped)   │
    │               │                │──────────────▶│
    │               │                │               │
    │               │                │ 11. Results   │
    │               │                │◀──────────────│
    │               │                │               │
    │               │ 12. Response   │               │
    │◀──────────────│◀───────────────│               │
```

### JWT Validation Rules

| Check | Failure Response | Purpose |
|-------|------------------|---------|
| Token present | 401 Unauthorized | Require authentication |
| Valid signature | 401 Unauthorized | Prevent tampering |
| Not expired | 401 Unauthorized | Session timeout |
| `sub` matches route user_id | 404 Not Found | Prevent enumeration |

---

## Data Flow Examples

### Create Task Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Create Task Flow                         │
└─────────────────────────────────────────────────────────────┘

1. User submits form
   ┌──────────────────────────────────────┐
   │ { "title": "Buy groceries",          │
   │   "description": "Milk, eggs, bread" }│
   └──────────────────────────────────────┘
                    │
                    ▼
2. Frontend sends POST /api/v1/tasks
   Headers: Authorization: Bearer <jwt>
   Body: { "title": "...", "description": "..." }
                    │
                    ▼
3. Backend validates JWT
   • Decode token
   • Verify signature with BETTER_AUTH_SECRET
   • Check expiry
   • Extract user_id from "sub" claim
                    │
                    ▼
4. Backend validates request body (Pydantic)
   • title: required, non-empty string
   • description: optional string
                    │
                    ▼
5. Task inserted with user_id
   INSERT INTO tasks (id, user_id, title, description, completed)
   VALUES (uuid, <jwt.sub>, 'Buy groceries', 'Milk...', false)
                    │
                    ▼
6. Response returned to UI
   201 Created
   { "id": "...", "title": "Buy groceries", ... }
```

### Get Tasks Flow (User Isolation)

```
User A (token.sub = "user-a-id")     User B (token.sub = "user-b-id")
            │                                    │
            ▼                                    ▼
    GET /api/v1/tasks                   GET /api/v1/tasks
    Bearer: <token-A>                   Bearer: <token-B>
            │                                    │
            ▼                                    ▼
    SELECT * FROM tasks                 SELECT * FROM tasks
    WHERE user_id = 'user-a-id'         WHERE user_id = 'user-b-id'
            │                                    │
            ▼                                    ▼
    Returns only A's tasks              Returns only B's tasks
    (3 tasks)                           (5 tasks)
```

---

## Scalability & Phase III Readiness

### Current Architecture Qualities

| Quality | Implementation | Phase III Benefit |
|---------|----------------|-------------------|
| Stateless Backend | No server-side sessions | Horizontal scaling |
| JWT-based Auth | Self-contained tokens | Distributed systems |
| Database-driven | Neon serverless | Auto-scaling storage |
| REST API | Standard HTTP/JSON | AI agent compatibility |

### Phase III Extension Points

```
Phase II (Current)              Phase III (Future)
┌─────────────────┐            ┌─────────────────┐
│  Next.js App    │            │  Next.js App    │
└────────┬────────┘            └────────┬────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│  FastAPI REST   │            │  FastAPI REST   │◀─── AI Agent
└────────┬────────┘            └────────┬────────┘     (same API)
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│  Neon Postgres  │            │  Neon Postgres  │
└─────────────────┘            │  + Vector Store │
                               └─────────────────┘
```

- AI agents can reuse REST APIs without changes
- Same authentication flow works for agent tokens
- Database can extend with vector columns for embeddings

---

## Non-Goals (Phase II Scope)

| Excluded | Rationale |
|----------|-----------|
| GraphQL | REST sufficient for CRUD; complexity not justified |
| Microservices | Monolith appropriate for team size and scope |
| Background Workers | No async jobs required for basic CRUD |
| AI Inference | Reserved for Phase III |
| Real-time (WebSockets) | Polling sufficient; out of scope |
| File Attachments | Not in Phase II requirements |
| Mobile Native Apps | Web-only for Phase II |

---

## Architecture Acceptance Criteria

### Separation of Concerns

- [ ] **AC-001**: Frontend contains NO business logic
- [ ] **AC-002**: Backend is fully functional without frontend
- [ ] **AC-003**: Database schema enforces referential integrity
- [ ] **AC-004**: Each layer can be tested independently

### Security & Isolation

- [ ] **AC-005**: All user data scoped by JWT `sub` claim
- [ ] **AC-006**: No direct database access from frontend
- [ ] **AC-007**: Invalid tokens return 401 Unauthorized
- [ ] **AC-008**: Wrong user access returns 404 Not Found

### Independence

- [ ] **AC-009**: Backend deployable without frontend
- [ ] **AC-010**: Frontend deployable without backend (shows auth error)
- [ ] **AC-011**: Database migrations reversible
- [ ] **AC-012**: No circular dependencies between layers

---

## References

- @specs/features/authentication.md - Auth feature specification
- @specs/features/task-crud.md - Task CRUD specification
- @specs/api/rest-endpoints.md - API contract
- @specs/database/schema.md - Database schema
- @.specify/memory/constitution.md - Project constitution
