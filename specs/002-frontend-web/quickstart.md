# Quickstart: Frontend Web Application

**Feature**: 002-frontend-web
**Date**: 2026-01-15

---

## Prerequisites

- Node.js 18+ installed
- Backend API running at localhost:8000 (see 001-backend-api)
- npm or pnpm package manager

---

## Setup

### 1. Create Next.js Project

```bash
cd /mnt/c/Users/nida.nasarr/Desktop/fullstack-app/hackathon-todo

# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd frontend
```

### 2. Install Dependencies

```bash
npm install better-auth lucide-react
```

### 3. Environment Setup

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
BETTER_AUTH_SECRET=<same-secret-as-backend>
```

---

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── tasks/
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Skeleton.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── FilterTabs.tsx
│   └── lib/
│       ├── api.ts
│       ├── auth.ts
│       └── utils.ts
├── middleware.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Run Development Server

```bash
# Terminal 1: Backend (from backend/)
cd backend
uv run uvicorn main:app --reload --port 8000

# Terminal 2: Frontend (from frontend/)
cd frontend
npm run dev
```

Frontend: http://localhost:3000
Backend API: http://localhost:8000/docs

---

## Verification Checklist

### Auth Flow

```bash
# 1. Navigate to http://localhost:3000
# Should redirect to /login

# 2. Click "Register" link
# Should navigate to /register

# 3. Fill registration form:
#    Email: test@example.com
#    Password: password123
#    Confirm: password123
# Should redirect to /tasks after success

# 4. Logout
# Should redirect to /login

# 5. Login with same credentials
# Should redirect to /tasks
```

### Task Operations

```bash
# 1. On /tasks page, add a new task:
#    Title: "My first task"
# Task should appear in list

# 2. Click checkbox to toggle completion
# Task should show as completed

# 3. Click delete button
# Task should be removed

# 4. Refresh page
# State should persist
```

### Responsive Design

```bash
# 1. Open DevTools (F12)
# 2. Toggle device toolbar (Ctrl+Shift+M)
# 3. Test at:
#    - Mobile: 375px width
#    - Tablet: 768px width
#    - Desktop: 1024px width
# UI should adapt appropriately
```

---

## Common Issues

### CORS Errors

If you see CORS errors, ensure backend has frontend origin in allowed origins:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    ...
)
```

### Session Not Persisting

Ensure cookies are being sent:

```typescript
// lib/api.ts
fetch(url, {
  credentials: 'include',  // Required for httpOnly cookies
  ...
})
```

### API Connection Failed

Check backend is running and accessible:

```bash
curl http://localhost:8000/api/v1/auth/login -I
# Should return 405 (Method Not Allowed) not connection error
```

---

## References

- @specs/002-frontend-web/spec.md - Feature specification
- @specs/002-frontend-web/research.md - Technical decisions
- @specs/ui/pages.md - UI layouts
- @specs/ui/components.md - Component specs
