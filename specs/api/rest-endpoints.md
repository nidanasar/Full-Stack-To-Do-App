# REST API Endpoints

## Base URL
`/api/v1`

## Authentication

### POST /auth/register
Create a new user account.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:** `201 Created`
```json
{
  "user": { "id": "string", "email": "string" },
  "token": "string"
}
```

### POST /auth/login
Authenticate user.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "user": { "id": "string", "email": "string" },
  "token": "string"
}
```

## Tasks (Protected)

### GET /tasks
Get all tasks for authenticated user.

**Response:** `200 OK`
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "description": "string | null",
      "completed": "boolean",
      "createdAt": "string",
      "updatedAt": "string"
    }
  ]
}
```

### POST /tasks
Create a new task.

**Request Body:**
```json
{
  "title": "string",
  "description": "string | null"
}
```

**Response:** `201 Created`

### PATCH /tasks/:id
Update a task.

**Request Body:**
```json
{
  "title": "string",
  "description": "string | null",
  "completed": "boolean"
}
```

**Response:** `200 OK`

### DELETE /tasks/:id
Delete a task.

**Response:** `204 No Content`

## Error Responses
```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```
