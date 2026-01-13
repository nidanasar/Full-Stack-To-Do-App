# Frontend Specification — Phase II

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Status**: Ratified

## Purpose

Define the complete frontend behavior for Phase II of the Evolution of Todo project, ensuring a responsive, secure, and user-scoped task management UI built using spec-driven development.

This specification governs UI architecture, components, pages, authentication flow, and user experience requirements.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 16+ (App Router) | Server-side rendering, routing |
| Language | TypeScript (strict mode) | Type safety |
| Styling | Tailwind CSS | Mobile-first responsive design |
| Authentication | Better Auth | JWT session management |
| State | React Server Components | Default rendering strategy |
| HTTP Client | Centralized API client | Backend communication |

---

## Architecture Principles

| Principle | Description | Enforcement |
|-----------|-------------|-------------|
| Server Components First | Use Server Components by default | Code review |
| Client Components for Interactivity | Only use "use client" when needed | Code review |
| Centralized API Access | No direct fetch outside lib/api.ts | Linting |
| Backend-Driven Authorization | UI reflects backend auth state | Testing |
| No Business Logic | Frontend handles UI only | Architecture review |

### Rendering Strategy

| Component Type | Use Case | Directive |
|----------------|----------|-----------|
| Server Component | Static content, initial data fetch | None (default) |
| Client Component | Forms, buttons, interactive UI | `"use client"` |

---

## Application Structure

```
/frontend
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group (public)
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   ├── register/
│   │   │   └── page.tsx          # Register page
│   │   └── layout.tsx            # Auth layout (centered)
│   │
│   ├── (dashboard)/              # Dashboard route group (protected)
│   │   ├── tasks/
│   │   │   └── page.tsx          # Tasks dashboard
│   │   └── layout.tsx            # Dashboard layout (with nav)
│   │
│   ├── api/                      # API routes
│   │   └── auth/
│   │       └── [...betterauth]/  # Better Auth handlers
│   │
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home (redirects to /tasks)
│   └── not-found.tsx             # 404 page
│
├── components/                   # Reusable UI components
│   ├── ui/                       # Base UI elements
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Skeleton.tsx
│   │
│   ├── auth/                     # Auth-specific components
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── LogoutButton.tsx
│   │
│   ├── tasks/                    # Task-specific components
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   ├── TaskFilter.tsx
│   │   └── EmptyState.tsx
│   │
│   └── layout/                   # Layout components
│       ├── Navbar.tsx
│       ├── Header.tsx
│       └── Footer.tsx
│
├── lib/                          # Utilities and services
│   ├── api.ts                    # API client (centralized)
│   ├── auth.ts                   # Better Auth client
│   ├── utils.ts                  # Helper functions
│   └── types.ts                  # TypeScript types
│
├── hooks/                        # Custom React hooks
│   ├── useAuth.ts                # Authentication hook
│   └── useTasks.ts               # Task operations hook
│
├── middleware.ts                 # Route protection middleware
│
├── styles/                       # Global styles
│   └── globals.css               # Tailwind imports
│
└── tailwind.config.ts            # Tailwind configuration
```

---

## Authentication Flow

### Login Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │     │   Frontend   │     │   Backend    │
│   Browser    │     │  Better Auth │     │   FastAPI    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ 1. Navigate to     │                    │
       │    /login          │                    │
       │───────────────────▶│                    │
       │                    │                    │
       │ 2. Enter email     │                    │
       │    + password      │                    │
       │───────────────────▶│                    │
       │                    │                    │
       │                    │ 3. POST /auth/login│
       │                    │───────────────────▶│
       │                    │                    │
       │                    │ 4. Validate +      │
       │                    │    return JWT      │
       │                    │◀───────────────────│
       │                    │                    │
       │ 5. Store JWT in    │                    │
       │    httpOnly cookie │                    │
       │◀───────────────────│                    │
       │                    │                    │
       │ 6. Redirect to     │                    │
       │    /tasks          │                    │
       │◀───────────────────│                    │
