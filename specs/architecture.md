# Architecture Overview

## System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│   (React)   │◀────│   (Node)    │◀────│  (SQLite)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Technology Stack

### Frontend
- Framework: React
- State Management: React Context/useState
- Styling: CSS Modules or Tailwind

### Backend
- Runtime: Node.js
- Framework: Express.js
- Authentication: JWT

### Database
- Development: SQLite
- ORM: Prisma or Drizzle

## Monorepo Structure
- Shared types between frontend and backend
- Independent deployment capability
- Unified development scripts
