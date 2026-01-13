---
description: Generate JWT tokens for authentication in FastAPI backend.
---

# Skill: JWT Generation

## Purpose
Create JWT access tokens after successful authentication. Complements `sp.jwt-auth.md` which handles validation.

## Stack Context
- **Backend**: FastAPI + python-jose
- **Frontend**: Better Auth (consumes tokens)
- **Secret**: Shared `BETTER_AUTH_SECRET` env var

## Dependencies

```toml
# pyproject.toml
[project.dependencies]
python-jose = { extras = ["cryptography"], version = "^3.3.0" }
```

## Implementation

### Token Configuration
```python
# utils/jwt.py
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import jwt

# Configuration
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

def create_access_token(
    user_id: UUID,
    email: str | None = None,
    expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User's UUID (stored in 'sub' claim)
        email: Optional email for convenience
        expires_delta: Custom expiration (default: 7 days)

    Returns:
        Encoded JWT string
    """
    if expires_delta is None:
        expires_delta = timedelta(days=JWT_EXPIRATION_DAYS)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),  # Subject: user identifier
        "iat": int(now.timestamp()),  # Issued at
        "exp": int(expire.timestamp()),  # Expiration
    }

    if email:
        payload["email"] = email

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

### Token Verification (Reference)
```python
# utils/jwt.py (continued)
from jose import JWTError

class TokenPayload:
    def __init__(self, sub: UUID, email: str | None = None):
        self.sub = sub
        self.email = email

def verify_token(token: str) -> TokenPayload:
    """
    Verify and decode a JWT token.

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return TokenPayload(
            sub=UUID(payload["sub"]),
            email=payload.get("email")
        )
    except JWTError:
        raise
```

### Usage in Auth Routes

#### Registration
```python
# routes/auth.py
from utils.jwt import create_access_token
from utils.security import hash_password

@router.post("/auth/register", status_code=201)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    # Check existing email
    existing = await get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(409, "Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        password=hash_password(user_data.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Generate token
    token = create_access_token(user.id, user.email)

    return {
        "user": {"id": str(user.id), "email": user.email},
        "token": token
    }
```

#### Login
```python
# routes/auth.py
from utils.security import verify_password

@router.post("/auth/login")
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    user = await get_user_by_email(session, credentials.email)

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    # Generate token
    token = create_access_token(user.id, user.email)

    return {
        "user": {"id": str(user.id), "email": user.email},
        "token": token
    }
```

## Token Payload Structure

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1699999999,
  "exp": 1700604799
}
```

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string (UUID) | User ID - primary identifier |
| `email` | string | User email (optional, for display) |
| `iat` | int | Issued at (Unix timestamp) |
| `exp` | int | Expiration (Unix timestamp) |

## Environment Variables

```bash
# .env
BETTER_AUTH_SECRET=your-256-bit-secret-key-minimum-32-characters
```

### Generating a Secure Secret
```bash
# Generate a secure random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Security Considerations

| Consideration | Implementation |
|---------------|----------------|
| Secret length | Minimum 256 bits (32 bytes) |
| Algorithm | HS256 (HMAC-SHA256) |
| Expiration | 7 days default (configurable) |
| Clock skew | python-jose handles automatically |
| Token refresh | Not implemented (frontend handles re-auth) |

## Response Format

Both register and login return the same structure:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Integration with Better Auth

Frontend receives token and stores it via Better Auth:
```typescript
// Frontend receives token from login/register response
const { user, token } = await response.json();

// Better Auth stores token in httpOnly cookie
// Subsequent requests include Authorization: Bearer <token>
```

## Testing

```python
# tests/test_jwt.py
from utils.jwt import create_access_token, verify_token
from uuid import uuid4

def test_create_and_verify_token():
    user_id = uuid4()
    email = "test@example.com"

    token = create_access_token(user_id, email)

    payload = verify_token(token)
    assert payload.sub == user_id
    assert payload.email == email

def test_expired_token():
    from datetime import timedelta

    user_id = uuid4()
    token = create_access_token(user_id, expires_delta=timedelta(seconds=-1))

    with pytest.raises(JWTError):
        verify_token(token)
```

## Checklist
- [ ] BETTER_AUTH_SECRET is at least 32 characters
- [ ] Secret is stored in .env, not hardcoded
- [ ] Token includes `sub`, `iat`, `exp` claims
- [ ] Expiration is set (default 7 days)
- [ ] Login and register both return `{user, token}`
- [ ] Email is optional in payload (for display only)
