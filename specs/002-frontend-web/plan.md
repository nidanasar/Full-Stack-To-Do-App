# Implementation Plan: Frontend Web Application

**Branch**: `002-frontend-web` | **Date**: 2026-01-15 | **Spec**: @specs/002-frontend-web/spec.md
**Input**: Feature specification from `/specs/002-frontend-web/spec.md`

## Summary

Build a Next.js 16+ frontend with App Router that provides user registration, login, and task CRUD operations. Uses Better Auth for JWT session management with httpOnly cookies, Tailwind CSS for mobile-first styling, and Server Components for optimal performance. All data comes from the FastAPI backend at localhost:8000.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 18+
**Primary Dependencies**: Next.js 16+, Better Auth, Tailwind CSS, Lucide React
**Storage**: N/A (API-backed)
**Testing**: vitest (if needed)
**Target Platform**: Web (desktop, tablet, mobile)
**Project Type**: Web application (frontend)
**Performance Goals**: <5s page loads, immediate optimistic updates
**Constraints**: httpOnly cookies only, no localStorage tokens
**Scale/Scope**: Single-user experience, ~100 tasks max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | All implementation from spec.md |
| II. Reusable Intelligence | ✅ PASS | Using frontend-web agent |
| III. Multi-User Security | ✅ PASS | JWT via httpOnly cookies, user isolation |
| IV. Cloud-Native Foundation | ✅ PASS | Monorepo structure, env vars |
| V. Clean Architecture | ✅ PASS | RESTful API, Tailwind mobile-first |

**Tech Stack Compliance**:
- [x] Next.js 16+ App Router - Required
- [x] TypeScript strict mode - Required
- [x] Tailwind CSS - Required
- [x] Better Auth (JWT) - Required
- [x] Lucide React icons - Chosen per research

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-web/
├── plan.md              # This file
├── research.md          # Phase 0 output (completed)
├── data-model.md        # Phase 1 output (completed)
├── quickstart.md        # Phase 1 output (completed)
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── tasks/
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── error.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Skeleton.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── FilterTabs.tsx
│   └── lib/
│       ├── api.ts
│       ├── auth.ts
│       └── utils.ts
├── middleware.ts
├── tailwind.config.ts
├── next.config.ts
├── tsconfig.json
├── package.json
├── .env.local
├── .env.example
└── CLAUDE.md
```

**Structure Decision**: Standard Next.js App Router structure with route groups for auth pages, centralized components, and lib for utilities.

## Complexity Tracking

> No violations - all choices align with constitution.

## Implementation Phases

### Phase 1: Setup & Configuration

**Purpose**: Initialize Next.js project with all dependencies

**Tasks**:
1. Create Next.js 16+ project with TypeScript, Tailwind, App Router
2. Install dependencies: better-auth, lucide-react
3. Create .env.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET
4. Configure tailwind.config.ts with custom theme
5. Create lib/utils.ts with cn() helper for className merging

**Checkpoint**: `npm run dev` starts without errors

---

### Phase 2: Core Library

**Purpose**: Build API client and auth utilities

**Tasks**:
1. Create lib/api.ts with fetchWithAuth wrapper
2. Create typed API functions: login, register, getTasks, createTask, updateTask, deleteTask
3. Create lib/auth.ts with Better Auth configuration
4. Export getSession, signIn, signOut from auth module

**Checkpoint**: API client compiles with proper types

---

### Phase 3: UI Components

**Purpose**: Build reusable UI components

**Tasks**:
1. Create components/ui/Button.tsx with variants (primary, outline, ghost)
2. Create components/ui/Input.tsx with label and error states
3. Create components/ui/Skeleton.tsx for loading states
4. Create components/FilterTabs.tsx for All/Active/Completed
5. Create components/TaskForm.tsx for task creation
6. Create components/TaskItem.tsx with checkbox and delete
7. Create components/TaskList.tsx as client component with state

**Checkpoint**: Components render in isolation

---

### Phase 4: Auth Pages (US1, US2)

**Purpose**: Implement registration and login flows

**Tasks**:
1. Create app/(auth)/layout.tsx with centered card layout
2. Create app/(auth)/login/page.tsx with form and validation
3. Create app/(auth)/register/page.tsx with confirm password
4. Handle form errors inline
5. Redirect to /tasks on success

**Checkpoint**: User can register and login

---

### Phase 5: Dashboard Page (US3-US7)

**Purpose**: Implement task management

**Tasks**:
1. Create app/tasks/page.tsx as Server Component
2. Fetch initial tasks in server component
3. Pass tasks to TaskList client component
4. Create app/tasks/loading.tsx with skeleton
5. Implement optimistic updates for toggle
6. Implement delete with immediate removal
7. Implement filter switching

**Checkpoint**: Full CRUD working on /tasks

---

### Phase 6: Route Protection (US8)

**Purpose**: Implement middleware for auth redirects

**Tasks**:
1. Create middleware.ts at project root
2. Define protected routes (/tasks)
3. Define auth routes (/login, /register)
4. Redirect unauthenticated to /login
5. Redirect authenticated away from auth pages
6. Add logout functionality

**Checkpoint**: Routes properly protected

---

### Phase 7: Layout & Polish

**Purpose**: Complete app shell and responsive design

**Tasks**:
1. Create app/layout.tsx with header
2. Add logout button in header (when authenticated)
3. Create app/page.tsx redirecting to /tasks or /login
4. Create app/error.tsx for error boundaries
5. Verify mobile responsiveness
6. Test all acceptance scenarios

**Checkpoint**: All user stories pass

---

### Phase 8: Documentation & Verification

**Purpose**: Final verification and docs

**Tasks**:
1. Create frontend/CLAUDE.md with implementation notes
2. Create frontend/.env.example
3. Update root docker-compose.yml if needed
4. Run quickstart.md verification checklist
5. Verify all acceptance criteria from spec.md

**Checkpoint**: Feature complete, ready for commit

---

## Dependencies & Execution Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Library)
    ↓
Phase 3 (Components)
    ↓
Phase 4 (Auth) ←→ Phase 5 (Dashboard) [can partially overlap]
    ↓
Phase 6 (Protection)
    ↓
Phase 7 (Polish)
    ↓
Phase 8 (Docs)
```

