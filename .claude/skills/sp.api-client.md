---
description: Implement a centralized API client for Next.js with JWT injection and type-safe responses.
---

# Skill: API Client

## Purpose
Provide a centralized fetch wrapper that handles JWT token injection, error handling, and type-safe responses for all backend API calls.

## Stack Context
- **Frontend**: Next.js 16+ with App Router
- **Auth**: Better Auth (provides session/token)
- **Backend**: FastAPI REST API

## Implementation

### API Client Core
```typescript
// lib/api.ts
import { auth } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
}

export class ApiClientError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

/**
 * Server-side API client (for Server Components and Route Handlers)
 */
export async function serverApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const session = await auth();

  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (session?.accessToken) {
    headers.set("Authorization", `Bearer ${session.accessToken}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
    cache: options.cache ?? "no-store", // Default: no caching for API calls
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiClientError(
      error.error?.code || "UNKNOWN_ERROR",
      error.error?.message || "An error occurred",
      response.status
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  const json: ApiResponse<T> = await response.json();

  if (json.error) {
    throw new ApiClientError(json.error.code, json.error.message, response.status);
  }

  return json.data as T;
}
```

### Client-Side API Client
```typescript
// lib/api-client.ts
"use client";

import { useSession } from "@/lib/auth-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClientError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

/**
 * Client-side API function (for use in Client Components)
 */
export async function clientApi<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Redirect to login on unauthorized
    window.location.href = "/login";
    throw new ApiClientError("UNAUTHORIZED", "Please log in", 401);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiClientError(
      error.error?.code || "UNKNOWN_ERROR",
      error.error?.message || "An error occurred",
      response.status
    );
  }

  if (response.status === 204) {
    return null as T;
  }

  const json = await response.json();
  return json.data ?? json;
}
```

### Custom Hook for API Calls
```typescript
// hooks/use-api.ts
"use client";

import { useState, useCallback } from "react";
import { clientApi, ApiClientError } from "@/lib/api-client";
import { useSession } from "@/lib/auth-client";

interface UseApiState<T> {
  data: T | null;
  error: ApiClientError | null;
  isLoading: boolean;
}

export function useApi<T>() {
  const { data: session } = useSession();
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });

  const execute = useCallback(
    async (endpoint: string, options?: RequestInit): Promise<T | null> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const data = await clientApi<T>(
          endpoint,
          options,
          session?.accessToken
        );
        setState({ data, error: null, isLoading: false });
        return data;
      } catch (err) {
        const error = err instanceof ApiClientError
          ? err
          : new ApiClientError("UNKNOWN", "Unknown error", 500);
        setState({ data: null, error, isLoading: false });
        return null;
      }
    },
    [session?.accessToken]
  );

  return { ...state, execute };
}
```

## Usage Examples

### Server Component (Fetching Data)
```typescript
// app/tasks/page.tsx
import { serverApi } from "@/lib/api";
import { Task } from "@/types";

export default async function TasksPage() {
  const tasks = await serverApi<Task[]>("/api/v1/tasks");

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  );
}
```

### Client Component (Creating Data)
```typescript
// components/task-form.tsx
"use client";

import { useApi } from "@/hooks/use-api";
import { Task } from "@/types";

export function TaskForm() {
  const { execute, isLoading, error } = useApi<Task>();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const task = await execute("/api/v1/tasks", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title"),
        description: formData.get("description"),
      }),
    });

    if (task) {
      // Success - redirect or update UI
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" required />
      <textarea name="description" />
      <button disabled={isLoading}>
        {isLoading ? "Creating..." : "Create Task"}
      </button>
      {error && <p className="text-red-500">{error.message}</p>}
    </form>
  );
}
```

### Deleting Data
```typescript
// components/task-item.tsx
"use client";

import { clientApi } from "@/lib/api-client";
import { useSession } from "@/lib/auth-client";

export function TaskItem({ task }: { task: Task }) {
  const { data: session } = useSession();

  async function handleDelete() {
    if (!confirm("Delete this task?")) return;

    await clientApi(
      `/api/v1/tasks/${task.id}`,
      { method: "DELETE" },
      session?.accessToken
    );

    // Trigger revalidation or update local state
  }

  return (
    <div>
      <span>{task.title}</span>
      <button onClick={handleDelete}>Delete</button>
    </div>
  );
}
```

## TypeScript Types

```typescript
// types/index.ts
export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface User {
  id: string;
  email: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Error Handling Patterns

| Error Code | Status | Action |
|------------|--------|--------|
| `UNAUTHORIZED` | 401 | Redirect to /login |
| `RESOURCE_NOT_FOUND` | 404 | Show "not found" message |
| `VALIDATION_ERROR` | 400 | Display field errors |
| `INTERNAL_ERROR` | 500 | Show generic error |

## Checklist
- [ ] API_URL configured in environment
- [ ] Server and client API functions created
- [ ] JWT token injected in Authorization header
- [ ] 401 errors redirect to login
- [ ] Type-safe responses with generics
- [ ] Loading and error states handled
