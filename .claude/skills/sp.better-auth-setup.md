---
description: Configure Better Auth for Next.js 16+ with JWT authentication.
---

# Skill: Better Auth Setup

## Purpose
Set up Better Auth in Next.js to handle user authentication, session management, and JWT token storage.

## Stack Context
- **Frontend**: Next.js 16+ App Router
- **Auth Library**: Better Auth
- **Backend**: FastAPI (token validation)
- **Token Storage**: HTTP-only cookies

## Dependencies

```bash
npm install better-auth
```

## Implementation

### Auth Configuration
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  // Database adapter (if using Better Auth's built-in DB)
  // For this project, we use our own FastAPI backend
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  secret: process.env.BETTER_AUTH_SECRET,

  plugins: [
    jwt({
      // JWT configuration
      expiresIn: "7d",
    }),
  ],

  // Custom endpoints to proxy to FastAPI backend
  endpoints: {
    signIn: {
      path: "/api/auth/login",
      method: "POST",
    },
    signUp: {
      path: "/api/auth/register",
      method: "POST",
    },
  },
});

export type Session = typeof auth.$Infer.Session;
```

### Auth Client (Client Components)
```typescript
// lib/auth-client.ts
"use client";

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
});

export const {
  useSession,
  signIn,
  signUp,
  signOut,
} = authClient;
```

### Custom Auth with FastAPI Backend
```typescript
// lib/auth-api.ts
"use client";

import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AuthResponse {
  user: { id: string; email: string };
  token: string;
}

interface AuthStore {
  token: string | null;
  user: { id: string; email: string } | null;
}

// Simple auth store (consider using Zustand for production)
let authStore: AuthStore = {
  token: null,
  user: null,
};

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

export function getAuthUser(): AuthStore["user"] {
  if (typeof window === "undefined") return null;
  const user = localStorage.getItem("auth_user");
  return user ? JSON.parse(user) : null;
}

export async function signIn(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "Login failed");
  }

  const data: AuthResponse = await response.json();

  // Store token and user
  localStorage.setItem("auth_token", data.token);
  localStorage.setItem("auth_user", JSON.stringify(data.user));
  authStore = { token: data.token, user: data.user };

  return data;
}

export async function signUp(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "Registration failed");
  }

  const data: AuthResponse = await response.json();

  // Store token and user
  localStorage.setItem("auth_token", data.token);
  localStorage.setItem("auth_user", JSON.stringify(data.user));
  authStore = { token: data.token, user: data.user };

  return data;
}

export function signOut(): void {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("auth_user");
  authStore = { token: null, user: null };
  window.location.href = "/login";
}

export function isAuthenticated(): boolean {
  return !!getAuthToken();
}
```

### Auth Context Provider
```typescript
// contexts/auth-context.tsx
"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import {
  getAuthToken,
  getAuthUser,
  signIn as apiSignIn,
  signUp as apiSignUp,
  signOut as apiSignOut,
} from "@/lib/auth-api";

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize from localStorage
    const storedToken = getAuthToken();
    const storedUser = getAuthUser();
    setToken(storedToken);
    setUser(storedUser);
    setIsLoading(false);
  }, []);

  const signIn = async (email: string, password: string) => {
    const data = await apiSignIn(email, password);
    setUser(data.user);
    setToken(data.token);
  };

  const signUp = async (email: string, password: string) => {
    const data = await apiSignUp(email, password);
    setUser(data.user);
    setToken(data.token);
  };

  const signOut = () => {
    apiSignOut();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, signIn, signUp, signOut }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
```

### Root Layout with Provider
```typescript
// app/layout.tsx
import { AuthProvider } from "@/contexts/auth-context";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
```

## Usage Examples

### Login Form
```typescript
// app/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { signIn } = useAuth();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      await signIn(email, password);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      <button disabled={isLoading}>
        {isLoading ? "Signing in..." : "Sign In"}
      </button>
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
}
```

### Protected Component
```typescript
// components/user-info.tsx
"use client";

import { useAuth } from "@/contexts/auth-context";

export function UserInfo() {
  const { user, signOut } = useAuth();

  if (!user) return null;

  return (
    <div>
      <span>{user.email}</span>
      <button onClick={signOut}>Sign Out</button>
    </div>
  );
}
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-256-bit-secret-minimum-32-characters
```

## Checklist
- [ ] better-auth installed
- [ ] Auth context provider wraps app
- [ ] Token stored securely (localStorage or httpOnly cookie)
- [ ] signIn, signUp, signOut functions implemented
- [ ] useAuth hook available in components
- [ ] Environment variables configured