```

### Registration Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │     │   Frontend   │     │   Backend    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ 1. Navigate to     │                    │
       │    /register       │                    │
       │───────────────────▶│                    │
       │                    │                    │
       │ 2. Enter email +   │                    │
       │    password +      │                    │
       │    confirm         │                    │
       │───────────────────▶│                    │
       │                    │                    │
       │                    │ 3. Validate        │
       │                    │    passwords match │
       │                    │                    │
       │                    │ 4. POST /auth/     │
       │                    │    register        │
       │                    │───────────────────▶│
       │                    │                    │
       │                    │ 5. Create user +   │
       │                    │    return JWT      │
       │                    │◀───────────────────│
       │                    │                    │
       │ 6. Redirect to     │                    │
       │    /tasks          │                    │
       │◀───────────────────│                    │
```

### Logout Flow

```
┌──────────────┐     ┌──────────────┐
│    User      │     │   Frontend   │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │ 1. Click logout    │
       │───────────────────▶│
       │                    │
       │                    │ 2. Clear session
       │                    │    (delete cookie)
       │                    │
       │ 3. Redirect to     │
       │    /login          │
       │◀───────────────────│
```

### Session Persistence

| Scenario | Behavior |
|----------|----------|
| Valid session | User remains authenticated |
| Expired session | Redirect to /login on next request |
| Browser restart | Session persists (until token expiry) |

---

## Route Protection

### Middleware Implementation

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getSession } from './lib/auth'

const publicPaths = ['/login', '/register']
const authPaths = ['/login', '/register']

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const session = await getSession(request)

  // Redirect authenticated users away from auth pages
  if (session && authPaths.includes(pathname)) {
    return NextResponse.redirect(new URL('/tasks', request.url))
  }

  // Redirect unauthenticated users to login
  if (!session && !publicPaths.includes(pathname)) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
}
```

### Route Classification

| Route | Protection | Authenticated Behavior | Unauthenticated Behavior |
|-------|------------|------------------------|--------------------------|
| `/` | Public | Redirect to `/tasks` | Redirect to `/login` |
| `/login` | Public | Redirect to `/tasks` | Show login form |
| `/register` | Public | Redirect to `/tasks` | Show register form |
| `/tasks` | Protected | Show dashboard | Redirect to `/login` |

---

## Pages

### Login Page (`/login`)

**Route**: `/login`
**Auth Required**: No (redirects if authenticated)
**Component Type**: Client Component

**Layout**:
```
┌─────────────────────────────────────────┐
│                                         │
│              App Logo                   │
│          "Evolution of Todo"            │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         ┌─────────────────────┐         │
│         │  Email              │         │
│         │  [________________] │         │
│         │                     │         │
│         │  Password           │         │
│         │  [________________] │         │
│         │                     │         │
│         │  [    Sign In     ] │         │
│         │                     │         │
│         │  ─────────────────  │         │
│         │  Don't have an      │         │
│         │  account? Register  │         │
│         └─────────────────────┘         │
│                                         │
└─────────────────────────────────────────┘
```

**Behavior**:
| Action | Result |
|--------|--------|
| Submit valid credentials | Redirect to `/tasks` |
| Submit invalid credentials | Show error: "Invalid credentials" |
| Click "Register" link | Navigate to `/register` |

**Validation**:
- Email: Required, valid format
- Password: Required

**Error Display**:
- Inline error messages below form
- Generic "Invalid credentials" for auth failures

---

### Register Page (`/register`)

**Route**: `/register`
**Auth Required**: No (redirects if authenticated)
**Component Type**: Client Component

**Layout**:
```
┌─────────────────────────────────────────┐
│                                         │
│              App Logo                   │
│          "Create Account"               │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         ┌─────────────────────┐         │
│         │  Email              │         │
│         │  [________________] │         │
│         │                     │         │
│         │  Password           │         │
│         │  [________________] │         │
│         │                     │         │
│         │  Confirm Password   │         │
│         │  [________________] │         │
│         │                     │         │
│         │  [   Create Acct  ] │         │
│         │                     │         │
│         │  ─────────────────  │         │
│         │  Already have an    │         │
│         │  account? Sign In   │         │
│         └─────────────────────┘         │
│                                         │
└─────────────────────────────────────────┘
```

**Behavior**:
| Action | Result |
|--------|--------|
| Submit valid registration | Redirect to `/tasks` (auto-login) |
| Submit existing email | Show error: "Email already registered" |
| Passwords don't match | Show error: "Passwords do not match" |
| Password too short | Show error: "Password must be at least 8 characters" |

**Validation**:
- Email: Required, valid format, unique
- Password: Required, minimum 8 characters
- Confirm Password: Required, must match password

---

### Tasks Dashboard (`/tasks`)

**Route**: `/tasks`
**Auth Required**: Yes
**Component Type**: Mixed (Server + Client)

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────┐   │
│  │  Evolution of Todo          [User] [Logout]     │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │  Add New Task                                    │  │
│   │  [Title________________________] [Add Task]      │  │
│   └─────────────────────────────────────────────────┘  │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │  [All] [Active] [Completed]     X tasks         │  │
│   └─────────────────────────────────────────────────┘  │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │  ○ Buy groceries                        [✕]     │  │
│   │    Milk, eggs, bread                            │  │
│   ├─────────────────────────────────────────────────┤  │
│   │  ● Call dentist                         [✕]     │  │
│   │    Schedule appointment                         │  │
│   ├─────────────────────────────────────────────────┤  │
│   │  ○ Review PR                            [✕]     │  │
│   │    Check latest changes                         │  │
│   └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**States**:

| State | Display |
|-------|---------|
| Loading | Skeleton placeholders |
| Empty | "No tasks yet. Add your first task above!" |
| With Tasks | Task list with filter |
| Error | "Failed to load tasks. Please try again." |

**Features**:
- Fetch tasks on load (server-side)
- Add new task (client-side form)
- Toggle task completion (optimistic update)
- Delete task (with confirmation)
- Filter by status (All/Active/Completed)

---

## Component Specifications

### Detailed component specifications in `components.md`

---

## API Client (`lib/api.ts`)

### Implementation

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ApiError {
  code: string
  message: string
}

interface ApiResponse<T> {
  data?: T
  error?: ApiError
}

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies (JWT)
    })

    if (!response.ok) {
      const error = await response.json()
      return { error: error.error }
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return { data: undefined as T }
    }

    const data = await response.json()
    return { data }
  } catch (error) {
    return {
      error: {
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to server',
      },
    }
  }
}

// Task API methods
export const taskApi = {
  async getTasks(filter?: { completed?: boolean }) {
    const params = new URLSearchParams()
    if (filter?.completed !== undefined) {
      params.set('completed', String(filter.completed))
    }
    const query = params.toString() ? `?${params}` : ''
    return fetchWithAuth<{ tasks: Task[] }>(`/tasks${query}`)
  },

  async getTask(id: string) {
    return fetchWithAuth<Task>(`/tasks/${id}`)
  },

  async createTask(data: { title: string; description?: string }) {
    return fetchWithAuth<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async updateTask(id: string, data: Partial<Task>) {
    return fetchWithAuth<Task>(`/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  async deleteTask(id: string) {
    return fetchWithAuth<void>(`/tasks/${id}`, {
      method: 'DELETE',
    })
  },
}

