# Authentication Specification — Phase II

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Status**: Ratified

## Purpose

Define the authentication and authorization model for Phase II, ensuring secure multi-user access with strict data isolation.

This specification governs how users identify themselves (authentication) and what resources they can access (authorization).

---

## Overview

User authentication system for personalized task management with JWT-based stateless authorization.

---

## Auth Strategy

| Aspect | Implementation |
|--------|----------------|
| Authentication | Better Auth (frontend session management) |
| Authorization | JWT validation (backend enforcement) |
| Session Model | Stateless (no server-side sessions) |
| Token Storage | Secure httpOnly cookie (frontend) |

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │     │  Better Auth │     │   FastAPI   │
│   (Client)  │────▶│  (Frontend)  │────▶│  (Backend)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                    │
       │   Credentials     │     JWT Token      │
       │──────────────────▶│───────────────────▶│
       │                   │                    │
       │                   │     Validate       │
       │                   │     Signature      │
       │                   │     + Expiry       │
       │                   │     + user_id      │
       │                   │                    │
       │◀──────────────────│◀───────────────────│
       │      Response     │      Response      │
```

---

## Token Standard

### JWT Configuration

| Property | Value |
|----------|-------|
| Token Type | JSON Web Token (JWT) |
| Algorithm | HS256 (HMAC-SHA256) |
| Secret Key | `BETTER_AUTH_SECRET` environment variable |
| Transport | `Authorization: Bearer <jwt>` header |
| Expiration | 7 days (604800 seconds) |

### JWT Claims

| Claim | Type | Description | Required |
|-------|------|-------------|----------|
| `sub` | string (UUID) | User ID (primary identifier) | Yes |
| `exp` | number | Token expiration (Unix timestamp) | Yes |
| `iat` | number | Token issued-at (Unix timestamp) | Yes |

### Example Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1705276800,
  "iat": 1704672000
}
```

### Token Validation Order

```
1. Check token present in Authorization header
   └─ Missing → 401 Unauthorized

2. Decode and verify signature (BETTER_AUTH_SECRET)
   └─ Invalid signature → 401 Unauthorized

3. Check expiration claim (exp)
   └─ Expired → 401 Unauthorized

4. Extract user_id from sub claim
   └─ Use for all subsequent queries
```

---

## User Stories

### Sign Up (Priority: P1)

**As a visitor**, I can create an account with email and password so that I can manage my personal tasks.

**Acceptance Scenarios**:

1. **Given** I am on the signup page, **When** I submit valid email and password (8+ chars), **Then** my account is created and I am logged in automatically
2. **Given** I submit an email that already exists, **When** I click signup, **Then** I see an error "Email already registered"
3. **Given** I submit a password less than 8 characters, **When** I click signup, **Then** I see a validation error

**Independent Test**: Can be tested by submitting signup form and verifying JWT is returned and user can access dashboard.

---

### Login (Priority: P1)

**As a user**, I can log in with my credentials so that I can access my tasks.

**Acceptance Scenarios**:

1. **Given** I have an account, **When** I submit correct credentials, **Then** I receive a JWT and am redirected to dashboard
2. **Given** I submit incorrect password, **When** I click login, **Then** I see generic error "Invalid credentials" (no password hints)
3. **Given** I submit non-existent email, **When** I click login, **Then** I see generic error "Invalid credentials" (prevents enumeration)

**Independent Test**: Can be tested by logging in with valid credentials and verifying protected route access.

---

### Logout (Priority: P2)

**As a user**, I can log out from my account so that my session is secure on shared devices.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I click logout, **Then** my session is cleared and I am redirected to login
2. **Given** I have logged out, **When** I try to access a protected route, **Then** I am redirected to login

**Independent Test**: Can be tested by logging out and verifying 401 on subsequent API calls.

---

### Session Persistence (Priority: P2)

**As a user**, I remain logged in across browser sessions so that I don't have to re-authenticate frequently.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I close and reopen the browser, **Then** I am still logged in (until token expires)
2. **Given** my token has expired, **When** I try to access a protected route, **Then** I am redirected to login

---

## Authentication Flows

### Login Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────┐
│  User    │     │   Frontend   │     │   Backend    │     │  Neon  │
│ Browser  │     │  Better Auth │     │   FastAPI    │     │Postgres│
└────┬─────┘     └──────┬───────┘     └──────┬───────┘     └───┬────┘
     │                  │                    │                 │
     │ 1. Submit login  │                    │                 │
     │     form         │                    │                 │
     │─────────────────▶│                    │                 │
     │                  │                    │                 │
     │                  │ 2. POST /api/v1/   │                 │
     │                  │    auth/login      │                 │
     │                  │───────────────────▶│                 │
     │                  │                    │                 │
     │                  │                    │ 3. Query user   │
     │                  │                    │    by email     │
     │                  │                    │────────────────▶│
     │                  │                    │                 │
     │                  │                    │ 4. User record  │
     │                  │                    │◀────────────────│
     │                  │                    │                 │
     │                  │                    │ 5. Verify       │
     │                  │                    │    bcrypt hash  │
     │                  │                    │                 │
     │                  │                    │ 6. Generate JWT │
     │                  │                    │    (sub, exp,   │
     │                  │                    │     iat)        │
     │                  │                    │                 │
     │                  │ 7. Return JWT      │                 │
     │                  │◀───────────────────│                 │
     │                  │                    │                 │
     │ 8. Store JWT in  │                    │                 │
     │    httpOnly      │                    │                 │
     │    cookie        │                    │                 │
     │◀─────────────────│                    │                 │
     │                  │                    │                 │
     │ 9. Redirect to   │                    │                 │
     │    /dashboard    │                    │                 │
     │◀─────────────────│                    │                 │
