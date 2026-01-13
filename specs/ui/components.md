# UI Components

## Core Components

### TaskItem
Displays a single task with actions.

**Props:**
- `task: Task` - Task data object
- `onToggle: (id: string) => void` - Toggle completion
- `onDelete: (id: string) => void` - Delete task
- `onEdit: (id: string) => void` - Edit task

**States:**
- Default: Normal display
- Completed: Strikethrough styling
- Hover: Show action buttons

### TaskList
Container for rendering multiple tasks.

**Props:**
- `tasks: Task[]` - Array of tasks
- `filter: 'all' | 'active' | 'completed'` - Current filter

### TaskForm
Form for creating/editing tasks.

**Props:**
- `onSubmit: (task: TaskInput) => void` - Submit handler
- `initialData?: Task` - For edit mode

**Fields:**
- Title (required)
- Description (optional)

### AuthForm
Shared form for login/register.

**Props:**
- `mode: 'login' | 'register'` - Form mode
- `onSubmit: (credentials: Credentials) => void`

### Header
App header with navigation.

**Elements:**
- Logo/App name
- User info (when logged in)
- Logout button (when logged in)

### FilterTabs
Task filter controls.

**Options:**
- All
- Active
- Completed
