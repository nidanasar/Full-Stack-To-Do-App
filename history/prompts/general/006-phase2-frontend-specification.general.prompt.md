---
id: 006
title: Phase II Frontend Specification
stage: general
date: 2026-01-13
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: nida.nasarr
command: /sp.specify
labels: ["frontend", "nextjs", "typescript", "tailwind", "components", "phase2"]
links:
  spec: specs/ui/pages.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/ui/pages.md
  - specs/ui/components.md
tests:
  - null
---

## Prompt

/sp.specify # Frontend Specification — Phase II

## Purpose
Define the complete frontend architecture, page structure, component library,
and UX patterns for Phase II, ensuring a responsive, accessible, and
user-friendly task management interface.

---

## Tech Stack

- Framework: Next.js 16+ (App Router)
- Language: TypeScript (strict mode)
- Styling: Tailwind CSS
- Auth: Better Auth (client SDK)
- State: React hooks (useState, useEffect)
- HTTP: Fetch API with credentials

---

## Application Structure

Route Groups:
- (auth)/ — Login, Register (public)
- (dashboard)/ — Tasks (protected)

Middleware:
- Route protection via Next.js middleware
- Redirect unauthenticated users to /login
- Redirect authenticated users from /login to /tasks

---

## Pages

### Login Page (/login)
- Email and password fields
- Submit button with loading state
- Link to register page
- Error display for invalid credentials

### Register Page (/register)
- Email and password fields
- Password confirmation
- Submit button with loading state
- Link to login page
- Error display for validation failures

### Tasks Dashboard (/tasks)
- Task list with filter (all/active/completed)
- Add task form
- Task items with toggle and delete
- Empty state when no tasks
- Loading skeletons during fetch

---

## Components

Base UI:
- Button (variants: primary, secondary, danger, ghost)
- Input (with error state)
- Card (container component)
- Skeleton (loading placeholder)

Auth Components:
- LoginForm
- RegisterForm
- LogoutButton

Task Components:
- TaskList
- TaskItem
- TaskForm
- TaskFilter
- EmptyState

---

## API Client

- Base URL from environment variable
- Credentials included for JWT cookies
- Consistent error handling
- Type-safe request/response

---

## UX Rules

1. Optimistic updates for task operations
2. Loading states for all async operations
3. Error messages near the source of error
4. Accessible (ARIA labels, keyboard navigation)
5. Mobile-first responsive design

---

## Phase II Constraints

Not implemented:
- Drag-and-drop reordering
- Task due dates
- Task categories/tags
- Search functionality
- Offline support

## Response snapshot

Completely rewrote `specs/ui/pages.md` and `specs/ui/components.md` with comprehensive Phase II frontend specification.

**specs/ui/pages.md (720+ lines)**:
- Application structure with route groups ((auth)/ and (dashboard)/)
- Middleware implementation for route protection with code
- Authentication flows (login, register, logout) with sequence diagrams
- Page layouts and wireframes for Login, Register, Tasks Dashboard
- API client implementation with fetchWithAuth pattern
- UX rules: optimistic updates, loading states, error handling
- Data limits and validation rules
- 12 functional requirements (FR-UI-001 through FR-UI-012)
- 20 acceptance criteria (AC-UI-001 through AC-UI-020)

**specs/ui/components.md (1100+ lines)**:
- Complete component inventory with dependency matrix
- Base UI components with full TypeScript implementations:
  - Button (primary, secondary, danger, ghost variants)
  - Input (with error states and accessibility)
  - Card (container component)
  - Skeleton (loading placeholder)
- Auth components with form handling:
  - LoginForm (email/password, validation, error handling)
  - RegisterForm (email/password/confirm, validation)
  - LogoutButton (session clearing)
- Task components with optimistic updates:
  - TaskList (filter state, optimistic toggle/delete)
  - TaskItem (checkbox, title, delete button)
  - TaskForm (add new task with validation)
  - TaskFilter (all/active/completed tabs)
  - EmptyState (context-aware empty messaging)
- Component props interfaces and TypeScript types
- Accessibility requirements (ARIA labels, keyboard navigation)
- 12 functional requirements (FR-COMP-001 through FR-COMP-012)
- 16 acceptance criteria (AC-COMP-001 through AC-COMP-016)

**Key Implementation Patterns**:
- Route protection middleware:
```typescript
export function middleware(request: NextRequest) {
  const token = request.cookies.get('session_token')?.value
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
                     request.nextUrl.pathname.startsWith('/register')
  if (!token && !isAuthPage) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  // ...
}
```

- Optimistic update pattern:
```typescript
async function handleToggle(taskId: string) {
  const task = tasks.find(t => t.id === taskId)
  // Optimistic update
  setTasks(tasks.map(t =>
    t.id === taskId ? { ...t, completed: !t.completed } : t
  ))
  const { error } = await taskApi.updateTask(taskId, { completed: !task.completed })
  // Revert on error
  if (error) {
    setTasks(tasks.map(t =>
      t.id === taskId ? { ...t, completed: task.completed } : t
    ))
  }
}
```

- API client with credentials:
```typescript
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // Include cookies (JWT)
  })
  // error handling...
}
```

## Outcome

- ✅ Impact: Complete frontend specification defining pages, components, API client, and UX patterns
- 🧪 Tests: N/A (specification document)
- 📁 Files: specs/ui/pages.md (rewritten), specs/ui/components.md (rewritten)
- 🔁 Next prompts: `/sp.plan` for implementation plan, `/sp.tasks` for task breakdown
- 🧠 Reflection: Specs include implementation-ready TypeScript code; optimistic update patterns ensure responsive UX

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - specification document
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding Storybook component documentation patterns
