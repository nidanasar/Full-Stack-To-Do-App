"""SQLModel definitions for User and Task entities."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey, Index, Text
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """User account for authentication and task ownership."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(Text, unique=True, nullable=False, index=True))
    hashed_password: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Task(SQLModel, table=True):
    """Task item belonging to a user."""

    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_user_completed", "user_id", "completed"),
        Index("idx_tasks_user_created", "user_id", "created_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    title: str = Field(sa_column=Column(Text, nullable=False))
    description: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