// Auth API methods
export const authApi = {
  async login(email: string, password: string) {
    return fetchWithAuth<{ user: User; token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },

  async register(email: string, password: string) {
    return fetchWithAuth<{ user: User; token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },
}
```

### API Client Rules

| Rule | Implementation |
|------|----------------|
| JWT attached automatically | `credentials: 'include'` |
| Centralized error handling | Try/catch with typed errors |
| Type-safe responses | Generic `ApiResponse<T>` |
| No direct fetch elsewhere | Only use `taskApi` / `authApi` |

---

## UX Rules

### Optimistic Updates

```typescript
// Example: Toggle task completion
async function toggleTask(taskId: string, currentCompleted: boolean) {
  // 1. Optimistic update (immediately reflect in UI)
  setTasks(tasks.map(t =>
    t.id === taskId ? { ...t, completed: !currentCompleted } : t
  ))

  // 2. Make API call
  const { error } = await taskApi.updateTask(taskId, {
    completed: !currentCompleted
  })

  // 3. Revert on error
  if (error) {
    setTasks(tasks.map(t =>
      t.id === taskId ? { ...t, completed: currentCompleted } : t
    ))
    showError(error.message)
  }
}
```

### Loading States

| Component | Loading Indicator |
|-----------|-------------------|
| Task List | Skeleton cards |
| Form Submit | Disabled button + spinner |
| Toggle Complete | Immediate (optimistic) |
| Delete | Disabled button during API call |

### Error Handling

| Error Type | Display |
|------------|---------|
| Form validation | Inline below field |
| API error | Toast notification |
| Network error | "Unable to connect. Check your internet." |
| Auth error | Redirect to login |

### Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, stacked |
| Tablet | 640-1024px | Wider form, compact list |
| Desktop | > 1024px | Max-width container, comfortable spacing |

---

## Security Constraints

### Token Security

| Constraint | Implementation |
|------------|----------------|
| No JS access to JWT | httpOnly cookie |
| HTTPS in production | Server config |
| No token in localStorage | Cookie only |

### Data Security

| Constraint | Implementation |
|------------|----------------|
| No user_id in frontend state | Backend handles via JWT |
| No cross-user data display | Backend enforces isolation |
| Sanitize user input | React auto-escapes |

### Frontend Security Rules

```typescript
// ❌ NEVER do this
localStorage.setItem('token', jwt)
sessionStorage.setItem('user_id', userId)

// ✅ CORRECT: Let Better Auth handle cookies
// JWT stored in httpOnly cookie automatically
```

---

## Phase II Constraints

### Not Implemented

| Feature | Status | Rationale |
|---------|--------|-----------|
| Task priorities | Excluded | Out of scope |
| Task tags/labels | Excluded | Out of scope |
| Search by title | Excluded | Basic filter sufficient |
| Realtime updates | Excluded | Polling/refresh sufficient |
| Admin UI | Excluded | Single role for MVP |
| Dark mode | Excluded | Out of scope |
| Task due dates | Excluded | Out of scope |

### UI Limits

| Limit | Value |
|-------|-------|
| Tasks displayed | All (no pagination) |
| Title input max | 500 characters |
| Description input max | 5000 characters |

---

## Functional Requirements

### Authentication UI Requirements

- **FR-UI-001**: System MUST display login form at `/login`
- **FR-UI-002**: System MUST display registration form at `/register`
- **FR-UI-003**: System MUST redirect authenticated users from auth pages
- **FR-UI-004**: System MUST redirect unauthenticated users to `/login`
- **FR-UI-005**: System MUST display logout button when authenticated

### Task UI Requirements

- **FR-UI-006**: System MUST display task list at `/tasks`
- **FR-UI-007**: System MUST display task creation form
- **FR-UI-008**: System MUST allow task completion toggle
- **FR-UI-009**: System MUST allow task deletion
- **FR-UI-010**: System MUST support filtering by completion status
- **FR-UI-011**: System MUST display loading skeleton during fetch
- **FR-UI-012**: System MUST display empty state when no tasks

### UX Requirements

- **FR-UI-013**: System MUST use optimistic updates for toggles
- **FR-UI-014**: System MUST disable submit buttons during API calls
- **FR-UI-015**: System MUST display inline validation errors
- **FR-UI-016**: System MUST be responsive across screen sizes

---

## Frontend Acceptance Criteria

### Authentication

- [ ] **AC-UI-001**: Login page displays email and password fields
- [ ] **AC-UI-002**: Registration page displays email, password, and confirm fields
- [ ] **AC-UI-003**: Invalid credentials show error message
- [ ] **AC-UI-004**: Successful login redirects to `/tasks`
- [ ] **AC-UI-005**: Logout clears session and redirects to `/login`

### Route Protection

- [ ] **AC-UI-006**: Unauthenticated users cannot access `/tasks`
- [ ] **AC-UI-007**: Authenticated users cannot access `/login` or `/register`
- [ ] **AC-UI-008**: Session persists across page refreshes

### Task Operations

- [ ] **AC-UI-009**: Tasks load on dashboard mount
- [ ] **AC-UI-010**: New task appears immediately after creation
- [ ] **AC-UI-011**: Task completion toggles optimistically
- [ ] **AC-UI-012**: Deleted task removes from list
- [ ] **AC-UI-013**: Filter buttons work correctly

### Validation

- [ ] **AC-UI-014**: Empty email shows validation error
- [ ] **AC-UI-015**: Empty password shows validation error
- [ ] **AC-UI-016**: Empty title shows validation error
- [ ] **AC-UI-017**: Password mismatch shows error

### Responsive Design

- [ ] **AC-UI-018**: UI works on mobile (< 640px)
- [ ] **AC-UI-019**: UI works on tablet (640-1024px)
- [ ] **AC-UI-020**: UI works on desktop (> 1024px)

---

## References

- @specs/architecture.md - System architecture (Frontend Architecture section)
- @specs/features/authentication.md - Authentication specification
- @specs/api/rest-endpoints.md - API contract
- @specs/ui/components.md - Component specifications
- @.specify/memory/constitution.md - Project constitution
