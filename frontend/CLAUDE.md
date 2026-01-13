<!-- # Frontend Package - Claude Instructions

## Package Overview
React-based frontend for the hackathon-todo application.

## Technology Stack
- React 18+
- TypeScript
- React Router for navigation
- Fetch/Axios for API calls

## Key Directories
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Route pages
│   ├── hooks/         # Custom React hooks
│   ├── context/       # React Context providers
│   ├── services/      # API service functions
│   ├── types/         # TypeScript types
│   └── utils/         # Utility functions
├── public/
└── package.json
```

## Development Commands
```bash
npm run dev      # Start development server
npm run build    # Production build
npm run test     # Run tests
npm run lint     # Lint code
```

## Conventions
- Components use PascalCase
- Hooks prefixed with `use`
- API calls go through services/
- State management via Context API
- CSS Modules or Tailwind for styling

## API Integration
- Base URL from environment variable
- JWT token stored in localStorage
- Automatic token injection in requests
- Error handling with user-friendly messages -->

# Frontend Guidelines (Next.js 16+ App Router)

## Stack
- Next.js 16+, TypeScript, Tailwind CSS, Better Auth (JWT mode)

## Patterns
- Server Components default
- Client Components ('use client') for forms/interactivity
- API calls via `/lib/api.ts` (with auth headers)

## Structure
- /app: Pages (/tasks, /auth/signin, /auth/signup)
- /components: UI (TaskList, TaskForm)
- /lib/api.ts: API client with JWT fetch

## Auth Flow
- Use Better Auth: Enable JWT plugin
- On login: Get token, store in cookies/headers
- API calls: `Authorization: Bearer ${token}`

## Styling
Tailwind only. Responsive (mobile-first).

API Client Example:
```ts
export const api = {
  async getTasks(userId: string) {
    const token = getSessionToken(); // From Better Auth
    return fetch(`/api/${userId}/tasks`, { headers: { Authorization: `Bearer ${token}` } });
  }
};
