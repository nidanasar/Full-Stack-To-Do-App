# UI Pages

## Page Structure

### / (Home/Dashboard)
**Route:** `/`
**Auth Required:** Yes

**Layout:**
```
┌─────────────────────────────────┐
│           Header                │
├─────────────────────────────────┤
│        TaskForm (Add)           │
├─────────────────────────────────┤
│         FilterTabs              │
├─────────────────────────────────┤
│                                 │
│          TaskList               │
│                                 │
└─────────────────────────────────┘
```

**Features:**
- Add new task
- View all tasks
- Filter tasks
- Toggle/edit/delete tasks

### /login
**Route:** `/login`
**Auth Required:** No (redirect if logged in)

**Layout:**
```
┌─────────────────────────────────┐
│         App Logo                │
├─────────────────────────────────┤
│         AuthForm                │
│        (login mode)             │
├─────────────────────────────────┤
│    Link to /register            │
└─────────────────────────────────┘
```

### /register
**Route:** `/register`
**Auth Required:** No (redirect if logged in)

**Layout:**
```
┌─────────────────────────────────┐
│         App Logo                │
├─────────────────────────────────┤
│         AuthForm                │
│       (register mode)           │
├─────────────────────────────────┤
│      Link to /login             │
└─────────────────────────────────┘
```

## Routing
- Protected routes redirect to `/login` if not authenticated
- Auth pages redirect to `/` if already authenticated
- 404 page for unknown routes
