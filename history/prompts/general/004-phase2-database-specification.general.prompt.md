---
id: 004
title: Phase II Database Specification
stage: general
date: 2026-01-13
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: nida.nasarr
command: /sp.specify
labels: ["database", "postgresql", "neon", "sqlmodel", "schema", "phase2"]
links:
  spec: specs/database/schema.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/database/schema.md
tests:
  - null
---

## Prompt

/sp.specify # Database Specification — Phase II

## Purpose
Define the persistent data model for Phase II, ensuring reliable
storage, strict user isolation, and compatibility with FastAPI + SQLModel.

---

## Database Engine

- Provider: Neon
- Type: Serverless PostgreSQL
- Connection via: `DATABASE_URL`
- Async driver required

---

## Design Principles

- All data scoped by `user_id`
- No shared or global task records
- Referential integrity enforced
- Schema optimized for CRUD, not analytics

---

## Tables

### Users Table
| Column | Type | Constraints |
|------|------|-------------|
| id | UUID | Primary Key |
| email | TEXT | Unique, not null |
| hashed_password | TEXT | Not null |
| created_at | TIMESTAMP | Default now() |

### Tasks Table
| Column | Type | Constraints |
|------|------|-------------|
| id | UUID | Primary Key |
| user_id | UUID | Foreign Key → users.id |
| title | TEXT | Not null |
| description | TEXT | Nullable |
| completed | BOOLEAN | Default false |
| created_at | TIMESTAMP | Default now() |
| updated_at | TIMESTAMP | Auto-updated |

Indexes:
- `(user_id)`
- `(user_id, completed)`

---

## Relationships

- One user → many tasks
- Tasks **must** reference exactly one user
- Cascading delete allowed (user → tasks)

---

## ORM Mapping

- SQLModel used for all models
- Models must:
  - Be type-safe
  - Match schema exactly
  - Use UUID primary keys

---

## Data Access Rules

- All queries must include `user_id` filter
- No cross-user joins
- No raw SQL unless unavoidable

---

## Migration Strategy

- SQLModel metadata-based migrations
- No destructive migrations in Phase II
- Schema changes require spec updates

---

## Phase II Constraints

- No soft deletes
- No audit logs
- No task history tracking

---

## Database Acceptance Criteria

- Data persists across restarts
- Tasks are always user-scoped
- Schema aligns with SQLModel models
- Violations rejected at DB or API level

## Response snapshot

Completely rewrote `specs/database/schema.md` with comprehensive Phase II database specification including:

**Database Engine**:
- Neon Serverless PostgreSQL configuration
- asyncpg async driver
- Connection pool settings (pool_size=5, max_overflow=10, pool_recycle=1800s)
- Connection string format

**Design Principles Table**:
- User isolation, no shared records, referential integrity, CRUD optimization, type safety

**Schema Overview**:
- Visual diagram showing users and tasks tables with constraints

**Tables**:
- Users: id (UUID PK), email (TEXT UQ), hashed_password (TEXT), created_at (TIMESTAMPTZ)
- Tasks: id (UUID PK), user_id (UUID FK), title (TEXT), description (TEXT?), completed (BOOLEAN), created_at, updated_at (TIMESTAMPTZ)
- Complete SQL DDL for both tables
- Trigger for auto-updating `updated_at`

**Indexes**:
- idx_users_email (UNIQUE B-tree)
- idx_tasks_user_id (B-tree)
- idx_tasks_user_completed (composite B-tree)
- idx_tasks_user_created (composite B-tree DESC)
- Query patterns with expected performance (O(log n))

**Relationships**:
- Entity Relationship Diagram
- Rules: 1:N, NOT NULL FK, CASCADE DELETE, no orphans

**ORM Mapping (SQLModel)**:
- Complete User model with type hints
- Complete Task model with type hints
- Pydantic schemas: UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

**Data Access Rules**:
- Query patterns (MUST follow)
- Complete TaskRepository class with async methods
- Anti-patterns section (what NEVER to do)

**Database Session Management**:
- Async session factory with connection pooling
- Transaction pattern example

**Migration Strategy**:
- Alembic approach (forward-only in Phase II)
- Complete initial migration script

**Phase II Constraints**:
- Not implemented: soft deletes, audit logs, task history, full-text search
- Data limits: 1000 tasks/user, 500 char title, 5000 char description

**Functional Requirements**: 12 requirements (FR-DB-001 through FR-DB-012)

**Acceptance Criteria**: 16 checkboxes (AC-DB-001 through AC-DB-016)

## Outcome

- ✅ Impact: Complete database specification defining schema, ORM mapping, access patterns, and constraints
- 🧪 Tests: N/A (specification document)
- 📁 Files: specs/database/schema.md (rewritten)
- 🔁 Next prompts: `/sp.plan` for implementation plan, `/sp.tasks` for task breakdown
- 🧠 Reflection: Spec provides implementation-ready SQLModel code; anti-patterns section prevents common security mistakes

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - specification document
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding database testing patterns section for pytest integration