```

### Signup Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────┐
│  User    │     │   Frontend   │     │   Backend    │     │  Neon  │
│ Browser  │     │  Better Auth │     │   FastAPI    │     │Postgres│
└────┬─────┘     └──────┬───────┘     └──────┬───────┘     └───┬────┘
     │                  │                    │                 │
     │ 1. Submit signup │                    │                 │
     │     form         │                    │                 │
     │─────────────────▶│                    │                 │
     │                  │                    │                 │
     │                  │ 2. POST /api/v1/   │                 │
     │                  │    auth/register   │                 │
     │                  │───────────────────▶│                 │
     │                  │                    │                 │
     │                  │                    │ 3. Check email  │
     │                  │                    │    uniqueness   │
     │                  │                    │────────────────▶│
     │                  │                    │                 │
     │                  │                    │ 4. Email status │
     │                  │                    │◀────────────────│
     │                  │                    │                 │
     │                  │                    │ 5. Hash password│
     │                  │                    │    (bcrypt)     │
     │                  │                    │                 │
     │                  │                    │ 6. Insert user  │
     │                  │                    │────────────────▶│
     │                  │                    │                 │
     │                  │                    │ 7. User created │
     │                  │                    │◀────────────────│
     │                  │                    │                 │
     │                  │                    │ 8. Generate JWT │
     │                  │                    │                 │
     │                  │ 9. Return JWT      │                 │
     │                  │◀───────────────────│                 │
     │                  │                    │                 │
     │ 10. Store JWT    │                    │                 │
     │     + redirect   │                    │                 │
     │◀─────────────────│                    │                 │
```

### Logout Flow

```
┌──────────┐     ┌──────────────┐
│  User    │     │   Frontend   │
│ Browser  │     │  Better Auth │
└────┬─────┘     └──────┬───────┘
     │                  │
     │ 1. Click logout  │
     │─────────────────▶│
     │                  │
     │                  │ 2. Clear session
     │                  │    (delete cookie)
     │                  │
     │ 3. Redirect to   │
     │    /login        │
     │◀─────────────────│
     │                  │
     │ Note: Backend    │
     │ remains stateless│
     │ (no invalidation)│
```

---

## Authorization Rules

### Endpoint Protection

Every protected endpoint requires a valid JWT in the `Authorization` header.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Backend Validation Requirements

The backend **MUST** validate on every protected request:

| Check | Description | Failure |
|-------|-------------|---------|
| Token Present | Authorization header exists | 401 Unauthorized |
| Valid Signature | Token signed with BETTER_AUTH_SECRET | 401 Unauthorized |
| Not Expired | `exp` claim > current time | 401 Unauthorized |
| User Exists | `sub` claim matches a user in database | 401 Unauthorized |

### User Isolation Rules

| Condition | Response | Rationale |
|-----------|----------|-----------|
| No token | `401 Unauthorized` | Authentication required |
| Invalid/expired token | `401 Unauthorized` | Re-authentication required |
| Token user ≠ resource owner | `404 Not Found` | Prevents user enumeration |

**Critical**: Return 404 (not 403) when a user tries to access another user's resource. This prevents attackers from discovering valid resource IDs.

### Authorization Code Pattern

```python
# Backend dependency injection
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate user from JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401)

    return user

# Task endpoint with user isolation
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)

    # Return 404 for both "not found" AND "wrong user"
    if task is None or task.user_id != current_user.id:
        raise HTTPException(status_code=404)

    return task
```

---

## Protected Routes

### Route Classification

| Route Pattern | Protection | Description |
|---------------|------------|-------------|
| `/api/v1/auth/register` | Public | User registration |
| `/api/v1/auth/login` | Public | User authentication |
| `/api/v1/tasks` | Protected | List user's tasks |
| `/api/v1/tasks/:id` | Protected | Single task operations |

### Frontend Route Protection

| Route | Protection | Behavior |
|-------|------------|----------|
| `/login` | Public | Redirect to /dashboard if authenticated |
| `/signup` | Public | Redirect to /dashboard if authenticated |
| `/dashboard` | Protected | Redirect to /login if not authenticated |
| `/tasks/*` | Protected | Redirect to /login if not authenticated |

---

## Security Constraints

### Token Security

| Constraint | Enforcement | Level |
|------------|-------------|-------|
| No token in URL | Code review, linting | Application |
| No token in query params | Code review, linting | Application |
| httpOnly cookie storage | Better Auth config | Frontend |
| Secure flag in production | Better Auth config | Frontend |

