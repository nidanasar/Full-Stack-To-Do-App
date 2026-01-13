---
description: Implement route protection with Next.js middleware and layout guards.
---

# Skill: Protected Routes

## Purpose
Protect authenticated routes from unauthenticated users and redirect authenticated users away from auth pages.

## Stack Context
- **Framework**: Next.js 16+ App Router
- **Auth**: JWT stored in cookies/localStorage
- **Patterns**: Middleware + Layout guards

## Route Protection Rules

| Route | Auth Required | Redirect If |
|-------|---------------|-------------|
| `/` (Dashboard) | Yes | Unauthenticated → `/login` |
| `/login` | No | Authenticated → `/` |
| `/register` | No | Authenticated → `/` |

## Option 1: Middleware (Recommended)

### Middleware Configuration
```typescript
// middleware.ts (at project root)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that require authentication
const protectedRoutes = ["/", "/tasks"];

// Routes for non-authenticated users only
const authRoutes = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from cookie
  const token = request.cookies.get("auth_token")?.value;
  const isAuthenticated = !!token;

  // Protected route + not authenticated → redirect to login
  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!isAuthenticated) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Auth route + authenticated → redirect to dashboard
  if (authRoutes.some((route) => pathname.startsWith(route))) {
    if (isAuthenticated) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - static files
     * - _next internal paths
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
```

## Option 2: Layout-Based Protection

### Protected Layout (Server Component)
```typescript
// app/(protected)/layout.tsx
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (!token) {
    redirect("/login");
  }

  // Optionally validate token here
  // const isValid = await validateToken(token);
  // if (!isValid) redirect("/login");

  return <>{children}</>;
}
```

### Auth Layout (Redirect if Logged In)
```typescript
// app/(auth)/layout.tsx
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (token) {
    redirect("/");
  }

  return <>{children}</>;
}
```

### File Structure with Route Groups
```
app/
├── (protected)/          # Requires auth
│   ├── layout.tsx        # Auth check
│   ├── page.tsx          # Dashboard (/)
│   └── tasks/
│       └── page.tsx      # Tasks list
├── (auth)/               # Public only
│   ├── layout.tsx        # Redirect if authed
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
└── layout.tsx            # Root layout
```

## Option 3: Client-Side Guard Component

### Auth Guard Component
```typescript
// components/auth-guard.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean; // true = must be logged in, false = must be logged out
}

export function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    if (requireAuth && !user) {
      router.replace("/login");
    } else if (!requireAuth && user) {
      router.replace("/");
    }
  }, [user, isLoading, requireAuth, router]);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  // Don't render children if auth check fails
  if (requireAuth && !user) return null;
  if (!requireAuth && user) return null;

  return <>{children}</>;
}
```

### Usage in Pages
```typescript
// app/page.tsx (Dashboard - requires auth)
"use client";

import { AuthGuard } from "@/components/auth-guard";
import { TaskList } from "@/components/task-list";

export default function DashboardPage() {
  return (
    <AuthGuard requireAuth>
      <TaskList />
    </AuthGuard>
  );
}

// app/login/page.tsx (Login - requires no auth)
"use client";

import { AuthGuard } from "@/components/auth-guard";
import { AuthForm } from "@/components/auth-form";

export default function LoginPage() {
  return (
    <AuthGuard requireAuth={false}>
      <AuthForm mode="login" />
    </AuthGuard>
  );
}
```

## Handling Redirect After Login

### Store Redirect URL
```typescript
// middleware.ts
if (!isAuthenticated) {
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("redirect", pathname);
  return NextResponse.redirect(loginUrl);
}
```

### Read Redirect URL After Login
```typescript
// app/login/page.tsx
"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signIn } = useAuth();

  async function handleLogin(email: string, password: string) {
    await signIn(email, password);

    // Redirect to original destination or dashboard
    const redirect = searchParams.get("redirect") || "/";
    router.push(redirect);
  }

  return <AuthForm mode="login" onSubmit={handleLogin} />;
}
```

## Cookie Management for Auth

### Setting Auth Cookie (After Login)
```typescript
// lib/auth-api.ts
export async function signIn(email: string, password: string) {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  // Set cookie for middleware to read
  document.cookie = `auth_token=${data.token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;

  return data;
}
```

### Clearing Auth Cookie (Logout)
```typescript
export function signOut() {
  // Clear cookie
  document.cookie = "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  localStorage.removeItem("auth_user");
  window.location.href = "/login";
}
```

## Comparison of Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **Middleware** | Runs before render, no flash | Limited to edge runtime |
| **Layout** | Server-side, type-safe | Can't access localStorage |
| **Client Guard** | Full React features | Flash of content possible |

## Recommended Setup

Use **Middleware + Layout** combination:
1. Middleware handles initial redirect (no flash)
2. Layout validates token on server
3. Client components read user from context

## Checklist
- [ ] Middleware configured for protected routes
- [ ] Auth routes redirect logged-in users
- [ ] Redirect URL preserved for post-login
- [ ] Loading state while checking auth
- [ ] Cookie set on login, cleared on logout
- [ ] Token validated server-side in layouts
