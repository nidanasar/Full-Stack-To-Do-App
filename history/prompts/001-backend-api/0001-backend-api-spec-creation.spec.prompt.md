---
id: 0001
title: Backend API Spec Creation
stage: spec
date: 2026-01-13
surface: agent
model: claude-opus-4-5-20251101
feature: 001-backend-api
branch: 001-backend-api
user: nida.nasarr
command: /sp.specify
labels: ["backend", "api", "fastapi", "jwt", "crud"]
links:
  spec: specs/001-backend-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-backend-api/spec.md
  - specs/001-backend-api/checklists/requirements.md
tests:
  - null
---

## Prompt

# Backend Specification — Phase II (Full-Stack Todo)

## Purpose
Define the internal backend structure and behavior for Phase II, ensuring secure, scalable, and spec-driven implementation of the REST API and database interactions.

---

## Technology Stack
- Python 3.13+
- FastAPI (REST API framework)
- SQLModel (ORM)
- Neon Serverless PostgreSQL
- Pydantic (request/response validation)
- python-jose (JWT verification)
- Async DB sessions

---

## Project Structure
/backend
├── main.py # FastAPI app entry
├── models.py # SQLModel classes
├── routes/
│ ├── tasks.py # CRUD endpoints
│ └── auth.py # Auth logic
├── db.py # Database connection/session
├── dependencies.py # Common dependencies
├── middleware.py # JWT verification
└── utils.py # Helper functions

---

## Core Responsibilities
- Validate JWT (`Authorization: Bearer <jwt>`) on all endpoints
- Enforce `token.sub === user_id` for every request
- Filter all DB queries by `user_id` to ensure multi-user isolation
- Implement full CRUD for tasks (add, update, delete, view, mark complete)
- Handle errors using FastAPI `HTTPException` with proper status codes
- Use async database sessions for all queries
- Pydantic models for request/response validation
- Log all actions for audit (spec-driven subagent logs)

---

## Middleware
- JWT verification
- User isolation enforcement
- Error catching for auth and DB issues
- Attach `current_user` to request context

---

## Routes & Handlers
- **/api/{user_id}/tasks** → task CRUD operations
- **/api/{user_id}/tasks/{task_id}** → get/update/delete individual task
- **/auth/** → Better Auth integration, token verification

---

## Database Integration
- Async queries via SQLModel
- Map API inputs to models
- Ensure transactions commit or rollback on failure
- Apply all filtering and validation rules from API/database specs

---

## Validation Rules
- Title required, max 255 chars
- UUIDs validated
- Empty or invalid payloads rejected (400)
- Unauthorized or forbidden access handled (401/403)

---

## Security Constraints
- No JWT in URL or query params
- All DB operations filtered by `user_id`
- No sensitive data exposed
- HTTPS required in production

---

## Phase II Constraints
- Only basic CRUD features
- No bulk operations, no PATCH, no admin endpoints
- Must align exactly with API, frontend, and database specs

---

## Acceptance Criteria
- JWT enforced on all endpoints
- Only authenticated user can access their tasks
- Async DB sessions with error handling
- Full spec-driven implementation using subagents and skills
- Logs and Claude Code iterations visible for review

## Response snapshot

Created backend API specification at `specs/001-backend-api/spec.md` with:

1. **5 User Stories** (P1-P2 priority):
   - Secure Task Creation (P1)
   - Task Listing with Filtering (P1)
   - Task Update (P2)
   - Task Deletion (P2)
   - User Registration & Login (P1)

2. **18 Functional Requirements** (FR-001 to FR-018):
   - JWT validation on protected endpoints
   - User ID extraction from JWT sub claim
   - Full CRUD operations for tasks
   - Consistent error response format
   - Async database sessions

3. **10 Success Criteria** with measurable metrics:
   - Task creation under 500ms (p95)
   - Task list retrieval under 200ms
   - 100% user isolation enforcement
   - Zero cross-user data access

4. **Quality Validation**: All checklist items passed

## Outcome

- Impact: Created comprehensive backend API specification aligned with existing API, database, and authentication specs
- Tests: null
- Files: 2 files created (spec.md, requirements.md checklist)
- Next prompts: /sp.plan or /sp.clarify
- Reflection: Spec created without clarifications needed - all requirements derived from existing specs and user input

## Evaluation notes (flywheel)

- Failure modes observed: None - spec generation successful
- Graders run and results (PASS/FAIL): Quality checklist PASS (all 16 items)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