## Estimated Task Count

| Phase | Estimated Tasks |
|-------|-----------------|
| Phase 1: Setup | 5 |
| Phase 2: Library | 4 |
| Phase 3: Components | 7 |
| Phase 4: Auth Pages | 5 |
| Phase 5: Dashboard | 7 |
| Phase 6: Protection | 6 |
| Phase 7: Polish | 5 |
| Phase 8: Docs | 5 |
| **Total** | **~44** |

## User Story Mapping

| User Story | Phase | Key Files |
|------------|-------|-----------|
| US1 Registration | Phase 4 | app/(auth)/register/page.tsx |
| US2 Login | Phase 4 | app/(auth)/login/page.tsx |
| US3 View Dashboard | Phase 5 | app/tasks/page.tsx |
| US4 Create Task | Phase 5 | components/TaskForm.tsx |
| US5 Toggle Task | Phase 5 | components/TaskItem.tsx |
| US6 Delete Task | Phase 5 | components/TaskItem.tsx |
| US7 Filter Tasks | Phase 5 | components/FilterTabs.tsx |
| US8 Logout | Phase 6 | middleware.ts, layout.tsx |

## Next Steps

1. Run `/sp.tasks` to generate detailed tasks.md
2. Begin implementation with Phase 1
3. Create PHR after each phase completion

## References

- @specs/002-frontend-web/spec.md - Feature specification
- @specs/002-frontend-web/research.md - Technical decisions
- @specs/002-frontend-web/data-model.md - TypeScript interfaces
- @specs/002-frontend-web/quickstart.md - Setup guide
- @specs/ui/pages.md - Page layouts
- @specs/ui/components.md - Component specs
- @.specify/memory/constitution.md - Project principles