### Transport Security

| Constraint | Environment | Enforcement |
|------------|-------------|-------------|
| HTTPS required | Production | Infrastructure |
| HTTP allowed | Development only | Configuration |

### Secret Management

| Constraint | Implementation |
|------------|----------------|
| Secrets never in code | Environment variables only |
| Secrets never committed | `.gitignore`, pre-commit hooks |
| Secrets rotatable | Config-driven, no hardcoding |

### Password Security

| Requirement | Implementation |
|-------------|----------------|
| Minimum length | 8 characters |
| Hashing algorithm | bcrypt |
| Salt | Auto-generated by bcrypt |
| No plaintext storage | Enforced by model layer |

---

## Error Responses

### Authentication Errors

| Scenario | Status | Response Body |
|----------|--------|---------------|
| No token provided | 401 | `{"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}` |
| Invalid token | 401 | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}}` |
| Expired token | 401 | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token"}}` |

### Authorization Errors

| Scenario | Status | Response Body |
|----------|--------|---------------|
| Resource not found | 404 | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |
| Wrong user's resource | 404 | `{"error": {"code": "NOT_FOUND", "message": "Resource not found"}}` |

**Note**: Both "not found" and "wrong user" return identical 404 responses to prevent enumeration attacks.

### Validation Errors

| Scenario | Status | Response Body |
|----------|--------|---------------|
| Invalid email format | 422 | `{"error": {"code": "VALIDATION_ERROR", "message": "Invalid email format"}}` |
| Password too short | 422 | `{"error": {"code": "VALIDATION_ERROR", "message": "Password must be at least 8 characters"}}` |
| Email already exists | 409 | `{"error": {"code": "CONFLICT", "message": "Email already registered"}}` |
| Invalid credentials | 401 | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid credentials"}}` |

---

## Phase II Limits

### Not Implemented in Phase II

| Feature | Status | Rationale |
|---------|--------|-----------|
| Refresh tokens | Excluded | Complexity; 7-day expiry sufficient |
| Role-based access (RBAC) | Excluded | Single role (user) sufficient |
| OAuth providers | Excluded | Email/password sufficient for MVP |
| Multi-factor auth (MFA) | Excluded | Out of scope |
| Password reset | Excluded | Out of scope for hackathon |
| Email verification | Excluded | Out of scope for hackathon |

### Future Considerations (Phase III+)

- Refresh token rotation for better security
- OAuth2 providers (Google, GitHub)
- API key authentication for AI agents
- Rate limiting on auth endpoints

---

## Functional Requirements

### Authentication Requirements

- **FR-AUTH-001**: System MUST allow users to register with email and password
- **FR-AUTH-002**: System MUST validate email format on registration
- **FR-AUTH-003**: System MUST enforce minimum password length of 8 characters
- **FR-AUTH-004**: System MUST hash passwords using bcrypt before storage
- **FR-AUTH-005**: System MUST issue JWT on successful login/registration
- **FR-AUTH-006**: System MUST set JWT expiration to 7 days

### Authorization Requirements

- **FR-AUTHZ-001**: System MUST validate JWT on every protected request
- **FR-AUTHZ-002**: System MUST reject requests without valid JWT with 401
- **FR-AUTHZ-003**: System MUST reject requests with expired JWT with 401
- **FR-AUTHZ-004**: System MUST return 404 when user accesses another user's resource
- **FR-AUTHZ-005**: System MUST extract user_id from JWT `sub` claim for all queries

### Session Requirements

- **FR-SESS-001**: System MUST store JWT in httpOnly cookie on frontend
- **FR-SESS-002**: System MUST clear session on logout
- **FR-SESS-003**: System MUST persist session across browser restarts (until expiry)

---

## Auth Acceptance Criteria

### Security Criteria

- [ ] **AC-AUTH-001**: Unauthorized requests (no token) receive 401
- [ ] **AC-AUTH-002**: Requests with invalid token receive 401
- [ ] **AC-AUTH-003**: Requests with expired token receive 401
- [ ] **AC-AUTH-004**: Users cannot access other users' tasks (returns 404)
- [ ] **AC-AUTH-005**: Login with wrong password returns generic "Invalid credentials"
- [ ] **AC-AUTH-006**: Login with non-existent email returns generic "Invalid credentials"

### Functional Criteria

- [ ] **AC-AUTH-007**: New users can register with valid email/password
- [ ] **AC-AUTH-008**: Registered users can log in and receive JWT
- [ ] **AC-AUTH-009**: Logged-in users can log out and lose access
- [ ] **AC-AUTH-010**: Session persists across browser restarts

### Data Criteria

- [ ] **AC-AUTH-011**: Passwords are never stored in plaintext
- [ ] **AC-AUTH-012**: Email addresses are unique in the system
- [ ] **AC-AUTH-013**: All task queries are scoped to authenticated user

### Traceability

- [ ] **AC-AUTH-014**: All authentication behavior traceable to this specification

---

## References

- @specs/architecture.md - System architecture
- @specs/api/rest-endpoints.md - API contract
- @.specify/memory/constitution.md - Project constitution (Section III: Multi-User Security)
