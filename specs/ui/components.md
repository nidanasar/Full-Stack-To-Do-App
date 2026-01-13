# Component Specifications — Phase II

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Status**: Ratified

## Purpose

Define detailed specifications for all frontend components, including props, states, behavior, and implementation patterns.

---

## Component Organization

```
components/
├── ui/                    # Base UI elements (reusable primitives)
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── Skeleton.tsx
│   └── Label.tsx
│
├── auth/                  # Authentication components
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── LogoutButton.tsx
│
├── tasks/                 # Task management components
│   ├── TaskList.tsx
│   ├── TaskItem.tsx
│   ├── TaskForm.tsx
│   ├── TaskFilter.tsx
│   └── EmptyState.tsx
│
└── layout/                # Layout components
    ├── Navbar.tsx
    ├── Header.tsx
    └── Footer.tsx
```

---

## Base UI Components

### Button

**File**: `components/ui/Button.tsx`
**Type**: Client Component

**Props**:
```typescript
interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
  onClick?: () => void
  className?: string
}
```

**Variants**:
| Variant | Use Case | Styling |
|---------|----------|---------|
| primary | Main actions (Submit, Save) | Blue background, white text |
| secondary | Secondary actions (Cancel) | Gray background |
| danger | Destructive actions (Delete) | Red background |
| ghost | Subtle actions | Transparent, text only |

**States**:
| State | Appearance |
|-------|------------|
| Default | Normal styling |
| Hover | Darker shade |
| Disabled | 50% opacity, no pointer |
| Loading | Spinner icon, disabled |

**Implementation**:
```typescript
'use client'

import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled,
  loading,
  type = 'button',
  onClick,
  className,
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={cn(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        {
          'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
          'bg-gray-200 text-gray-900 hover:bg-gray-300': variant === 'secondary',
          'bg-red-600 text-white hover:bg-red-700': variant === 'danger',
          'hover:bg-gray-100': variant === 'ghost',
          'h-8 px-3 text-sm': size === 'sm',
          'h-10 px-4 text-sm': size === 'md',
          'h-12 px-6 text-base': size === 'lg',
        },
        className
      )}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  )
}
```

---

### Input

**File**: `components/ui/Input.tsx`
**Type**: Client Component

**Props**:
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}
```

**States**:
| State | Border Color |
|-------|--------------|
| Default | Gray |
| Focus | Blue ring |
| Error | Red border |
| Disabled | Gray background |

**Implementation**:
```typescript
'use client'

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'
import { Label } from './Label'

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && <Label htmlFor={props.id}>{label}</Label>}
        <input
          ref={ref}
          className={cn(
            'flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm',
            'placeholder:text-gray-400',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error ? 'border-red-500' : 'border-gray-300',
            className
          )}
          {...props}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
    )
  }
)
Input.displayName = 'Input'
```

---

### Card

**File**: `components/ui/Card.tsx`
**Type**: Server Component

**Props**:
```typescript
interface CardProps {
  children: React.ReactNode
  className?: string
}
```

**Implementation**:
```typescript
import { cn } from '@/lib/utils'

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 bg-white p-4 shadow-sm',
        className
      )}
    >
      {children}
    </div>
  )
}
```

---

### Skeleton

**File**: `components/ui/Skeleton.tsx`
**Type**: Server Component

**Props**:
```typescript
interface SkeletonProps {
  className?: string
}
```

**Implementation**:
```typescript
import { cn } from '@/lib/utils'

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-gray-200',
        className
      )}
    />
  )
}
```

---

## Authentication Components

### LoginForm

**File**: `components/auth/LoginForm.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface LoginFormProps {
  onSuccess?: () => void
}
```

**State**:
```typescript
interface FormState {
  email: string
  password: string
  error: string | null
  loading: boolean
}
```

**Behavior**:
| Action | Result |
|--------|--------|
| Submit with valid credentials | Call `authApi.login()`, redirect on success |
| Submit with invalid credentials | Display error message |
| Submit with empty fields | Show validation errors |

**Implementation**:
```typescript
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authApi } from '@/lib/api'

