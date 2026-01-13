---
id: 001
title: Phase II Constitution Ratification
stage: constitution
date: 2025-01-13
surface: agent
model: claude-opus-4-5
feature: none
branch: main
user: nida.nasarr
command: /sp.constitution
labels: ["constitution", "phase2", "governance", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

# /constitution.md - Hackathon Todo Phase II

**Project**: Evolution of Todo – Mastering Spec-Driven Development & Cloud Native AI (Phase II: Full-Stack Web Application)

## Core Principles
- **Spec-Driven Development**: All implementations via Claude Code + Spec-Kit + subagents. Refine specs until output matches acceptance criteria exactly. Zero manual code writing.
- **Reusable Intelligence**: Modular subagents (@agents/) for backend/frontend/database/auth. Skills/blueprints saved for future phases (e.g., Kubernetes).
- **Multi-User Security & Isolation**: JWT auth (Better Auth + python-jose). Backend verifies path `user_id` == token `sub`; users see/modify only own tasks.
- **Cloud-Native Foundation**: Monorepo for single-context edits. Docker/Kafka/Dapr-ready. Neon Serverless Postgres for persistence.
- **Clean Architecture**: RESTful API, responsive UI (Tailwind mobile-first), SQLModel for type-safe DB.

## Key Standards
- **Spec Referencing**: Every Claude prompt starts with `@specs/file.md` + subagent activation. Update specs for changes; history in `/specs/history/phase2/`.
- **Code Quality**: PEP8 Python, ESLint/Prettier TS. Pydantic validation, async DB sessions.
- **Citation/Traceability**: Changes cite spec/commit SHA.
- **Version Control**: Main commits: "Subagent backend: CRUD endpoints".
- **Tech Stack Lock**: Next.js 16+ App Router, FastAPI, SQLModel, Neon Postgres, Better Auth

## Constraints
- Structure: Strict monorepo per @.spec-kit/config.yaml
- API: Endpoints `/api/v1/{resource}` w/ query params
- Features: Phase II basic CRUD only
- Env Vars: DATABASE_URL, BETTER_AUTH_SECRET, NEXTAUTH_URL
- No Bloat: <5s page loads, <100ms API

## Success Criteria
- Functional: docker-compose up → Signup → Tasks CRUD → Logout
- Secure: No token → 401; Wrong user_id → 404
- Spec Compliance: 100% acceptance criteria met
- Deployed: Vercel frontend, Neon backend
- Auditable: Subagent logs, PHR records

## Response snapshot

Created and ratified the Hackathon Todo Phase II Constitution v1.0.0 with:
- 5 Core Principles: Spec-Driven Development, Reusable Intelligence, Multi-User Security, Cloud-Native Foundation, Clean Architecture
- Key Standards: Code quality, tech stack lock, version control
- Constraints: Scope, performance, API patterns
- Success Criteria: Functional, security, compliance, deployment, audit
- Governance: Amendment procedure, compliance review, enforcement

File written to: `.specify/memory/constitution.md`

## Outcome

- Impact: Initial constitution ratified, establishes governance for Phase II
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md (created/updated)
- Next prompts: /sp.specify for features, /sp.plan for implementation
- Reflection: Constitution provides clear guardrails for spec-driven development

## Evaluation notes (flywheel)

- Failure modes observed: None - clean initial ratification
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor compliance during implementation
