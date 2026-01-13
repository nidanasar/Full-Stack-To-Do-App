<!--
SYNC IMPACT REPORT
==================
Version Change: 0.0.0 → 1.0.0 (MAJOR - initial ratification)
Modified Principles: None (initial version)
Added Sections:
  - Core Principles (5 principles)
  - Key Standards
  - Constraints
  - Success Criteria
  - Governance
Removed Sections: None
Templates Status:
  - .specify/templates/plan-template.md ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md ✅ Compatible (requirements align)
  - .specify/templates/tasks-template.md ✅ Compatible (phase structure aligns)
Follow-up TODOs: None
-->

# Hackathon Todo Phase II Constitution

**Project**: Evolution of Todo – Mastering Spec-Driven Development & Cloud Native AI (Phase II: Full-Stack Web Application)

## Core Principles

### I. Spec-Driven Development

All implementations MUST be executed via Claude Code + Spec-Kit + subagents. Specs MUST be refined until output matches acceptance criteria exactly. Zero manual code writing is permitted.

**Non-Negotiables**:
- Every Claude prompt MUST start with `@specs/file.md` + subagent activation
- Specs MUST be updated before implementing changes
- History MUST be maintained in `/specs/history/phase2/`
- Changes MUST cite spec/commit SHA (e.g., "Implemented per @specs/features/task-crud.md")

### II. Reusable Intelligence

Modular subagents (`@agents/`) MUST be used for backend, frontend, database, and auth operations. Skills and blueprints MUST be saved for future phases (e.g., Kubernetes, Phase III).

**Non-Negotiables**:
- Subagents MUST be organized in `.claude/agents/`
- Skills MUST be stored in `.claude/skills/`
- All changes MUST utilize reusable subagents
- Cloud blueprints MUST be extracted where applicable (e.g., Helm values.yaml)

### III. Multi-User Security & Isolation

JWT authentication (Better Auth + python-jose) MUST be implemented. Backend MUST verify path `user_id` matches token `sub` claim. Users MUST only see and modify their own tasks.

**Non-Negotiables**:
- No token → 401 Unauthorized
- Wrong user_id → 404 Not Found (prevents enumeration)
- Token expiry MUST be handled gracefully
- `user_id` MUST NEVER come from request body; ALWAYS from JWT
- All queries MUST filter by authenticated user's ID

### IV. Cloud-Native Foundation

Monorepo structure MUST be used for single-context edits. Architecture MUST be Docker/Kafka/Dapr-ready. Neon Serverless Postgres MUST be used for persistence.

**Non-Negotiables**:
- Strict monorepo structure per `.spec-kit/config.yaml`
- No external repositories permitted
- Environment variables: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `NEXTAUTH_URL=http://localhost:3000`
- Docker-compose MUST orchestrate all services

### V. Clean Architecture

RESTful API design MUST be followed. Responsive UI MUST use Tailwind CSS (mobile-first). SQLModel MUST be used for type-safe database operations.

**Non-Negotiables**:
- API endpoints: `/api/v1/{resource}` with query params (status/sort)
- Headers: `Authorization: Bearer <jwt>`
- Pydantic validation on all inputs
- Async database sessions
- <5s page loads, <100ms API response times
- No unnecessary dependencies

## Key Standards

### Code Quality

| Layer | Standard |
|-------|----------|
| Python | PEP8, type hints, Pydantic validation |
| TypeScript | ESLint, Prettier, strict mode |
| Database | SQLModel with async sessions |
| Testing | pytest (backend), vitest (frontend) |

### Tech Stack Lock

| Layer | Exact Technology |
|-------|------------------|
| Frontend | Next.js 16+ App Router, TypeScript, Tailwind CSS, Better Auth (JWT) |
| Backend | FastAPI, SQLModel, Neon Postgres |
| Auth | Shared `BETTER_AUTH_SECRET` |
| Dev | UV, docker-compose, Spec-Kit Plus |

### Version Control

- Main branch commits only (no feature branches for Phase II)
- Commit format: "Subagent [type]: [description]"
- Example: "Subagent backend: CRUD endpoints"

## Constraints

### Scope Constraints

- Phase II: Basic CRUD only (add, delete, update, view, mark-complete)
- Intermediate features (priorities, tags) reserved for bonus/Phase III
- No external repos; strict monorepo structure

### Performance Constraints

- Page loads: <5 seconds
- API responses: <100ms
- No bloat: minimal dependencies only

### API Constraints

- Endpoints follow `/api/v1/{resource}` pattern
- Query parameters for filtering (status, sort)
- JWT required in Authorization header for protected routes

## Success Criteria

### Functional Acceptance

- [ ] `docker-compose up` starts all services
- [ ] User can sign up and receive JWT
- [ ] User can perform full CRUD on tasks
- [ ] User can logout and session ends
- [ ] Multi-user isolation: User A cannot see User B's tasks

### Security Acceptance

- [ ] Missing token returns 401 Unauthorized
- [ ] Invalid/expired token returns 401 Unauthorized
- [ ] Accessing other user's resource returns 404 Not Found
- [ ] Token expiry handled gracefully (re-auth flow)

### Spec Compliance

- [ ] 100% acceptance criteria met per `@specs/features/*.md`
- [ ] All changes cite spec references

### Deployment Acceptance

- [ ] Vercel frontend link functional
- [ ] Backend connected to Neon Postgres
- [ ] Environment variables properly configured

### Auditability

- [ ] Subagent logs maintained in `specs/history/phase2/subagent-logs.md`
- [ ] Claude iterations visible and traceable
- [ ] PHR records created for significant changes

## Governance

### Amendment Procedure

1. Proposed changes MUST be documented with rationale
2. Changes MUST be reviewed against existing principles
3. Version MUST be incremented per semantic versioning:
   - MAJOR: Principle removal or redefinition
   - MINOR: New principle or expanded guidance
   - PATCH: Clarifications and typo fixes
4. Amendment date MUST be updated

### Compliance Review

- All PRs/reviews MUST verify constitution compliance
- Complexity MUST be justified if Constitution Check fails
- Claude Code MUST reject violations
- Pre-submit validation: `npm run lint && uv run pytest && curl tests`

### Enforcement

This constitution supersedes all other practices. Non-compliance MUST be flagged and resolved before merge.

**Version**: 1.0.0 | **Ratified**: 2025-01-13 | **Last Amended**: 2025-01-13
