---
description: Guide for choosing between Server and Client Components in Next.js App Router.
---

# Skill: Server/Client Component Split

## Purpose
Define when to use Server Components (default) vs Client Components ('use client') in Next.js 16+ App Router for optimal performance and user experience.

## Stack Context
- **Framework**: Next.js 16+ App Router
- **Default**: Server Components (RSC)
- **Client**: 'use client' directive

## Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│                    Does the component...                     │
├─────────────────────────────────────────────────────────────┤
│ Need useState, useEffect, or event handlers?                │
│ ├─ YES → Client Component                                   │
│ └─ NO  ↓                                                    │
├─────────────────────────────────────────────────────────────┤
│ Need browser APIs (localStorage, window, navigator)?        │
│ ├─ YES → Client Component                                   │
│ └─ NO  ↓                                                    │
├─────────────────────────────────────────────────────────────┤
│ Need to handle user interaction (onClick, onChange)?        │
│ ├─ YES → Client Component                                   │
│ └─ NO  → Server Component (default)                         │
└─────────────────────────────────────────────────────────────┘
```

## Server Components (Default)

### When to Use
- Data fetching from database/API
- Static content rendering
- SEO-critical content
- Large dependencies (keep off client bundle)
- Accessing backend resources directly

### Example: Task List Page
```typescript
// app/tasks/page.tsx (Server Component - no directive needed)
import { serverApi } from "@/lib/api";
import { Task } from "@/types";
import { TaskList } from "@/components/task-list";

export default async function TasksPage() {
  // Fetch data on server
  const tasks = await serverApi<Task[]>("/api/v1/tasks");

  // Pass to client component for interactivity
  return <TaskList initialTasks={tasks} />;
}
```

### Example: Layout with Auth Check
```typescript
// app/(protected)/layout.tsx (Server Component)
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();

  if (!session) {
    redirect("/login");
  }

  return <>{children}</>;
}
```

## Client Components

### When to Use
- Interactive UI (forms, buttons, toggles)
- State management (useState, useReducer)
- Effects (useEffect, custom hooks)
- Event handlers (onClick, onChange, onSubmit)
- Browser APIs (localStorage, window)
- Third-party libraries requiring client-side JS

### Example: Task Form
```typescript
// components/task-form.tsx
"use client"; // Required for interactivity

import { useState } from "react";
import { useAuth } from "@/contexts/auth-context";

export function TaskForm({ onSubmit }: { onSubmit: (task: Task) => void }) {
  const [title, setTitle] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { token } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    // ... submit logic
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <button disabled={isLoading}>Create</button>
    </form>
  );
}
```

### Example: Task Item with Actions
```typescript
// components/task-item.tsx
"use client";

import { useState } from "react";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete() {
    if (!confirm("Delete?")) return;
    setIsDeleting(true);
    await onDelete(task.id);
  }

  return (
    <div>
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />
      <span>{task.title}</span>
      <button onClick={handleDelete} disabled={isDeleting}>
        Delete
      </button>
    </div>
  );
}
```

## Hybrid Pattern: Server + Client

### Pattern: Server fetches, Client handles interaction
```typescript
// app/page.tsx (Server Component)
import { serverApi } from "@/lib/api";
import { TaskList } from "@/components/task-list";

export default async function HomePage() {
  const tasks = await serverApi<Task[]>("/api/v1/tasks");
  return <TaskList initialTasks={tasks} />;
}

// components/task-list.tsx (Client Component)
"use client";

import { useState } from "react";
import { TaskItem } from "./task-item";

export function TaskList({ initialTasks }: { initialTasks: Task[] }) {
  const [tasks, setTasks] = useState(initialTasks);

  function handleToggle(id: string) {
    setTasks((prev) =>
      prev.map((t) =>
        t.id === id ? { ...t, completed: !t.completed } : t
      )
    );
    // Also update backend...
  }

  return (
    <ul>
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} onToggle={handleToggle} />
      ))}
    </ul>
  );
}
```

## Component Classification

### Server Components (No 'use client')
| Component | Reason |
|-----------|--------|
| Page layouts | No interactivity |
| Data fetching pages | async/await |
| Static headers/footers | No state |
| SEO content | Must be server-rendered |
| Auth check layouts | Server-side auth |

### Client Components ('use client')
| Component | Reason |
|-----------|--------|
| TaskForm | Form state, submission |
| TaskItem | onClick handlers |
| TaskList | useState for tasks |
| FilterTabs | Filter state |
| AuthForm | Form handling |
| Header (with logout) | onClick for logout |

## Project File Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Server (wraps with providers)
│   ├── page.tsx            # Server (fetches tasks)
│   ├── login/
│   │   └── page.tsx        # Client (form)
│   └── register/
│       └── page.tsx        # Client (form)
├── components/
│   ├── task-form.tsx       # Client
│   ├── task-item.tsx       # Client
│   ├── task-list.tsx       # Client
│   ├── filter-tabs.tsx     # Client
│   ├── auth-form.tsx       # Client
│   └── header.tsx          # Client (logout button)
├── contexts/
│   └── auth-context.tsx    # Client (provider)
└── lib/
    ├── api.ts              # Server API client
    └── api-client.ts       # Client API client
```

## Performance Tips

1. **Keep Client Components Small**
   - Extract interactive parts into small client components
   - Keep parent as server component

2. **Avoid 'use client' in Layouts**
   - Use composition instead
   - Wrap with client provider in root layout only

3. **Preload Data on Server**
   - Fetch in server component
   - Pass as props to client component

4. **Minimize Client Bundle**
   - Heavy libraries stay on server
   - Only interactive code goes to client

## Checklist
- [ ] Pages default to Server Components
- [ ] 'use client' only where interaction needed
- [ ] Data fetching happens on server
- [ ] Interactive components receive data as props
- [ ] Auth context wrapped at root level
- [ ] No useState/useEffect in server components