export function LoginForm({ onSuccess }: LoginFormProps) {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    // Client-side validation
    if (!email || !password) {
      setError('Email and password are required')
      setLoading(false)
      return
    }

    const { data, error: apiError } = await authApi.login(email, password)

    if (apiError) {
      setError(apiError.message)
      setLoading(false)
      return
    }

    onSuccess?.()
    router.push('/tasks')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        id="email"
        type="email"
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        required
      />
      <Input
        id="password"
        type="password"
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="••••••••"
        required
      />
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
      <Button type="submit" loading={loading} className="w-full">
        Sign In
      </Button>
    </form>
  )
}
```

---

### RegisterForm

**File**: `components/auth/RegisterForm.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface RegisterFormProps {
  onSuccess?: () => void
}
```

**State**:
```typescript
interface FormState {
  email: string
  password: string
  confirmPassword: string
  errors: {
    email?: string
    password?: string
    confirmPassword?: string
    form?: string
  }
  loading: boolean
}
```

**Validation Rules**:
| Field | Rule | Error Message |
|-------|------|---------------|
| email | Required, valid format | "Valid email is required" |
| password | Required, min 8 chars | "Password must be at least 8 characters" |
| confirmPassword | Must match password | "Passwords do not match" |

**Implementation**:
```typescript
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authApi } from '@/lib/api'

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  function validate(): boolean {
    const newErrors: Record<string, string> = {}

    if (!email) {
      newErrors.email = 'Email is required'
    }
    if (!password) {
      newErrors.password = 'Password is required'
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    const { data, error } = await authApi.register(email, password)

    if (error) {
      setErrors({ form: error.message })
      setLoading(false)
      return
    }

    onSuccess?.()
    router.push('/tasks')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        id="email"
        type="email"
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        placeholder="you@example.com"
      />
      <Input
        id="password"
        type="password"
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={errors.password}
        placeholder="••••••••"
      />
      <Input
        id="confirmPassword"
        type="password"
        label="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        error={errors.confirmPassword}
        placeholder="••••••••"
      />
      {errors.form && (
        <p className="text-sm text-red-500">{errors.form}</p>
      )}
      <Button type="submit" loading={loading} className="w-full">
        Create Account
      </Button>
    </form>
  )
}
```

---

### LogoutButton

**File**: `components/auth/LogoutButton.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface LogoutButtonProps {
  className?: string
}
```

**Behavior**:
1. Clear auth session (Better Auth handles this)
2. Redirect to `/login`

**Implementation**:
```typescript
'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { signOut } from '@/lib/auth'

export function LogoutButton({ className }: LogoutButtonProps) {
  const router = useRouter()

  async function handleLogout() {
    await signOut()
    router.push('/login')
  }

  return (
    <Button variant="ghost" onClick={handleLogout} className={className}>
      Logout
    </Button>
  )
}
```

---

## Task Components

### TaskList

**File**: `components/tasks/TaskList.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface TaskListProps {
  initialTasks: Task[]
}
```

**State**:
```typescript
interface State {
  tasks: Task[]
  filter: 'all' | 'active' | 'completed'
  loading: boolean
}
```

**Computed Values**:
```typescript
const filteredTasks = tasks.filter(task => {
  if (filter === 'active') return !task.completed
  if (filter === 'completed') return task.completed
  return true
})

const taskCount = filteredTasks.length
```

**Implementation**:
```typescript
'use client'

import { useState } from 'react'
import { TaskItem } from './TaskItem'
import { TaskFilter } from './TaskFilter'
import { EmptyState } from './EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { taskApi } from '@/lib/api'
import type { Task } from '@/lib/types'

