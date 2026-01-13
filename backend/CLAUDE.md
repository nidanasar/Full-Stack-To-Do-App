<!-- # Backend Package - Claude Instructions

## Package Overview
Node.js/Express backend API for the hackathon-todo application.

## Technology Stack
- Node.js 18+
- Express.js
- TypeScript
- Prisma ORM
- SQLite (development)
- JWT for authentication
- bcrypt for password hashing

## Key Directories
```
backend/
├── src/
│   ├── routes/        # API route handlers
│   ├── controllers/   # Business logic
│   ├── middleware/    # Express middleware
│   ├── services/      # Data access layer
│   ├── utils/         # Utility functions
│   └── types/         # TypeScript types
├── prisma/
│   └── schema.prisma  # Database schema
└── package.json
```

## Development Commands
```bash
npm run dev           # Start with hot reload
npm run build         # Compile TypeScript
npm run start         # Run production build
npm run db:migrate    # Run Prisma migrations
npm run db:studio     # Open Prisma Studio
npm run test          # Run tests
```

## Environment Variables
```
DATABASE_URL=file:./dev.db
JWT_SECRET=your-secret-key
PORT=3001
```

## API Conventions
- RESTful endpoints under `/api/v1`
- JSON request/response bodies
- Standard HTTP status codes
- Error responses include code and message
- Protected routes require Bearer token -->


### `backend/CLAUDE.md`
```markdown
# Backend Guidelines (FastAPI + SQLModel)

## Stack
- FastAPI, SQLModel, psycopg (async), python-jose[cryptography] for JWT
- DATABASE_URL from .env

## Structure
- main.py: App + middleware
- models.py: SQLModel (Task, User FK)
- crud.py: DB ops
- routes/tasks.py: APIRouter
- deps.py: JWT verify + get_current_user
- db.py: engine/session

## Auth Middleware
- Dependency: Verify JWT from Authorization header
- Shared secret: BETTER_AUTH_SECRET
- Extract user_id from token, validate path user_id == token user_id
- pyjwt or python-jose

## API Conventions
- Prefix /api
- Pydantic models for req/res
- Filter all by current_user.id
- HTTPException for 401/403/404

Example Dep:
```python
from fastapi import Depends, HTTPException
from jose import jwt, JWTError

def get_current_user(token: str = Header()) -> str:
    try:
        payload = jwt.decode(token.replace("Bearer ", ""), BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload["sub"]  # user_id
    except JWTError:
        raise HTTPException(401)
