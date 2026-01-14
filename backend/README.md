# Hackathon Todo Backend

FastAPI backend for the Phase II Todo application with JWT authentication and Neon PostgreSQL.

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Install dependencies
uv sync --all-extras

# Run development server
uv run uvicorn main:app --reload --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT

### Tasks (JWT Required)
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task (full)
- `PATCH /api/v1/tasks/{id}` - Update task (partial)
- `DELETE /api/v1/tasks/{id}` - Delete task

## Testing

```bash
uv run pytest -v
```
