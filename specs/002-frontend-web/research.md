# Research: Frontend Web Application

**Feature**: 002-frontend-web
**Date**: 2026-01-15

---

## Technical Decisions

### 1. Framework: Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with App Router

**Rationale**:
- Constitution mandates Next.js 16+ App Router
- Server Components for better performance
- Built-in routing and layouts
- Excellent TypeScript support

**Alternatives Considered**:
- Remix - Good alternative but Next.js is constitution-mandated
- Vite + React Router - No SSR out of box
- Create React App - Deprecated

---

### 2. Authentication: Better Auth

**Decision**: Use Better Auth for JWT session management

**Rationale**:
- Constitution mandates Better Auth
- Handles JWT in httpOnly cookies automatically
- Shared BETTER_AUTH_SECRET with backend
- Secure by default (no localStorage tokens)

**Alternatives Considered**:
- NextAuth.js - Good but Better Auth is constitution-mandated
- Custom JWT handling - More work, less secure
- Clerk/Auth0 - External services, not needed

**Integration Pattern**:
```typescript
// lib/auth.ts
import { betterAuth } from 'better-auth'

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  secret: process.env.BETTER_AUTH_SECRET,
})

export const { signIn, signOut, getSession } = auth
```

---

### 3. Styling: Tailwind CSS

**Decision**: Use Tailwind CSS with mobile-first approach

**Rationale**:
- Constitution mandates Tailwind CSS
- Mobile-first responsive design
- No CSS-in-JS runtime overhead
- Consistent design system

**Alternatives Considered**:
- styled-components - Runtime overhead
- CSS Modules - Less consistent
- Chakra UI - Extra dependency

**Breakpoints**:
| Breakpoint | Width | Use Case |
|------------|-------|----------|
| Default | < 640px | Mobile |
| sm | >= 640px | Tablet |
| lg | >= 1024px | Desktop |

---

### 4. State Management: React State + Server Components

**Decision**: Use React useState for client state, Server Components for data fetching

**Rationale**:
- No global state library needed
- Tasks fetched via Server Components
- Local state for UI (filter, form inputs)
- Optimistic updates via local state

**Alternatives Considered**:
- Redux - Overkill for this scope
- Zustand - Extra dependency not needed
- React Query - Good but SSR sufficient

**Pattern**:
```typescript
// Server Component fetches initial data
async function TasksPage() {
  const tasks = await fetchTasks()
  return <TaskList initialTasks={tasks} />
}

// Client Component manages local state
function TaskList({ initialTasks }) {
  const [tasks, setTasks] = useState(initialTasks)
  // ... optimistic updates
}
```

---

### 5. API Client: Centralized fetch wrapper

**Decision**: Create centralized API client in `lib/api.ts`

**Rationale**:
- Constitution requires centralized API access
- Single place for error handling
- Automatic JWT attachment via cookies
- Type-safe responses

**Implementation**:
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

async function fetchWithAuth<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // httpOnly cookie
    headers: { 'Content-Type': 'application/json', ...options?.headers }
  })
  // ... error handling
}
```

---

### 6. Form Handling: Native React forms

**Decision**: Use native React form handling with useState

**Rationale**:
- Simple forms (login, register, create task)
- No complex validation needed
- react-hook-form is overkill

**Alternatives Considered**:
- react-hook-form - Extra dependency
- Formik - Extra dependency
- Zod validation - Could add later if needed

---

### 7. Icons: Lucide React

**Decision**: Use Lucide React for icons

**Rationale**:
- Tree-shakable (only imports used icons)
- Consistent style
- TypeScript support
- Referenced in component specs

**Usage**:
```typescript
import { Loader2, X } from 'lucide-react'
```

---

### 8. Route Protection: Next.js Middleware

**Decision**: Use Next.js middleware for auth redirects

**Rationale**:
- Runs before page renders
- Handles both auth and protected routes
- Single source of truth for route rules

**Pattern**:
```typescript
// middleware.ts
export async function middleware(request: NextRequest) {
  const session = await getSession(request)

  if (!session && isProtectedRoute(pathname)) {
    return NextResponse.redirect('/login')
  }

  if (session && isAuthRoute(pathname)) {
    return NextResponse.redirect('/tasks')
  }
}
```

---

## Resolved Clarifications

| Question | Resolution |
|----------|------------|
| How to store JWT? | httpOnly cookie via Better Auth |
| Which icons? | Lucide React (tree-shakable) |
| How to handle loading? | Skeleton components + loading states |
| Optimistic updates? | Yes, for toggle and delete |
| Form library? | Native React (simple forms) |

---

## Best Practices Applied

### Next.js App Router
- Use Server Components by default
- Add "use client" only when needed
- Use `loading.tsx` for Suspense fallbacks
- Use `error.tsx` for error boundaries

### TypeScript
- Strict mode enabled
- All props typed with interfaces
- API responses typed
- No `any` types

### Tailwind CSS
- Mobile-first (default styles for mobile)
- Use `cn()` utility for conditional classes
- Consistent spacing scale
- Focus states for accessibility

### Security
- No tokens in localStorage
- httpOnly cookies only
- Input sanitization (React handles)
- CORS configured on backend

---

## References

- @specs/ui/pages.md - UI specification
- @specs/ui/components.md - Component specs
- @.specify/memory/constitution.md - Project principles
