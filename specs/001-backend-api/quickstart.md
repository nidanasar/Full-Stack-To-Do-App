# Quickstart: Backend API

**Feature**: 001-backend-api
**Date**: 2026-01-13

---

## Prerequisites

- Python 3.13+
- UV package manager
- Neon PostgreSQL database
- Environment variables configured

---

## Environment Setup

Create `.env` file in `backend/` directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-shared-secret-key
ENVIRONMENT=development
```

---

## Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies with UV
uv sync

# Or with pip
pip install -r requirements.txt
```

---

## Running the Server

```bash
# Development mode with auto-reload
uv run uvicorn main:app --reload --port 8000

# Production mode
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## API Endpoints

### Authentication (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get JWT token |

### Tasks (Protected - requires JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List all tasks |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get single task |
| PUT | `/api/v1/tasks/{id}` | Update task (full) |
| PATCH | `/api/v1/tasks/{id}` | Update task (partial) |
| DELETE | `/api/v1/tasks/{id}` | Delete task |

---

## Quick Test

### 1. Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Login and get token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 3. Create a task (use token from step 2)

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"title": "My first task", "description": "Test description"}'
```

### 4. List tasks

```bash
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

---

## API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_tasks.py -v
```

---

## Project Structure

```
backend/
├── main.py           # FastAPI app entry
├── config.py         # Settings
├── database.py       # Async DB connection
├── models.py         # SQLModel entities
├── schemas.py        # Pydantic schemas
├── auth.py           # JWT & password utils
├── routes/
│   ├── auth.py       # Auth endpoints
│   └── tasks.py      # Task endpoints
├── dependencies.py   # FastAPI deps
├── exceptions.py     # Error handlers
├── tests/
│   ├── conftest.py   # Test fixtures
│   ├── test_auth.py  # Auth tests
│   └── test_tasks.py # Task tests
├── pyproject.toml    # Dependencies
└── .env              # Environment vars
```

---

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Verify DATABASE_URL and Neon server is accessible.

### JWT Validation Error

```
{"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}}
```

**Solution**: Ensure BETTER_AUTH_SECRET matches frontend configuration.

### CORS Error

```
Access-Control-Allow-Origin header missing
```

**Solution**: CORS is configured in main.py - verify frontend origin is allowed.

---

## References

- @specs/001-backend-api/spec.md - Feature specification
- @specs/api/rest-endpoints.md - API contract
- @specs/database/schema.md - Database schema
