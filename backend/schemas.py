"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =============================================================================
# Auth Schemas (US5)
# =============================================================================


class UserCreate(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    """Schema for authentication responses (register/login)."""

    user: UserResponse
    token: str


# =============================================================================
# Task Schemas (US1-US4)
# =============================================================================


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)


class TaskUpdate(BaseModel):
    """Schema for full task update (PUT) - all fields required."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool


class TaskPatch(BaseModel):
    """Schema for partial task update (PATCH) - all fields optional."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task data in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
