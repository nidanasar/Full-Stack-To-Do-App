<!-- # Hackathon Todo - Monorepo Instructions

## Project Overview
A full-stack todo application built as a monorepo with separate frontend and backend packages.

## Repository Structure
```
hackathon-todo/
├── .spec-kit/          # Spec-Kit configuration
├── specs/              # Project specifications
│   ├── overview.md     # Project overview
│   ├── architecture.md # System architecture
│   ├── features/       # Feature specifications
│   ├── api/            # API documentation
│   ├── database/       # Database schema
│   └── ui/             # UI specifications
├── frontend/           # React frontend application
├── backend/            # Node.js backend API
└── README.md           # Project readme
```

## Quick Start
```bash
# Install dependencies for all packages
npm install

# Start development servers
npm run dev

# Run tests
npm run test
```

## Packages
- **frontend/** - React application (see frontend/CLAUDE.md)
- **backend/** - Express API server (see backend/CLAUDE.md)

## Development Guidelines
- Follow specs in `specs/` directory
- Keep frontend and backend changes in sync
- Update API specs when endpoints change
- Write tests for new features

## Specifications Reference
- Feature specs: `specs/features/`
- API contracts: `specs/api/rest-endpoints.md`
- Database schema: `specs/database/schema.md`
- UI components: `specs/ui/` -->

# Todo App - Hackathon II (Phase II: Full-Stack Web App)

## Project Overview
Monorepo for spec-driven development. Transform Phase I console app to multi-user web app with Neon DB + Better Auth + JWT.

## Spec-Kit Structure
- @specs/overview.md: Overview
- @specs/features/: Features (e.g., @specs/features/task-crud.md)
- @specs/api/: API (e.g., @specs/api/rest-endpoints.md)
- @specs/database/: DB (e.g., @specs/database/schema.md)
- @specs/ui/: UI (e.g., @specs/ui/pages.md)
- specs/history/phase2/: Spec iterations

Always reference specs with @specs/path.md before implementing.

## Project Structure
- /frontend: Next.js 16+ App Router, TS, Tailwind, Better Auth
- /backend: FastAPI, SQLModel, Neon Postgres
- docker-compose.yml: Run both services

## Workflow
1. Read spec: e.g., "@specs/features/task-crud.md"
2. Generate plan: "Plan implementation for this spec"
3. Break into tasks: Backend first, then frontend
4. Implement: Edit files per backend/CLAUDE.md or frontend/CLAUDE.md
5. Test: Frontend `npm run dev`, Backend `uvicorn main:app --reload --port 8000`
6. Save iterations to specs/history/phase2/

## Commands
- Both: `docker-compose up`
- Frontend only: `cd frontend && npm run dev`
- Backend only: `cd backend && uv run uvicorn main:app --reload --port 8000`

## Recent Changes
- 001-backend-api: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
