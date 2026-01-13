---
description: Implement optimistic UI updates for immediate user feedback before API response.
---

# Skill: Optimistic UI

## Purpose
Provide instant visual feedback when users perform actions, updating the UI immediately before the API responds. Roll back on error.

## Stack Context
- **Frontend**: Next.js + React
- **Pattern**: Update local state → Call API → Rollback on error

## Core Concept

```
User Action → Update UI Immediately → Call API
                     ↓                    ↓
                  Success            Error → Rollback
```

## Task Toggle Pattern

```typescript
// components/task-list.tsx
"use client";

import { useState } from "react";
import { Task } from "@/types";
import { clientApi } from "@/lib/api-client";
import { useAuth } from "@/contexts/auth-context";

interface TaskListProps {
  initialTasks: Task[];
}

export function TaskList({ initialTasks }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const { token } = useAuth();

  async function handleToggle(taskId: string) {
    // Find the task
    const taskIndex = tasks.findIndex((t) => t.id === taskId);
    if (taskIndex === -1) return;

    const task = tasks[taskIndex];
    const previousCompleted = task.completed;

    // 1. Optimistically update UI
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
    );

    try {
      // 2. Call API
      await clientApi(
        `/api/v1/tasks/${taskId}`,
        {
          method: "PATCH",
          body: JSON.stringify({ completed: !previousCompleted }),
        },
        token
      );
      // Success - UI already updated
    } catch (error) {
      // 3. Rollback on error
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId ? { ...t, completed: previousCompleted } : t
        )
      );
      // Optionally show error toast
      console.error("Failed to update task:", error);
    }
  }

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => handleToggle(task.id)}
          />
          <span className={task.completed ? "line-through" : ""}>
            {task.title}
          </span>
        </li>
      ))}
    </ul>
  );
}
```

## Task Delete Pattern

```typescript
// In TaskList component

async function handleDelete(taskId: string) {
  // Store the task for potential rollback
  const taskToDelete = tasks.find((t) => t.id === taskId);
  if (!taskToDelete) return;

  const taskIndex = tasks.findIndex((t) => t.id === taskId);

  // 1. Optimistically remove from UI
  setTasks((prev) => prev.filter((t) => t.id !== taskId));

  try {
    // 2. Call API
    await clientApi(
      `/api/v1/tasks/${taskId}`,
      { method: "DELETE" },
      token
    );
    // Success - task already removed from UI
  } catch (error) {
    // 3. Rollback - restore task at original position
    setTasks((prev) => {
      const newTasks = [...prev];
      newTasks.splice(taskIndex, 0, taskToDelete);
      return newTasks;
    });
    console.error("Failed to delete task:", error);
  }
}
```

## Task Create Pattern

```typescript
// In TaskList component

async function handleCreate(title: string, description?: string) {
  // Generate temporary ID for optimistic update
  const tempId = `temp-${Date.now()}`;
  const tempTask: Task = {
    id: tempId,
    title,
    description: description || null,
    completed: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  // 1. Optimistically add to UI
  setTasks((prev) => [tempTask, ...prev]);

  try {
    // 2. Call API
    const createdTask = await clientApi<Task>(
      "/api/v1/tasks",
      {
        method: "POST",
        body: JSON.stringify({ title, description }),
      },
      token
    );

    // 3. Replace temp task with real task
    setTasks((prev) =>
      prev.map((t) => (t.id === tempId ? createdTask : t))
    );
  } catch (error) {
    // 4. Rollback - remove temp task
    setTasks((prev) => prev.filter((t) => t.id !== tempId));
    console.error("Failed to create task:", error);
    throw error; // Re-throw so form can show error
  }
}
```

## Complete TaskList with Optimistic Updates

