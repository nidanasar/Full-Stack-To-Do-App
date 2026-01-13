---
description: Implement secure password hashing with bcrypt/passlib for FastAPI authentication.
---

# Skill: Password Hashing

## Purpose
Securely hash passwords on registration and verify them on login. Never store plaintext passwords.

## Stack Context
- **Backend**: FastAPI + Python
- **Library**: passlib with bcrypt backend
- **Security**: Industry-standard bcrypt with automatic salting

## Dependencies

```toml
# pyproject.toml
[project.dependencies]
passlib = { extras = ["bcrypt"], version = "^1.7.4" }
```

Or with pip:
```bash
pip install "passlib[bcrypt]"
```

## Implementation

### Password Context Setup
```python
# utils/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Work factor (higher = slower but more secure)
)

def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### Usage in Registration
```python
# routes/auth.py
from pydantic import BaseModel, EmailStr, Field
from utils.security import hash_password

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

@router.post("/auth/register", status_code=201)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    # Check if email exists
    existing = await get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(409, "Email already registered")

    # Hash password BEFORE storing
    hashed = hash_password(user_data.password)

    # Create user with hashed password
    user = User(
        email=user_data.email,
        password=hashed  # Never store plaintext!
    )
    session.add(user)
    await session.commit()

    # Generate token and return
    token = create_access_token(user.id)
    return {"user": {"id": str(user.id), "email": user.email}, "token": token}
```

### Usage in Login
```python
# routes/auth.py
from utils.security import verify_password

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/auth/login")
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    # Fetch user by email
    user = await get_user_by_email(session, credentials.email)

    # Verify password (handles None user gracefully)
    if not user or not verify_password(credentials.password, user.password):
        # Generic message prevents account enumeration
        raise HTTPException(401, "Invalid credentials")

    # Generate token and return
    token = create_access_token(user.id)
    return {"user": {"id": str(user.id), "email": user.email}, "token": token}
```

## User Model

```python
# models/user.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str  # Stores HASHED password only
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Security Best Practices

| Practice | Implementation |
|----------|----------------|
| Never store plaintext | Always use `hash_password()` before saving |
| Use bcrypt | Built-in salting, configurable work factor |
| Work factor 12+ | Balance security vs. performance |
| Generic login errors | "Invalid credentials" for all failures |
| Timing-safe comparison | passlib handles this automatically |

## Common Mistakes

```python
# WRONG: Storing plaintext
user.password = credentials.password

# CORRECT: Hash first
user.password = hash_password(credentials.password)

# WRONG: Revealing which field is wrong
if not user:
    raise HTTPException(401, "Email not found")
if not verify_password(...):
    raise HTTPException(401, "Wrong password")

# CORRECT: Generic error
if not user or not verify_password(...):
    raise HTTPException(401, "Invalid credentials")
```

## Testing

```python
# tests/test_password.py
from utils.security import hash_password, verify_password

def test_password_hashing():
    password = "SecurePass123"
    hashed = hash_password(password)

    # Hash is different from original
    assert hashed != password

    # Verification works
    assert verify_password(password, hashed) is True

    # Wrong password fails
    assert verify_password("WrongPass", hashed) is False

def test_hash_is_unique():
    """Same password produces different hashes (due to salt)."""
    password = "SamePassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2  # Different salts
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
```

## Checklist
- [ ] passlib[bcrypt] installed
- [ ] Password hashed before database insert
- [ ] Login uses `verify_password()` not direct comparison
- [ ] Generic error message on login failure
- [ ] Work factor is 12 or higher
- [ ] User model stores hashed password field
