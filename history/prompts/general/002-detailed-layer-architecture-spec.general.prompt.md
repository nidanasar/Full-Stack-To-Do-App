---
id: 002
title: Detailed Layer Architecture Specification
stage: general
date: 2026-01-13
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: nida.nasarr
command: /sp.specify
labels: ["architecture", "phase2", "frontend", "backend", "database", "authentication"]
links:
  spec: specs/architecture.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/architecture.md
tests:
  - null
---

## Prompt

/sp.specify ---

## Frontend Architecture

- Next.js App Router
- Server Components for data fetching
- Client Components for forms and interactivity
- Auth session stored via Better Auth
- API calls include `Authorization: Bearer <jwt>`

Responsibilities:
- UI rendering
- Auth flow (signup/login/logout)
- Input validation (client-side only)
- No business logic

---

## Backend Architecture

- FastAPI (async)
- SQLModel for ORM + typing
- JWT validation middleware
- User-scoped routing

Responsibilities:
- Auth verification
- Business logic
- Task CRUD
- Data validation (Pydantic)
- Authorization enforcement

---

## Database Architecture

- Neon Serverless PostgreSQL
- Tables:
  - `users`
  - `tasks`
- Tasks always linked to `user_id`
- No cross-user joins allowed

---

## Authentication Flow

1. User logs in via frontend
2. Better Auth issues JWT
3. JWT sent with every API request
4. Backend validates:
   - Token signature
   - Token expiry
   - `token.sub == path user_id`
5. Request allowed or rejected

---

## Data Flow Example (Create Task)

1. User submits form
2. Frontend sends POST `/api/{user_id}/tasks`
3. Backend validates JWT
4. Task inserted with `user_id`
5. Response returned to UI

---

## Scalability & Phase III Readiness

- Stateless backend
- JWT-based auth
- Database-driven persistence
- AI agent can reuse APIs without changes

---

## Non-Goals

- GraphQL
- Microservices
- Background workers
- AI inference in Phase II

---

## Architecture Acceptance Criteria

- Clear separation of concerns
- Backend fully independent of frontend
- All user data scoped by JWT
- No direct DB access from frontend

## Response snapshot

Extended `specs/architecture.md` (v1.0.0 → v1.1.0) with comprehensive layer architecture details:

**Frontend Architecture**:
- Component model diagram (Server/Client Components → Better Auth → API Client)
- Rendering strategy table (Server Components for data, Client Components for interactivity)
- Responsibilities matrix (owned vs not owned)
- Key patterns (no direct DB access, all calls include Bearer token)

**Backend Architecture**:
- Layer structure diagram (API → Middleware → Service → Data layers)
- Responsibilities matrix (JWT validation, business logic, authorization)
- User-scoped routing code example (dependency injection pattern)
- Validation layers table (Pydantic, Business Rules, Authorization)

**Database Architecture**:
- Schema design diagram with constraints
- Data isolation rules table (foreign key, WHERE clauses, cascade delete)
- Index definitions for performance

**Authentication Flow**:
- 12-step detailed sequence diagram (User → Frontend → Backend → Neon)
- JWT validation rules table with failure responses

**Data Flow Examples**:
- Create Task flow (6 steps with SQL insert)
- Get Tasks flow showing user isolation (User A vs User B)

**Scalability & Phase III**:
- Architecture qualities table with Phase III benefits
- Extension points diagram showing AI agent compatibility

**Non-Goals**: GraphQL, Microservices, Background Workers, AI Inference, WebSockets, File Attachments, Mobile Apps

**Acceptance Criteria**: 12 checkboxes across Separation of Concerns, Security & Isolation, and Independence categories

## Outcome

- ✅ Impact: Architecture spec extended from high-level to detailed layer-by-layer documentation
- 🧪 Tests: N/A (documentation update)
- 📁 Files: specs/architecture.md (updated, v1.1.0)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, `/sp.tasks` to break down into implementable tasks
- 🧠 Reflection: Detailed architecture provides clear implementation guidance; acceptance criteria enable verification

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - specification document
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider creating separate spec files for each layer if architecture.md grows too large