export function TaskList({ initialTasks }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed
    if (filter === 'completed') return task.completed
    return true
  })

  async function handleToggle(taskId: string) {
    const task = tasks.find(t => t.id === taskId)
    if (!task) return

    // Optimistic update
    setTasks(tasks.map(t =>
      t.id === taskId ? { ...t, completed: !t.completed } : t
    ))

    const { error } = await taskApi.updateTask(taskId, {
      completed: !task.completed
    })

    // Revert on error
    if (error) {
      setTasks(tasks.map(t =>
        t.id === taskId ? { ...t, completed: task.completed } : t
      ))
    }
  }

  async function handleDelete(taskId: string) {
    // Optimistic update
    setTasks(tasks.filter(t => t.id !== taskId))

    const { error } = await taskApi.deleteTask(taskId)

    // Revert on error (would need to refetch)
    if (error) {
      // Refetch tasks
      const { data } = await taskApi.getTasks()
      if (data) setTasks(data.tasks)
    }
  }

  function handleTaskCreated(task: Task) {
    setTasks([task, ...tasks])
  }

  return (
    <div className="space-y-4">
      <TaskFilter
        filter={filter}
        onFilterChange={setFilter}
        taskCount={filteredTasks.length}
      />

      {filteredTasks.length === 0 ? (
        <EmptyState filter={filter} />
      ) : (
        <div className="space-y-2">
          {filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={handleToggle}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

---

### TaskItem

**File**: `components/tasks/TaskItem.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface TaskItemProps {
  task: Task
  onToggle: (id: string) => void
  onDelete: (id: string) => void
}
```

**States**:
| State | Visual |
|-------|--------|
| Default | Normal styling |
| Completed | Strikethrough title, muted colors |
| Hover | Show delete button |
| Deleting | Disabled, faded |

**Layout**:
```
┌───────────────────────────────────────────────────┐
│ [○/●] Title of the task                      [✕] │
│       Optional description text                   │
└───────────────────────────────────────────────────┘
```

**Implementation**:
```typescript
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import type { Task } from '@/lib/types'

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  const [deleting, setDeleting] = useState(false)

  async function handleDelete() {
    setDeleting(true)
    await onDelete(task.id)
  }

  return (
    <Card
      className={cn(
        'flex items-start gap-3 transition-opacity',
        deleting && 'opacity-50 pointer-events-none'
      )}
    >
      {/* Completion toggle */}
      <button
        onClick={() => onToggle(task.id)}
        className={cn(
          'mt-1 h-5 w-5 rounded-full border-2 flex-shrink-0',
          'transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500',
          task.completed
            ? 'bg-blue-600 border-blue-600'
            : 'border-gray-300 hover:border-blue-400'
        )}
        aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
      >
        {task.completed && (
          <svg className="h-full w-full text-white" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
            />
          </svg>
        )}
      </button>

      {/* Task content */}
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            'text-sm font-medium',
            task.completed && 'line-through text-gray-400'
          )}
        >
          {task.title}
        </p>
        {task.description && (
          <p
            className={cn(
              'text-sm text-gray-500 mt-1',
              task.completed && 'line-through'
            )}
          >
            {task.description}
          </p>
        )}
      </div>

      {/* Delete button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={handleDelete}
        disabled={deleting}
        className="text-gray-400 hover:text-red-500"
        aria-label="Delete task"
      >
        ✕
      </Button>
    </Card>
  )
}
```

---

### TaskForm

**File**: `components/tasks/TaskForm.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface TaskFormProps {
  onTaskCreated: (task: Task) => void
}
```

**State**:
```typescript
interface FormState {
  title: string
  error: string | null
  loading: boolean
}
```

**Validation**:
| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required, non-empty | "Title is required" |
| title | Max 500 chars | "Title is too long" |

**Implementation**:
```typescript
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { taskApi } from '@/lib/api'
import type { Task } from '@/lib/types'

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    const trimmedTitle = title.trim()
    if (!trimmedTitle) {
      setError('Title is required')
      return
    }

    setLoading(true)
    const { data, error: apiError } = await taskApi.createTask({
      title: trimmedTitle
    })

    setLoading(false)

    if (apiError) {
      setError(apiError.message)
      return
    }

    if (data) {
      onTaskCreated(data)
      setTitle('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="flex-1">
        <Input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a new task..."
          error={error ?? undefined}
          maxLength={500}
        />
      </div>
      <Button type="submit" loading={loading}>
        Add Task
      </Button>
    </form>
  )
}
```

---

### TaskFilter

**File**: `components/tasks/TaskFilter.tsx`
**Type**: Client Component (`"use client"`)

**Props**:
```typescript
interface TaskFilterProps {
  filter: 'all' | 'active' | 'completed'
  onFilterChange: (filter: 'all' | 'active' | 'completed') => void
  taskCount: number
}
```

**Implementation**:
```typescript
'use client'

import { cn } from '@/lib/utils'

const filters = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
] as const

export function TaskFilter({ filter, onFilterChange, taskCount }: TaskFilterProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex gap-1">
        {filters.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => onFilterChange(value)}
            className={cn(
              'px-3 py-1 text-sm rounded-md transition-colors',
              filter === value
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            )}
          >
            {label}
          </button>
        ))}
      </div>
      <span className="text-sm text-gray-500">
        {taskCount} {taskCount === 1 ? 'task' : 'tasks'}
      </span>
    </div>
  )
}
```

---

### EmptyState

**File**: `components/tasks/EmptyState.tsx`
**Type**: Server Component

**Props**:
```typescript
interface EmptyStateProps {
  filter: 'all' | 'active' | 'completed'
}
```

**Messages**:
| Filter | Message |
|--------|---------|
| all | "No tasks yet. Add your first task above!" |
| active | "No active tasks. Great job!" |
| completed | "No completed tasks yet." |

**Implementation**:
```typescript
const messages = {
  all: {
    title: 'No tasks yet',
    description: 'Add your first task above to get started!',
  },
  active: {
    title: 'No active tasks',
    description: 'Great job! All your tasks are completed.',
  },
  completed: {
    title: 'No completed tasks',
    description: 'Complete a task to see it here.',
  },
}

export function EmptyState({ filter }: EmptyStateProps) {
  const { title, description } = messages[filter]

  return (
    <div className="text-center py-12">
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
    </div>
  )
}
```

---

## Layout Components

### Navbar

**File**: `components/layout/Navbar.tsx`
**Type**: Server Component (with client logout button)

**Props**:
```typescript
interface NavbarProps {
  user?: { email: string }
}
```

**Layout**:
```
┌──────────────────────────────────────────────────────┐
│  Evolution of Todo                    user@email.com │
│                                             [Logout] │
└──────────────────────────────────────────────────────┘
```

**Implementation**:
```typescript
import { LogoutButton } from '@/components/auth/LogoutButton'

export function Navbar({ user }: NavbarProps) {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-3xl px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">
            Evolution of Todo
          </h1>
          {user && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <LogoutButton />
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
```

---

## TypeScript Types

**File**: `lib/types.ts`

```typescript
// User types
export interface User {
  id: string
  email: string
  created_at: string
}

// Task types
export interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string | null
  completed?: boolean
}

// API types
export interface ApiError {
  code: string
  message: string
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
}

// Auth types
export interface AuthResponse {
  user: User
  token: string
}
```

---

## Component Acceptance Criteria

### Base Components

- [ ] **AC-COMP-001**: Button shows loading spinner when `loading=true`
- [ ] **AC-COMP-002**: Button is disabled when `disabled=true` or `loading=true`
- [ ] **AC-COMP-003**: Input shows error message when `error` prop is set
- [ ] **AC-COMP-004**: Skeleton animates with pulse effect

### Auth Components

- [ ] **AC-COMP-005**: LoginForm validates required fields
- [ ] **AC-COMP-006**: LoginForm shows error on invalid credentials
- [ ] **AC-COMP-007**: RegisterForm validates password match
- [ ] **AC-COMP-008**: RegisterForm validates password length
- [ ] **AC-COMP-009**: LogoutButton clears session and redirects

### Task Components

- [ ] **AC-COMP-010**: TaskList renders all tasks
- [ ] **AC-COMP-011**: TaskList filters by completion status
- [ ] **AC-COMP-012**: TaskItem toggles completion on click
- [ ] **AC-COMP-013**: TaskItem shows delete button
- [ ] **AC-COMP-014**: TaskForm validates non-empty title
- [ ] **AC-COMP-015**: TaskFilter highlights active filter
- [ ] **AC-COMP-016**: EmptyState shows appropriate message per filter

---

## References

- @specs/ui/pages.md - Frontend specification (pages, flows, API client)
- @specs/api/rest-endpoints.md - API contract
- @specs/features/authentication.md - Authentication specification
