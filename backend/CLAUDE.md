# Backend Guidelines (FastAPI + SQLModel)

## Stack
- **Framework**: FastAPI with async support
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon PostgreSQL (asyncpg driver)
- **Auth**: python-jose for JWT, passlib[bcrypt] for password hashing
- **Config**: pydantic-settings for environment variables

## Project Structure
```
backend/
├── main.py           # FastAPI app, CORS, lifespan, routers
├── config.py         # Settings class (DATABASE_URL, BETTER_AUTH_SECRET)
├── database.py       # Async engine, session factory
├── models.py         # User, Task SQLModels
├── schemas.py        # Pydantic request/response schemas
├── auth.py           # password_hash, password_verify, JWT utils
├── dependencies.py   # get_db, get_current_user
├── exceptions.py     # Custom exceptions, error handlers
├── routes/
│   ├── __init__.py   # Router exports
│   ├── auth.py       # POST /auth/register, /auth/login
│   └── tasks.py      # Task CRUD endpoints
├── tests/
│   ├── conftest.py   # Async test fixtures
│   ├── test_auth.py  # Auth endpoint tests
│   └── test_tasks.py # Task CRUD + isolation tests
├── pyproject.toml    # Dependencies (uv/pip)
├── .env.example      # Environment template
└── .gitignore
```

## API Endpoints

### Authentication (Public)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user, returns JWT |
| POST | `/api/v1/auth/login` | Login user, returns JWT |

### Tasks (JWT Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List user's tasks (filterable) |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get single task |
| PUT | `/api/v1/tasks/{id}` | Full update |
| PATCH | `/api/v1/tasks/{id}` | Partial update |
| DELETE | `/api/v1/tasks/{id}` | Delete task (204) |

## Key Implementation Details

### Authentication Flow
1. JWT extracted from `Authorization: Bearer <token>` header
2. Token validated with `BETTER_AUTH_SECRET` (shared with frontend)
3. User ID extracted from JWT `sub` claim
4. All task queries filtered by `user_id` from token

### User Isolation
- **Critical**: User ID NEVER comes from request body/URL
- All task operations use `WHERE user_id = current_user.id`
- Accessing another user's task returns 404 (not 403) to prevent enumeration

### Error Response Format
```json
{"error": {"code": "UNAUTHORIZED", "message": "Invalid credentials"}}
```

### Status Codes
- 200: Success
- 201: Created
- 204: No Content (delete)
- 401: Unauthorized (auth errors)
- 404: Not Found (also for wrong user's resources)
- 409: Conflict (duplicate email)
- 422: Validation Error

## Development Commands
```bash
# Install dependencies
uv sync --all-extras

# Run development server
uv run uvicorn main:app --reload --port 8000

# Run tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

## Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
BETTER_AUTH_SECRET=shared-secret-with-frontend
BETTER_AUTH_URL=http://localhost:3000
ENVIRONMENT=development
```

## Testing Notes
- Tests use SQLite in-memory database (aiosqlite)
- Fixtures provide test users, tokens, and auth headers
- User isolation tests verify cross-user access is blocked