```typescript
// components/task-list.tsx
"use client";

import { useState } from "react";
import { Task } from "@/types";
import { clientApi } from "@/lib/api-client";
import { useAuth } from "@/contexts/auth-context";
import { TaskItem } from "./task-item";
import { TaskForm } from "./task-form";

interface TaskListProps {
  initialTasks: Task[];
}

export function TaskList({ initialTasks }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());
  const { token } = useAuth();

  // Track pending operations for UI feedback
  function setPending(id: string, isPending: boolean) {
    setPendingIds((prev) => {
      const next = new Set(prev);
      isPending ? next.add(id) : next.delete(id);
      return next;
    });
  }

  async function handleToggle(taskId: string) {
    const task = tasks.find((t) => t.id === taskId);
    if (!task || pendingIds.has(taskId)) return;

    const previousCompleted = task.completed;
    setPending(taskId, true);

    // Optimistic update
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
    );

    try {
      await clientApi(
        `/api/v1/tasks/${taskId}`,
        {
          method: "PATCH",
          body: JSON.stringify({ completed: !previousCompleted }),
        },
        token
      );
    } catch {
      // Rollback
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId ? { ...t, completed: previousCompleted } : t
        )
      );
    } finally {
      setPending(taskId, false);
    }
  }

  async function handleDelete(taskId: string) {
    const task = tasks.find((t) => t.id === taskId);
    if (!task || pendingIds.has(taskId)) return;

    const taskIndex = tasks.indexOf(task);
    setPending(taskId, true);

    // Optimistic remove
    setTasks((prev) => prev.filter((t) => t.id !== taskId));

    try {
      await clientApi(
        `/api/v1/tasks/${taskId}`,
        { method: "DELETE" },
        token
      );
    } catch {
      // Rollback
      setTasks((prev) => {
        const restored = [...prev];
        restored.splice(taskIndex, 0, task);
        return restored;
      });
    } finally {
      setPending(taskId, false);
    }
  }

  async function handleCreate(data: { title: string; description: string }) {
    const tempId = `temp-${Date.now()}`;
    const tempTask: Task = {
      id: tempId,
      title: data.title,
      description: data.description || null,
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Optimistic add
    setTasks((prev) => [tempTask, ...prev]);

    try {
      const created = await clientApi<Task>(
        "/api/v1/tasks",
        {
          method: "POST",
          body: JSON.stringify(data),
        },
        token
      );
      // Replace temp with real
      setTasks((prev) => prev.map((t) => (t.id === tempId ? created : t)));
    } catch {
      // Rollback
      setTasks((prev) => prev.filter((t) => t.id !== tempId));
      throw new Error("Failed to create task");
    }
  }

  return (
    <div className="space-y-4">
      <TaskForm onSubmit={handleCreate} />
      <ul className="space-y-2">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            isPending={pendingIds.has(task.id)}
            onToggle={handleToggle}
            onDelete={handleDelete}
          />
        ))}
      </ul>
    </div>
  );
}
```

## TaskItem with Pending State

```typescript
// components/task-item.tsx
"use client";

import { Task } from "@/types";

interface TaskItemProps {
  task: Task;
  isPending: boolean;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({
  task,
  isPending,
  onToggle,
  onDelete,
}: TaskItemProps) {
  return (
    <li
      className={`flex items-center gap-2 p-2 rounded border ${
        isPending ? "opacity-50" : ""
      } ${task.id.startsWith("temp-") ? "bg-gray-50" : ""}`}
    >
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        disabled={isPending}
      />
      <span className={task.completed ? "line-through text-gray-500" : ""}>
        {task.title}
      </span>
      <button
        onClick={() => {
          if (confirm("Delete this task?")) {
            onDelete(task.id);
          }
        }}
        disabled={isPending}
        className="ml-auto text-red-500 hover:text-red-700 disabled:opacity-50"
      >
        Delete
      </button>
    </li>
  );
}
```

## Key Patterns

| Action | Optimistic Update | Rollback Strategy |
|--------|-------------------|-------------------|
| Toggle | Flip `completed` immediately | Restore previous value |
| Delete | Remove from array immediately | Re-insert at original index |
| Create | Add temp item with temp ID | Remove temp item |
| Update | Update fields immediately | Restore previous values |

## Checklist
- [ ] UI updates before API call
- [ ] Previous state stored for rollback
- [ ] Error triggers rollback
- [ ] Temp IDs used for creates (e.g., `temp-${Date.now()}`)
- [ ] Pending state prevents duplicate actions
- [ ] Visual feedback during pending (opacity, spinner)
